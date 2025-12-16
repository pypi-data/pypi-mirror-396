import logging

from datetime import datetime
from ..engines.base_engine import BaseEngine
from typing import Any, Callable, Dict, List, Tuple, Type, Union
from hmd_meta_types import Noun, Relationship, Entity


logger = logging.getLogger(f"HMD.{__name__}")


class AuditContext:
    def __init__(
        self,
        callback: Callable,
        audit_record_engine: BaseEngine,
        audit_record_class: Type[Noun],
        audit_relationship_class: Type[Relationship],
        event_type: str,
        event_subtype: str,
        action: str,
    ) -> None:
        self.__storage = audit_record_engine
        self.audit_record_data_cb = callback
        self.audit_record_class = audit_record_class
        self.audit_record_rel_class = audit_relationship_class

        self.event_type = event_type
        self.event_subtype = event_subtype
        self.action = action

        self.__entities = []

    def add_entity(self, entity: Union[Type[Entity], str]):
        self.__entities.append(entity)

    def add_entities(self, entities: List[Union[Type[Entity], str]]):
        self.__entities.extend(entities)

    def __enter__(self):
        self.start = datetime.now()
        self.end = datetime.now()

        self.__storage.begin_transaction()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = datetime.now()

        outcome = "success" if exc_type is None else "error"
        outcome_description = f"{exc_val}" if exc_val is not None else ""

        try:
            audit_record = self.audit_record_class(
                **self.audit_record_data_cb(
                    self.event_type,
                    self.event_subtype,
                    self.action,
                    self.start,
                    self.end,
                    outcome,
                    outcome_description,
                )
            )
            audit_record = self.__storage.put_entity(audit_record)

            for entity in self.__entities:
                identifier = entity
                if isinstance(entity, Entity):
                    identifier = entity.identifier
                rel = self.audit_record_rel_class(
                    ref_from=audit_record.identifier, ref_to=identifier
                )
                self.__storage.put_entity(rel)

            self.__storage.commit_transaction()
        except Exception as e:
            logger.error("Error storing audit records.")
            logger.error(e)

        # Re-raise exception to bubble up to calling service
        if exc_val is not None:
            raise exc_val


class AuditedEngine(BaseEngine):
    """Wraps calls to supplied BaseEngine with AuditContext to track actions on Entities.

    Args:
        engine (BaseEngine): storage engine derived from BaseEngine to audit
        engine_type (str): type of storage engine being wrapped, e.g. postgres
        audit_record_engine (BaseEngine): storage engine used to save audit records
        audit_record_class (Type[Noun]): HMD Noun class used to create audit records
        audit_relationship_class (Type[Relationship]): HMD Relationship class used to create audit record relationships
        prepare_audit_data (Callable): function to prepare dictionary of data for audit_record_class
        exclude (List[str]): list of class names to exclude for auditing
    """

    def __init__(
        self,
        engine: BaseEngine,
        engine_type: str,
        audit_record_engine: BaseEngine,
        audit_record_class: Type[Noun],
        audit_relationship_class: Type[Relationship],
        prepare_audit_data: Callable,
        exclude: List[str] = [],
    ) -> None:
        super().__init__()
        self.__engine = engine
        self.__engine_type = engine_type
        self.__storage = audit_record_engine
        self.__prepare_audit_data = prepare_audit_data
        self.__audit_record_class = audit_record_class
        self.__audit_relationship_class = audit_relationship_class
        self.__exclude = exclude

    @property
    def base_engine(self):
        return self.__engine

    def get_entity(self, entity_def: Type[Entity], id_: str) -> Entity:
        if entity_def.get_namespace_name() in self.__exclude:
            return self.__engine.get_entity(entity_def, id_)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="read",
        ) as audit_record:
            result = self.__engine.get_entity(entity_def, id_)
            audit_record.add_entity(result)
            return result

    def get_entities(self, entity_def: Type[Entity], ids_: List[str]) -> List[Entity]:
        if entity_def.get_namespace_name() in self.__exclude:
            return self.__engine.get_entities(entity_def, ids_)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="read",
        ) as audit_record:
            result = self.__engine.get_entities(entity_def, ids_)
            audit_record.add_entities(result)
            return result

    def search_entities(
        self, entity_def: Type[Entity], search_filter: Dict[str, Any]
    ) -> List[Entity]:
        if entity_def.get_namespace_name() in self.__exclude:
            return self.__engine.search_entities(entity_def, search_filter)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="search",
        ) as audit_record:
            result = self.__engine.search_entities(entity_def, search_filter)
            audit_record.add_entities(result)
            return result

    def list_entities(
        self, class_cache: Dict[str, Type[Entity]], id_: str = None
    ) -> List[Noun]:
        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="read",
        ) as audit_record:
            result = self.__engine.list_entities(class_cache, id_)
            audit_record.add_entities(result)
            return result

    def put_entity(self, entity: Entity) -> Entity:
        if entity.get_namespace_name() in self.__exclude:
            return self.__engine.put_entity(entity)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="upsert",
        ) as audit_record:
            result = self.__engine.put_entity(entity)
            audit_record.add_entity(result)
            return result

    def delete_entity(self, entity_def: Type[Entity], entity_id: str) -> None:
        if entity_def.get_namespace_name() in self.__exclude:
            return self.__engine.delete_entity(entity_def, entity_id)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="delete",
        ) as audit_record:
            result = self.__engine.delete_entity(entity_def, entity_id)
            audit_record.add_entity(entity_id)
            return result

    def get_relationships_from(
        self, relationship_def: Type[Relationship], id_: str
    ) -> List[Relationship]:
        if relationship_def.get_namespace_name() in self.__exclude:
            return self.__engine.get_relationships_from(relationship_def, id_)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="read",
        ) as audit_record:
            result = self.__engine.get_relationships_from(relationship_def, id_)
            audit_record.add_entities(result)
            return result

    def get_relationships_to(
        self, relationship_def: Type[Relationship], id_: str
    ) -> List[Relationship]:
        if relationship_def.get_namespace_name() in self.__exclude:
            return self.__engine.get_relationships_to(relationship_def, id_)

        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="read",
        ) as audit_record:
            result = self.__engine.get_relationships_to(relationship_def, id_)
            audit_record.add_entities(result)
            return result

    def upsert_entities(self, entities):
        with AuditContext(
            callback=self.__prepare_audit_data,
            audit_record_engine=self.__storage,
            audit_record_class=self.__audit_record_class,
            audit_relationship_class=self.__audit_relationship_class,
            event_type="database access",
            event_subtype=self.__engine_type,
            action="upsert",
        ) as audit_record:
            result = self.__engine.upsert_entities(entities)
            audit_record.add_entities(entities.get("nouns", []))
            audit_record.add_entities(entities.get("relationships", []))
            return result

    def native_query_nouns(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        return self.__engine.native_query_nouns(query, data)

    def native_query_relationships(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        return self.__engine.native_query_relationships(query, data)

    def begin_transaction(self) -> None:
        return self.__engine.begin_transaction()

    def commit_transaction(self) -> None:
        return self.__engine.commit_transaction()

    def rollback_transaction(self) -> None:
        return self.__engine.rollback_transaction()


class EngineAuditor:
    """Class used to wrap BaseEngine classes for auditing."""

    def __init__(
        self,
        audit_engine: BaseEngine,
        audit_record_class: Type[Noun],
        audit_relationship_class: Type[Relationship],
        prepare_audit_data: Callable,
    ) -> None:
        self.audit_engine = audit_engine
        self.audit_record_class = audit_record_class
        self.audit_relationship_class = audit_relationship_class
        self.prepare_audit_data = prepare_audit_data

    def audit(
        self, engine: BaseEngine, engine_type: str, exclude: List[str] = []
    ) -> AuditedEngine:
        """Wraps BaseEngine with audit capabilities"""

        if isinstance(engine, AuditedEngine):
            engine = engine.base_engine

        return AuditedEngine(
            engine=engine,
            engine_type=engine_type,
            audit_record_engine=self.audit_engine,
            prepare_audit_data=self.prepare_audit_data,
            audit_record_class=self.audit_record_class,
            audit_relationship_class=self.audit_relationship_class,
            exclude=exclude,
        )
