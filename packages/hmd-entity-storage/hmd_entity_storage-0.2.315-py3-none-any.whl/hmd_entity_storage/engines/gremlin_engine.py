import datetime
import logging
from functools import reduce
import os
from typing import Type, Dict, List, Any, Tuple

import backoff
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver.aiohttp.transport import AiohttpTransport
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import P
from gremlin_python.process.traversal import T, Cardinality
from gremlin_python.statics import long
from gremlin_python.driver.serializer import GraphSONSerializersV3d0
from hmd_meta_types import Noun, Relationship, Entity

from .base_engine import BaseEngine, gen_new_key, get_env_var

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

CREATED_PROPERTY = "_created"
UPDATED_PROPERTY = "_updated"
INSTANCE_NAME_PROPERTY = "_instance_name"
MANAGED_PROPERTIES = [T.id, T.label, "__id", INSTANCE_NAME_PROPERTY]
TRAVERSAL_STRATEGIES = [
    SubgraphStrategy(vertices=__.hasNot("is_deleted"), edges=__.hasNot("is_deleted")),
]
operator_map = {">=": P.gte, ">": P.gt, "<=": P.lte, "<": P.lt, "=": P.eq, "!=": P.neq}


def in_notebook():
    try:
        from IPython import get_ipython

        return "IPKernelApp" in get_ipython().config
    except:
        return False


def add_properties(g, properties: Dict[str, Any], isSingle=True):
    for k, v in properties.items():
        if isinstance(v, int) and v >= 2**31:
            v = long(v)
        if isSingle:
            g = g.property(Cardinality.single, k, v)
        else:
            g = g.property(k, v)

    return g


def remove_managed_properties_and_delist(a_dict: Dict):
    for key in MANAGED_PROPERTIES:
        if key in a_dict:
            del a_dict[key]
    for key in a_dict:
        if isinstance(a_dict[key], list):
            a_dict[key] = a_dict[key][0]
    return a_dict


def backoff_initialize_connection(data: Dict):
    """A method used by the backoff decorator to reset the connection"""
    engine: GremlinEngine
    engine = data["args"][0]
    engine.initialize_connection()


class GremlinEngine(BaseEngine):
    def __init__(
        self,
        host: str,
        user: str = "hmdroot",
        password: str = "",
        port: int = 8182,
        protocol: str = "wss",
        with_strategies: bool = True,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.protocol = protocol
        # with_strategies config option to enable required TraversalStrategies in Python if True
        # or init traversal without if False, and assume they are added on the server.
        self.with_strategies = with_strategies
        self.initialize_connection()

    def initialize_connection(self):
        transport_factory = None

        if in_notebook():
            transport_factory = lambda: AiohttpTransport(call_from_event_loop=True)

        remoteConn = DriverRemoteConnection(
            f"{self.protocol}://{self.host}:{self.port}/gremlin",
            "g",
            transport_factory=transport_factory,
        )
        self._g = traversal().withRemote(remoteConn)

    def _get_g(self):
        """Return the Gremlin graph traversal.
        If self.with_strategies is True, then we add the necessary SubgraphStrategy to filter out is_deleted=True vertices and edges to the Python client traversal
        If self.with_strategies is False, we return the bare traversal and assume the Gremlin Server graph was configured with the strategy.
        """
        if not self.with_strategies:
            # Return bare graph traversal without SubgraphStrategy
            return self._g

        # Add SubgraphStrategy to filter out deleted records
        return self._g.withStrategies(*TRAVERSAL_STRATEGIES)

    def get_entity(self, entity_def: Type[Entity], id_: str) -> Entity:
        if issubclass(entity_def, Noun):
            return self.get_noun(entity_def, id_)
        else:
            return self.get_relationship(entity_def, id_)

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def get_entities(self, entity_def: Type[Entity], ids_: List[str]) -> List[Entity]:
        # todo: one query
        result = []
        for id_ in ids_:
            if issubclass(entity_def, Noun):
                entity = self.get_noun(entity_def, id_)
                if not entity:
                    raise Exception(
                        f"Entity of type {entity_def.get_namespace_name()} with id {id_} not found."
                    )
                result.append(entity)
            else:
                entity = self.get_relationship(entity_def, id_)
                if entity:
                    result.append(entity)
        return result

    def _make_noun(self, noun_def: Type[Noun], data: Dict):
        data["identifier"] = data[T.id]

        if not isinstance(data["identifier"], str):
            data["identifier"] = data["__id"]
        return Entity.deserialize(noun_def, remove_managed_properties_and_delist(data))

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def get_noun(self, entity_def: Type[Noun], id_: str) -> Noun:
        data = self._get_g().V(id_).valueMap(True).toList()
        if data:
            return self._make_noun(entity_def, data[0])
        else:
            return None

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def get_relationship(self, entity_def: Type[Relationship], id_: str) -> Noun:
        data = (
            self._get_g()
            .E(id_)
            .as_("rel")
            .inV()
            .as_("to")
            .select("rel")
            .outV()
            .as_("from")
            .select("from", "rel", "to")
            .by(__.valueMap(True))
            .toList()
        )
        if data:
            return self._make_relationship(entity_def, data[0])
        else:
            return None

    def search_entities(
        self, entity_def: Type[Entity], search_filter: Dict[str, Any] = dict()
    ) -> List[Entity]:
        if issubclass(entity_def, Noun):
            return self.search_noun(entity_def, search_filter)
        elif issubclass(entity_def, Relationship):
            return self.search_relationship(entity_def, search_filter)
        else:
            raise NotImplementedError()

    def _build_search_criteria(self, search_filter: Dict):
        if "and" in search_filter:
            return __.and_(
                *[
                    self._build_search_criteria(sub_criteria)
                    for sub_criteria in search_filter["and"]
                ]
            )
        elif "or" in search_filter:
            return __.or_(
                *[
                    self._build_search_criteria(sub_criteria)
                    for sub_criteria in search_filter["or"]
                ]
            )
        else:
            target = (
                search_filter["value"]
                if "value" in search_filter
                else __.values(search_filter["attribute_target"])
            )
            return __.values(search_filter["attribute"]).is_(
                operator_map[search_filter["operator"]](target)
            )

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def search_noun(
        self, entity_def: Type[Noun], search_filter: Dict[str, Any] = dict()
    ) -> List[Noun]:
        self._validate_search_criteria(entity_def.entity_definition(), search_filter)
        results = self._get_g().V().hasLabel(entity_def.get_namespace_name())
        if len(search_filter) > 0:
            results = results.where(self._build_search_criteria(search_filter))
        results = results.valueMap(True).toList()
        return [self._make_noun(entity_def, data) for data in results]

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def search_relationship(
        self, entity_def: Type[Relationship], search_filter: Dict[str, Any] = dict()
    ) -> List[Noun]:
        self._validate_search_criteria(entity_def.entity_definition(), search_filter)
        results = self._get_g().E().hasLabel(entity_def.get_namespace_name())
        if len(search_filter) > 0:
            results = results.where(self._build_search_criteria(search_filter))
        results = (
            results.as_("rel")
            .inV()
            .as_("to")
            .select("rel")
            .outV()
            .as_("from")
            .select("from", "to", "rel")
            .by(__.valueMap(True))
            .fold()
            .next()
        )
        return [self._make_relationship(entity_def, data) for data in results]

    def put_entity(self, entity: Type[Entity]):
        if isinstance(entity, Noun):
            return self.put_noun(entity)
        else:
            return self.put_relationship(entity)

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def put_noun(self, entity: Noun) -> Noun:
        entity._updated = datetime.datetime.now(datetime.timezone.utc)
        if not entity.identifier:
            entity._created = entity._updated
        serialized = entity.serialize()
        if not "identifier" in serialized:
            id_ = gen_new_key()
            entity.identifier = id_
        else:
            id_ = serialized["identifier"]
            del serialized["identifier"]

        upsert = (
            self._get_g()
            .V(id_)
            .fold()
            .coalesce(
                __.unfold(),
                __.addV(entity.get_namespace_name())
                .property(T.id, id_)
                .property(
                    Cardinality.single,
                    INSTANCE_NAME_PROPERTY,
                    get_env_var("HMD_INSTANCE_NAME"),
                ),
            )
        )
        current_properties = (
            add_properties(upsert, serialized, isSingle=True).valueMap().next()
        )

        # See if the update removed any properties...
        remove_managed_properties_and_delist(current_properties)

        if any(property not in serialized for property in current_properties):
            self._drop_properties(
                self._get_g().V(id_),
                [
                    property
                    for property in current_properties
                    if property not in serialized
                ],
            )

        return entity

    def list_entities(
        self, class_cache: Dict[str, Type[Entity]], id_: int = None
    ) -> List[Noun]:
        raise NotImplementedError()

    def _drop_properties(self, dropper, props_to_drop: List[str]):
        def drop_property(g, prop):
            return g.properties(prop).drop()

        reduce(drop_property, [dropper] + props_to_drop).iterate()

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def put_relationship(self, relationship: Relationship) -> Relationship:
        assert isinstance(relationship.ref_to, str) or hasattr(
            relationship.ref_to, "identifier"
        ), "relationship.ref_to has no identifier property"
        ref_to_id = (
            relationship.ref_to
            if isinstance(relationship.ref_to, str)
            else relationship.ref_to.identifier
        )
        assert isinstance(relationship.ref_from, str) or hasattr(
            relationship.ref_from, "identifier"
        ), "relationship.ref_from has no identifier property"
        ref_from_id = (
            relationship.ref_from
            if isinstance(relationship.ref_from, str)
            else relationship.ref_from.identifier
        )

        relationship._updated = datetime.datetime.now(datetime.timezone.utc)
        if not relationship.identifier:
            relationship._created = relationship._updated
        serialized = relationship.serialize()
        if not "identifier" in serialized:
            id_ = gen_new_key()
            relationship.identifier = id_
        else:
            id_ = serialized["identifier"]
            del serialized["identifier"]

        del serialized["ref_from"]
        del serialized["ref_to"]

        g = self._get_g()

        if not "identifier" in serialized:
            # Remove SubGraphStrategy on inserting new edge for compatibility with Neptune 1.2
            g = g.withoutStrategies(*TRAVERSAL_STRATEGIES)
        upsert = (
            g.E(id_)
            .fold()
            .coalesce(
                __.unfold(),
                __.addE(relationship.get_namespace_name())
                .property(T.id, id_)
                .property(
                    Cardinality.single,
                    INSTANCE_NAME_PROPERTY,
                    get_env_var("HMD_INSTANCE_NAME"),
                )
                .to(__.V(ref_to_id))
                .from_(__.V(ref_from_id)),
            )
        )
        current_properties = (
            add_properties(upsert, serialized, isSingle=False).valueMap().next()
        )

        # See if the update removed any properties...
        remove_managed_properties_and_delist(current_properties)

        if any(property not in serialized for property in current_properties):
            self._drop_properties(
                self._get_g().E(id_),
                [
                    property
                    for property in current_properties
                    if property not in serialized
                ],
            )

        return relationship

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def delete_entity(self, entity_def: Type[Entity], id_: int) -> None:
        if issubclass(entity_def, Relationship):
            self._get_g().E(id_).property("is_deleted", True).iterate()
        else:
            self._get_g().V(id_).property(
                Cardinality.single, "is_deleted", True
            ).bothE().property("is_deleted", True).iterate()

    def _make_relationship(self, relationship_def, data: Dict):
        from_dict = data["from"]
        from_dict["identifier"] = from_dict[T.id]
        if not isinstance(from_dict["identifier"], str):
            from_dict["identifier"] = from_dict["__id"]
        remove_managed_properties_and_delist(from_dict)

        to_dict = data["to"]
        to_dict["identifier"] = to_dict[T.id]
        if not isinstance(to_dict["identifier"], str):
            to_dict["identifier"] = to_dict["__id"]
        remove_managed_properties_and_delist(to_dict)

        rel_dict = data["rel"]
        rel_dict["identifier"] = rel_dict[T.id]
        if not isinstance(rel_dict["identifier"], str):
            rel_dict["identifier"] = rel_dict["__id"]
        remove_managed_properties_and_delist(rel_dict)

        rel_dict["ref_from"] = from_dict["identifier"]
        rel_dict["ref_to"] = to_dict["identifier"]
        return Entity.deserialize(relationship_def, rel_dict)

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def get_relationships_from(
        self, relationship_def: Relationship, id_: int
    ) -> List[Relationship]:
        values = (
            self._get_g()
            .V(id_)
            .as_("from")
            .outE(relationship_def.get_namespace_name())
            .as_("rel")
            .inV()
            .as_("to")
            .select("from", "rel", "to")
            .by(__.valueMap(True))
            .fold()
            .next()
        )
        result = []
        for value in values:
            result.append(self._make_relationship(relationship_def, value))

        return result

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def get_relationships_to(
        self, relationship_def: Relationship, id_: int
    ) -> Relationship:
        values = (
            self._get_g()
            .V(id_)
            .as_("to")
            .inE(relationship_def.get_namespace_name())
            .as_("rel")
            .outV()
            .as_("from")
            .select("from", "rel", "to")
            .by(__.valueMap(True))
            .fold()
            .next()
        )
        result = []
        for value in values:
            result.append(self._make_relationship(relationship_def, value))

        return result

    @backoff.on_exception(
        backoff.constant,
        (Exception,),
        max_tries=2,
        on_backoff=backoff_initialize_connection,
        interval=1,
    )
    def upsert_entities(self, entities):
        nouns = entities.get("nouns", [])
        relationships = entities.get("relationships", [])

        def upsert_noun(g, noun):
            serialized = noun.serialize()
            if not "identifier" in serialized:
                id_ = gen_new_key()
                noun.identifier = id_
            else:
                id_ = serialized["identifier"]
                del serialized["identifier"]

            traversal = (
                g.V(id_)
                .fold()
                .coalesce(
                    __.unfold(),
                    __.addV(noun.get_namespace_name())
                    .property(T.id, id_)
                    .property(
                        Cardinality.single,
                        INSTANCE_NAME_PROPERTY,
                        get_env_var("HMD_INSTANCE_NAME"),
                    ),
                )
            )
            traversal = add_properties(traversal, serialized, isSingle=True)
            return id_, traversal

        def upsert_relationship(g, relationship):
            assert isinstance(relationship.ref_to, str) or hasattr(
                relationship.ref_to, "identifier"
            ), "relationship.ref_to has no identifier property"
            ref_to_id = (
                relationship.ref_to
                if isinstance(relationship.ref_to, str)
                else relationship.ref_to.identifier
            )
            assert isinstance(relationship.ref_from, str) or hasattr(
                relationship.ref_from, "identifier"
            ), "relationship.ref_from has no identifier property"
            ref_from_id = (
                relationship.ref_from
                if isinstance(relationship.ref_from, str)
                else relationship.ref_from.identifier
            )

            serialized = relationship.serialize()
            if not "identifier" in serialized:
                id_ = gen_new_key()
                relationship.identifier = id_
            else:
                id_ = serialized["identifier"]
                del serialized["identifier"]

            del serialized["ref_from"]
            del serialized["ref_to"]

            # Cannot chain g.E() in Neptune, so we start from the from V and traverse from there.
            traversal = (
                g.V(ref_from_id)
                .outE(relationship.get_namespace_name())
                .hasId(id_)
                .fold()
                .coalesce(
                    __.unfold(),
                    __.addE(relationship.get_namespace_name())
                    .property(T.id, id_)
                    .property(
                        Cardinality.single,
                        INSTANCE_NAME_PROPERTY,
                        get_env_var("HMD_INSTANCE_NAME"),
                    )
                    .to(__.V(ref_to_id))
                    .from_(__.V(ref_from_id)),
                )
            )
            traversal = add_properties(traversal, serialized, isSingle=False)
            return id_, traversal

        noun_traversal = self._get_g()
        noun_ids = []
        for noun in nouns:
            id_, traversal = upsert_noun(noun_traversal, noun)
            noun_traversal = traversal
            noun_ids.append(id_)
            noun.identifier = id_
        if len(nouns) > 0:
            noun_traversal = noun_traversal.iterate()
        # Fetch the current properties of nouns to see if any properties were removed
        current_nouns = {}
        for id_ in noun_ids:
            current_noun_properties = self._get_g().V(id_).valueMap().next()
            remove_managed_properties_and_delist(current_noun_properties)
            current_nouns[id_] = current_noun_properties

        for i, noun in enumerate(nouns):
            current_noun_properties = current_nouns.get(noun_ids[i], [])
            # If any property was removed, drop it
            if any(
                property not in noun.serialize()
                for property in current_noun_properties.get(noun_ids[i], [])
            ):
                self._drop_properties(
                    self._get_g().V(noun_ids[i]),
                    [
                        property
                        for property in current_noun_properties.get(noun_ids[i], [])
                        if property not in noun.serialize()
                    ],
                )

        relationship_traversal = self._get_g().withoutStrategies(*TRAVERSAL_STRATEGIES)
        relationship_ids = []
        for relationship in relationships:
            id_, traversal = upsert_relationship(relationship_traversal, relationship)
            relationship_traversal = traversal
            relationship_ids.append(id_)
            relationship.identifier = id_
        if len(relationships) > 0:
            relationship_traversal = relationship_traversal.iterate()

        # Fetch the current properties of relationships to see if any properties were removed
        current_relationships = {}
        for id_ in relationship_ids:
            current_relationship_properties = self._get_g().E(id_).valueMap().next()
            remove_managed_properties_and_delist(current_relationship_properties)
            current_relationships[id_] = current_relationship_properties
        for i, relationship in enumerate(relationships):
            current_properties = current_relationships.get(relationship.identifier, [])
            if any(
                property not in relationship.serialize()
                for property in current_properties
            ):
                self._drop_properties(
                    self._get_g().E(relationship.identifier),
                    [
                        property
                        for property in current_properties
                        if property not in relationship.serialize()
                    ],
                )

        return {"nouns": nouns, "relationships": relationships}

    def native_query_nouns(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    def native_query_relationships(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    def begin_transaction(self) -> None:
        pass

    def commit_transaction(self) -> None:
        pass

    def rollback_transaction(self) -> None:
        pass
