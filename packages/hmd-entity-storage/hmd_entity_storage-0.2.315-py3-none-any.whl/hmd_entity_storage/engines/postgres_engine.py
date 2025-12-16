import json
import logging
import os
import datetime
import zoneinfo
from time import sleep
from typing import Type, Tuple, Dict, List, Any, Optional
from urllib.parse import quote

import psycopg2
import psycopg2.extras
from alembic import command
from alembic.config import Config
from hmd_meta_types import Noun, Relationship, Entity
from psycopg2 import sql
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_READ_COMMITTED,
)

from hmd_cli_tools import cd
from hmd_schema_loader import DefaultLoader
from .base_engine import BaseEngine, gen_new_key

logger = logging.getLogger(f"HMD.{__name__}")


class PostgresEngine(BaseEngine):
    _noun_select = sql.SQL(
        "SELECT {id}, {content}, {created_at}, {updated_at} FROM {table} WHERE {is_deleted} = FALSE AND {name} = {def_name}"
    ).format(
        id=sql.Identifier("id"),
        content=sql.Identifier("content"),
        is_deleted=sql.Identifier("is_deleted"),
        name=sql.Identifier("name"),
        created_at=sql.Identifier("created_at"),
        updated_at=sql.Identifier("updated_at"),
        def_name=sql.Placeholder("def_name"),
        table=sql.Identifier("entity"),
    )
    _relationship_sql = sql.SQL(
        """
            SELECT r.{id}, r.{name}, r.{content}, r.{from_id}, r.{to_id}, {created_at}, {updated_at}
            FROM {table} r
            WHERE r.{is_deleted} = FALSE
        """
    ).format(
        id=sql.Identifier("id"),
        content=sql.Identifier("content"),
        is_deleted=sql.Identifier("is_deleted"),
        created_at=sql.Identifier("created_at"),
        updated_at=sql.Identifier("updated_at"),
        name=sql.Identifier("name"),
        from_id=sql.Identifier("from_id"),
        to_id=sql.Identifier("to_id"),
        table=sql.Identifier("relationship"),
    )
    timestamp_field_map = {"_updated": "updated_at", "_created": "created_at"}

    def __init__(
        self,
        host: str,
        user: str = "hmdroot",
        password: str = "",
        db_name: str = "hmd_entities",
    ):
        if host.startswith("/"):
            count = 0
            while count < 3:
                if os.path.exists(host):
                    print(f"Found socket {host}")
                    os.listdir(host)
                    break
                print("Waiting for socket...")
                sleep(3)
                count += 1

        self.__conn = psycopg2.connect(
            f"dbname={db_name} host={host} user={user} password={password}",
            cursor_factory=psycopg2.extras.DictCursor,
        )
        self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.debug(
            os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
        )
        if os.path.exists(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "../alembic/alembic.ini"
            )
        ):
            logger.debug(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "../alembic/alembic.ini",
                )
            )

            with cd(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../alembic/")
            ):
                alembic_cfg = Config()
                alembic_cfg.set_main_option("script_location", ".")
                if host.startswith("/"):
                    alembic_cfg.set_main_option(
                        "sqlalchemy.url",
                        f"postgresql://{user}:{quote(password).replace('%', '%%')}@/{db_name}?host={host}",
                    )
                else:
                    alembic_cfg.set_main_option(
                        "sqlalchemy.url",
                        f"postgresql://{user}:{quote(password).replace('%', '%%')}@{host}/{db_name}",
                    )
                command.upgrade(alembic_cfg, "head")

        if os.path.exists("/app/alembic"):
            logger.info("Running custom revisions...")
            with cd("/app/alembic"):
                alembic_cfg = Config()
                alembic_cfg.set_main_option("script_location", ".")
                alembic_cfg.set_main_option("version_table", "alembic_version_app")
                if host.startswith("/"):
                    alembic_cfg.set_main_option(
                        "sqlalchemy.url",
                        f"postgresql://{user}:{quote(password).replace('%', '%%')}@/{db_name}?host={host}",
                    )
                else:
                    alembic_cfg.set_main_option(
                        "sqlalchemy.url",
                        f"postgresql://{user}:{quote(password).replace('%', '%%')}@{host}/{db_name}",
                    )
                command.upgrade(alembic_cfg, "head")

    def get_cursor(self):
        return self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def get_entity(self, entity_def: Type[Entity], id_: str) -> Entity:
        if issubclass(entity_def, Noun):
            return self.get_noun(entity_def, id_)
        else:
            raise NotImplementedError()

    def get_entities(self, entity_def: Type[Entity], ids_: List[str]) -> List[Entity]:
        if issubclass(entity_def, Noun):
            return self.get_nouns(entity_def, ids_)
        else:
            raise NotImplementedError()

    def get_noun(self, entity_def: Type[Noun], id: str) -> Optional[Noun]:
        get_sql = self._noun_select + sql.SQL(" AND {id} = {def_id}").format(
            id=sql.Identifier("id"), def_id=sql.Placeholder("id")
        )

        with self.__conn.cursor() as cursor:
            cursor.execute(
                get_sql, {"id": id, "def_name": entity_def.get_namespace_name()}
            )
            results = cursor.fetchall()

            if len(results) > 0:
                content = results[0]["content"]
                return Entity.deserialize(
                    entity_def,
                    {
                        **{
                            "identifier": results[0]["id"],
                            "_updated": (
                                results[0]["updated_at"]
                                .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                .isoformat()
                                if results[0]["updated_at"]
                                else results[0]["updated_at"]
                            ),
                            "_created": (
                                results[0]["created_at"]
                                .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                .isoformat()
                                if results[0]["created_at"]
                                else results[0]["created_at"]
                            ),
                        },
                        **content,
                    },
                )
            return None

    def get_nouns(self, entity_def: Type[Noun], ids_: List[str]) -> List[Noun]:
        get_sql = self._noun_select + sql.SQL(" AND {id} in ({def_ids})").format(
            id=sql.Identifier("id"), def_ids=sql.SQL(",").join(map(sql.Literal, ids_))
        )

        with self.__conn.cursor() as cursor:
            cursor.execute(
                get_sql, {"ids": ids_, "def_name": entity_def.get_namespace_name()}
            )
            results = cursor.fetchall()

            value = []
            if len(results) > 0:
                for result in results:
                    content = result["content"]
                    value.append(
                        Entity.deserialize(
                            entity_def,
                            {
                                **{
                                    "identifier": result["id"],
                                    "_updated": (
                                        result["updated_at"].isoformat()
                                        if result["updated_at"]
                                        else result["updated_at"]
                                    ),
                                    "_created": (
                                        result["created_at"].isoformat()
                                        if result["created_at"]
                                        else result["created_at"]
                                    ),
                                },
                                **content,
                            },
                        )
                    )
            missing = [val.identifier for val in value if val.identifier not in ids_]
            if missing:
                raise Exception(
                    f"Entity of type {entity_def.get_namespace_name()} with id {missing[0]} not found."
                )

            return value

    def search_entities(
        self, entity_def: Type[Entity], search_filter: Dict[str, Any] = dict()
    ) -> List[Entity]:
        if issubclass(entity_def, Noun):
            return self.search_noun(entity_def, search_filter)
        elif issubclass(entity_def, Relationship):
            return self.search_relationships(entity_def, search_filter)
        else:
            raise NotImplementedError()

    def build_where_clause(self, condition: Dict[str, Any]) -> psycopg2.sql.Composed:
        if "and" in condition:
            sqls = []
            for sub_condition in condition["and"]:
                sub_sql = self.build_where_clause(sub_condition)
                sqls.append(sub_sql)
            return sql.SQL("({})").format(sql.SQL(" AND ").join(sqls))
        elif "or" in condition:
            sqls = []
            for sub_condition in condition["or"]:
                sub_sql = self.build_where_clause(sub_condition)
                sqls.append(sub_sql)
            return sql.SQL("({})").format(sql.SQL(" OR ").join(sqls))
        else:
            if condition["attribute"] in self.timestamp_field_map:
                op1 = sql.Identifier(self.timestamp_field_map[condition["attribute"]])
            else:
                op1 = sql.SQL("({content} ->> {attribute})").format(
                    content=sql.Identifier("content"),
                    attribute=sql.Literal(condition["attribute"]),
                )

            if "attribute_target" in condition:
                if condition["attribute_target"] in self.timestamp_field_map:
                    op2 = sql.Identifier(
                        self.timestamp_field_map[condition["attribute_target"]]
                    )
                else:
                    op2 = sql.SQL("({content} ->> {attribute})").format(
                        content=sql.Identifier("content"),
                        attribute=sql.Literal(condition["attribute_target"]),
                    )
            else:
                op2 = sql.Literal(condition["value"])

            where_sql = sql.SQL("({op1} {operator} {op2})").format(
                op1=op1, operator=sql.SQL(condition["operator"]), op2=op2
            )
            return where_sql

    def search_noun(self, entity_def: Type[Noun], search_filter=None) -> List[Noun]:
        if search_filter is None:
            search_filter = dict()
        self._validate_search_criteria(entity_def.entity_definition(), search_filter)
        search_sql = self._noun_select
        arg_map = {"def_name": entity_def.get_namespace_name()}
        if len(search_filter) > 0:
            where_sql = self.build_where_clause(search_filter)
            search_sql += sql.SQL(" AND ({})").format(where_sql)

        with self.__conn.cursor() as cursor:
            cursor.execute(search_sql, arg_map)
            results = cursor.fetchall()

            if len(results) > 0:
                return [
                    Entity.deserialize(
                        entity_def,
                        {
                            **{
                                "identifier": r["id"],
                                "_updated": (
                                    r["updated_at"]
                                    .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                    .isoformat()
                                    if r["updated_at"]
                                    else r["updated_at"]
                                ),
                                "_created": (
                                    r["created_at"]
                                    .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                    .isoformat()
                                    if r["created_at"]
                                    else r["created_at"]
                                ),
                            },
                            **r["content"],
                        },
                    )
                    for r in results
                ]

        return []

    def search_relationships(
        self, entity_def: Type[Relationship], search_filter: Dict[str, Any]
    ) -> List[Relationship]:
        search_sql = sql.SQL("{rel_sql} AND r.{name} = {def_name} ").format(
            rel_sql=self._relationship_sql,
            name=sql.Identifier("name"),
            def_name=sql.Placeholder("def_name"),
        )
        arg_map = {"def_name": entity_def.get_namespace_name()}
        if len(search_filter) > 0:
            count, where_sql = self.build_where_clause(search_filter)
            search_sql += sql.SQL(" AND ({})").format(where_sql)

        results = []
        with self.__conn.cursor() as cursor:
            cursor.execute(search_sql, arg_map)
            data = cursor.fetchall()

            if len(data) > 0:
                for r in data:
                    rel = Entity.deserialize(
                        entity_def,
                        {
                            **{
                                "identifier": r["id"],
                                "ref_from": r["from_id"],
                                "ref_to": r["to_id"],
                                "_updated": (
                                    r["updated_at"]
                                    .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                    .isoformat()
                                    if r["updated_at"]
                                    else r["updated_at"]
                                ),
                                "_created": (
                                    r["created_at"]
                                    .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                    .isoformat()
                                    if r["created_at"]
                                    else r["created_at"]
                                ),
                            },
                            **r["content"],
                        },
                    )
                    results.append(rel)

        return results

    def list_entities(self, loader: DefaultLoader, id: str = None) -> List[Noun]:
        raise NotImplementedError()

    def put_entity(self, entity: Type[Entity]):
        if isinstance(entity, Noun):
            return self.put_noun(entity)
        else:
            return self.put_relationship(entity)

    def put_noun(self, entity: Noun) -> Noun:
        sql_insert = sql.SQL(
            "INSERT INTO entity(id, name, content, updated_at) VALUES (%(id)s, %(name)s, %(content)s, %(updated_at)s) returning created_at"
        )
        sql_update = sql.SQL(
            "UPDATE entity SET name = %(name)s, content = %(content)s, updated_at = %(updated_at)s WHERE id=%(id)s returning created_at;"
        )
        statement = sql_update
        entity._updated = datetime.datetime.now(datetime.timezone.utc)
        if not hasattr(entity, "identifier") or entity.identifier is None:
            entity.identifier = gen_new_key()
            statement = sql_insert
        with self.__conn.cursor() as cursor:
            entity_dict = entity.serialize()
            if "identifier" in entity_dict:
                del entity_dict["identifier"]
            if "_updated" in entity_dict:
                del entity_dict["_updated"]
            if "_created" in entity_dict:
                del entity_dict["_created"]
            cursor.execute(
                statement,
                {
                    "id": entity.identifier,
                    "name": entity.__class__.get_namespace_name(),
                    "content": json.dumps(entity_dict),
                    "updated_at": entity._updated,
                },
            )
            entity._created = cursor.fetchone()["created_at"].replace(
                tzinfo=zoneinfo.ZoneInfo("UTC")
            )

        return entity

    def put_relationship(self, relationship: Relationship) -> Relationship:
        sql_insert = """
            INSERT INTO relationship(id, name, content, from_name, from_id, to_name, to_id, updated_at)
            VALUES (%(id)s, %(name)s, %(content)s, %(from_name)s, %(from_id)s, %(to_name)s, %(to_id)s, %(updated_at)s)
            returning created_at
        """

        sql_update = """
            UPDATE relationship SET name = %(name)s, content = %(content)s, from_name = %(from_name)s, from_id = %(from_id)s,
            to_name = %(to_name)s, to_id = %(to_id)s, updated_at = %(updated_at)s WHERE id=%(id)s
            returning created_at;
        """
        statement = sql_update
        relationship._updated = datetime.datetime.now(datetime.timezone.utc)
        if not hasattr(relationship, "identifier") or relationship.identifier is None:
            relationship.identifier = gen_new_key()
            statement = sql_insert
        with self.__conn.cursor() as cursor:
            rel_dict = relationship.serialize()
            if "identifier" in rel_dict:
                del rel_dict["identifier"]
            if "_updated" in rel_dict:
                del rel_dict["_updated"]
            if "_created" in rel_dict:
                del rel_dict["_created"]
            del rel_dict["ref_from"]
            del rel_dict["ref_to"]
            cursor.execute(
                statement,
                {
                    "id": relationship.identifier,
                    "name": relationship.__class__.get_namespace_name(),
                    "content": json.dumps(rel_dict),
                    "from_name": relationship.ref_from_type().get_namespace_name(),
                    "from_id": (
                        relationship.ref_from.identifier
                        if isinstance(
                            relationship.ref_from, relationship.ref_from_type()
                        )
                        else relationship.ref_from
                    ),
                    "to_name": relationship.ref_to_type().get_namespace_name(),
                    "to_id": (
                        relationship.ref_to.identifier
                        if isinstance(relationship.ref_to, relationship.ref_to_type())
                        else relationship.ref_to
                    ),
                    "updated_at": relationship._updated,
                },
            )
            relationship._created = cursor.fetchone()["created_at"].replace(
                tzinfo=zoneinfo.ZoneInfo("UTC")
            )

        return relationship

    def delete_entity(self, entity_def: Type[Entity], id: str) -> None:
        table = "relationship"
        if issubclass(entity_def, Noun):
            table = "entity"

            # first delete any relationships to/from this entity
            sql_delete = f"""
                UPDATE RELATIONSHIP SET is_deleted = TRUE where (from_id = %(id)s or to_id = %(id)s)
            """
            with self.__conn.cursor() as cursor:
                cursor.execute(sql_delete, {"id": id})

        sql_delete = f"""
            UPDATE {table} SET is_deleted = TRUE where id = %(id)s and name = %(name)s
        """
        with self.__conn.cursor() as cursor:
            cursor.execute(
                sql_delete, {"id": id, "name": entity_def.get_namespace_name()}
            )

    def _get_relationships(
        self, relationship_def: Type[Relationship], id_: str, from_to: str
    ) -> List[Relationship]:
        if from_to not in ["from", "to"]:
            raise Exception(f'argument, from_to, must be "from" or "to", was {from_to}')

        sql_select = sql.SQL(
            "{rel_sql} AND r.{id} = {def_id} AND r.{name} = {def_name}"
        ).format(
            rel_sql=self._relationship_sql,
            id=sql.Identifier(f"{from_to}_id"),
            def_id=sql.Placeholder("id"),
            name=sql.Identifier("name"),
            def_name=sql.Placeholder("name"),
        )
        results = []

        with self.__conn.cursor() as cursor:
            cursor.execute(
                sql_select, {"id": id_, "name": relationship_def.get_namespace_name()}
            )
            data = cursor.fetchall()

            if len(data) > 0:
                for r in data:
                    rel = Entity.deserialize(
                        relationship_def,
                        {
                            **{
                                "identifier": r["id"],
                                "ref_from": r["from_id"],
                                "ref_to": r["to_id"],
                                "_updated": (
                                    r["updated_at"].isoformat()
                                    if r["updated_at"]
                                    else r["updated_at"]
                                ),
                                "_created": (
                                    r["created_at"].isoformat()
                                    if r["created_at"]
                                    else r["created_at"]
                                ),
                            },
                            **r["content"],
                        },
                    )
                    results.append(rel)

        return results

    def upsert_entities(self, entities):
        nouns = entities.get("nouns", [])
        relationships = entities.get("relationships", [])
        noun_sql = sql.SQL(
            "INSERT INTO entity(id, name, content, updated_at) VALUES (%(id)s, %(name)s, %(content)s, %(updated_at)s) "
            "ON CONFLICT (id) DO UPDATE SET name = %(name)s, content = %(content)s, updated_at = %(updated_at)s"
        )
        relationship_sql = sql.SQL(
            "INSERT INTO relationship(id, name, content, from_name, from_id, to_name, to_id, updated_at) "
            "VALUES (%(id)s, %(name)s, %(content)s, %(from_name)s, %(from_id)s, %(to_name)s, %(to_id)s, %(updated_at)s) "
            "ON CONFLICT (id) DO UPDATE SET name = %(name)s, content = %(content)s, from_name = %(from_name)s, "
            "from_id = %(from_id)s, to_name = %(to_name)s, to_id = %(to_id)s, updated_at = %(updated_at)s"
        )
        _updated = datetime.datetime.now(datetime.timezone.utc)

        noun_statements = []
        relationship_statements = []

        for noun in nouns:
            if not hasattr(noun, "identifier") or noun.identifier is None:
                noun.identifier = gen_new_key()
            entity_dict = noun.serialize()
            if "identifier" in entity_dict:
                del entity_dict["identifier"]
            if "_updated" in entity_dict:
                del entity_dict["_updated"]
            if "_created" in entity_dict:
                del entity_dict["_created"]
            noun_statements.append(
                {
                    "id": noun.identifier,
                    "name": noun.__class__.get_namespace_name(),
                    "content": json.dumps(entity_dict),
                    "updated_at": _updated,
                },
            )

        with self.__conn.cursor() as cursor:
            cursor.executemany(noun_sql, noun_statements)

        for relationship in relationships:
            if (
                not hasattr(relationship, "identifier")
                or relationship.identifier is None
            ):
                relationship.identifier = gen_new_key()
            rel_dict = relationship.serialize()
            if "identifier" in rel_dict:
                del rel_dict["identifier"]
            if "_updated" in rel_dict:
                del rel_dict["_updated"]
            if "_created" in rel_dict:
                del rel_dict["_created"]
            del rel_dict["ref_from"]
            del rel_dict["ref_to"]
            relationship_statements.append(
                {
                    "id": relationship.identifier,
                    "name": relationship.__class__.get_namespace_name(),
                    "content": json.dumps(rel_dict),
                    "from_name": relationship.ref_from_type().get_namespace_name(),
                    "from_id": (
                        relationship.ref_from.identifier
                        if isinstance(
                            relationship.ref_from, relationship.ref_from_type()
                        )
                        else relationship.ref_from
                    ),
                    "to_name": relationship.ref_to_type().get_namespace_name(),
                    "to_id": (
                        relationship.ref_to.identifier
                        if isinstance(relationship.ref_to, relationship.ref_to_type())
                        else relationship.ref_to
                    ),
                    "updated_at": _updated,
                }
            )

        with self.__conn.cursor() as cursor:
            cursor.executemany(relationship_sql, relationship_statements)

        return {
            "nouns": nouns,
            "relationships": relationships,
        }

    def native_query_nouns(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        results = []
        with self.__conn.cursor() as cursor:
            cursor.execute(query, data)
            data = cursor.fetchall()

            if len(data) > 0:
                for r in data:
                    results.append(
                        (
                            r["name"],
                            {
                                **{
                                    "identifier": r["id"],
                                    "_updated": (
                                        r["updated_at"]
                                        .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                        .isoformat()
                                        if r["updated_at"]
                                        else r["updated_at"]
                                    ),
                                    "_created": (
                                        r["created_at"]
                                        .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                        .isoformat()
                                        if r["created_at"]
                                        else r["created_at"]
                                    ),
                                },
                                **r["content"],
                            },
                        )
                    )

        return results

    def native_query_relationships(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        results = []
        with self.__conn.cursor() as cursor:
            cursor.execute(query, data)
            data = cursor.fetchall()

            if len(data) > 0:
                for r in data:
                    results.append(
                        (
                            r["name"],
                            {
                                **{
                                    "identifier": r["id"],
                                    "ref_from": r["from_id"],
                                    "ref_to": r["to_id"],
                                    "_updated": (
                                        r["updated_at"]
                                        .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                        .isoformat()
                                        if r["updated_at"]
                                        else r["updated_at"]
                                    ),
                                    "_created": (
                                        r["created_at"]
                                        .replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                                        .isoformat()
                                        if r["created_at"]
                                        else r["created_at"]
                                    ),
                                },
                                **r["content"],
                            },
                        )
                    )

        return results

    def get_relationships_from(
        self, relationship_def: Type[Relationship], id_: str
    ) -> List[Relationship]:
        return self._get_relationships(relationship_def, id_, "from")

    def get_relationships_to(
        self, relationship_def: Type[Relationship], id_: str
    ) -> List[Relationship]:
        return self._get_relationships(relationship_def, id_, "to")

    def begin_transaction(self) -> None:
        self.__conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        pass

    def commit_transaction(self) -> None:
        self.__conn.commit()
        self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    def rollback_transaction(self) -> None:
        self.__conn.rollback()
        self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
