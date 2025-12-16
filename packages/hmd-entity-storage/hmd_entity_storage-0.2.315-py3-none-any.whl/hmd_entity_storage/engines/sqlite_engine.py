import logging
import pathlib
from datetime import datetime, timezone
from operator import itemgetter
from typing import Any, Dict, List, Type, Union, Tuple, Optional

from alembic import command
from alembic.config import Config
from hmd_meta_types import Entity, Noun, Relationship
from sqlalchemy import MetaData, create_engine, delete, insert, update, event
from sqlalchemy.orm import Session, aliased
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import and_, or_, select

from hmd_cli_tools import cd
from hmd_schema_loader import DefaultLoader
from .base_engine import BaseEngine, gen_new_key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SqliteEngine(BaseEngine):
    def __init__(
        self, database_path: Union[str, pathlib.Path], echo=False, timeout=30.0
    ):
        """
        Initialize SQLite engine with database locking retry support.

        Args:
            database_path: Path to the SQLite database file
            echo: Whether to echo SQL statements (default: False)
            timeout: Database busy timeout in seconds (default: 30.0)
                    SQLite will wait this long for locks to clear before raising OperationalError
        """
        self._db_uri = f"sqlite+pysqlite:///{database_path}"
        logger.info(self._db_uri)
        lib_dir = pathlib.Path(__file__).absolute().parent.parent

        alembic_dir = lib_dir / "alembic"
        alembic_ini = alembic_dir / "alembic.ini"

        if alembic_ini.exists():
            logger.info(alembic_ini)

            with cd(alembic_dir):
                alembic_cfg = Config()
                alembic_cfg.set_main_option("script_location", ".")
                alembic_cfg.set_main_option("sqlalchemy.url", self._db_uri)
                command.upgrade(alembic_cfg, "head")

        # Create engine with memory-optimized settings for SQLite
        # Use NullPool to avoid connection pooling (SQLite is single-writer)
        self._engine = create_engine(
            self._db_uri,
            echo=echo,
            future=True,
            poolclass=NullPool,  # No connection pooling - prevents memory accumulation
            connect_args={
                "check_same_thread": False,  # Allow multi-thread access
                "timeout": timeout,  # Wait up to timeout seconds for locks to clear
            },
        )

        # Store timeout for PRAGMA setting
        self._timeout_ms = int(timeout * 1000)

        # Apply memory-efficient PRAGMA settings to all connections
        # This is CRITICAL for preventing 50 GB memory spikes with large databases
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            try:
                # Set busy timeout at connection level for extra robustness
                # This complements the timeout in connect_args
                cursor.execute(f"PRAGMA busy_timeout = {self._timeout_ms}")
                # Limit cache to 32 MB (CRITICAL for 11 GB database)
                cursor.execute("PRAGMA cache_size = 8000")
                # Disable memory mapping (prevents 11 GB virtual memory usage)
                cursor.execute("PRAGMA mmap_size = 0")
                # Use WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode = WAL")
                # Checkpoint WAL frequently to prevent growth
                cursor.execute("PRAGMA wal_autocheckpoint = 500")
                # Use file for temp storage (safer for large DBs)
                cursor.execute("PRAGMA temp_store = FILE")
                # Balance safety and performance
                cursor.execute("PRAGMA synchronous = NORMAL")
                dbapi_conn.commit()
                logger.debug(
                    f"Applied memory-efficient PRAGMA settings to SQLite connection (busy_timeout={self._timeout_ms}ms)"
                )
            except Exception as e:
                logger.error(f"Error applying PRAGMA settings: {e}")
            finally:
                cursor.close()

        self._metadata = MetaData()
        self._metadata.reflect(bind=self._engine)
        self.tables = {
            Noun: self._metadata.tables["entity"],
            Relationship: self._metadata.tables["relationship"],
        }

    def _deserialze_entity(self, entity_def, row):
        if issubclass(entity_def, Relationship):
            identifier, content, rel_from, rel_to = row
            return Entity.deserialize(
                entity_def,
                {
                    **{
                        "identifier": identifier,
                        "ref_from": rel_from,
                        "ref_to": rel_to,
                    },
                    **content,
                },
            )

        identifier, content = row
        data = {"identifier": identifier, **content}
        return Entity.deserialize(entity_def, data)

    def _deserialze_entities(self, entity_def, rows):
        return [self._deserialze_entity(entity_def, row) for row in rows]

    def get_entity(self, entity_def: Type[Entity], id: str) -> Entity:
        if issubclass(entity_def, Noun):
            return self.get_noun(entity_def, id)
        else:
            raise NotImplementedError()

    def get_entities(self, entity_def: Type[Entity], ids_: List[str]) -> List[Entity]:
        # todo: attempt to query multiple entities at the same time
        if not issubclass(entity_def, Noun):
            raise NotImplementedError()

        results = []
        for id_ in ids_:
            result = self.get_noun(entity_def, id_)
            if not result:
                raise Exception(
                    f"Entity of type {entity_def.get_namespace_name()} with id {id_} not found."
                )
            results.append(result)
        return results

    def get_noun(self, entity_def: Type[Noun], id: str) -> Noun:
        def_name = entity_def.get_namespace_name()
        columns = self.tables[Noun].columns
        query = select(columns.id, columns.content).where(
            columns.id == id, columns.name == def_name, columns.is_deleted == False
        )

        with Session(self._engine) as session:
            result = session.execute(query).fetchone()
            if result:
                return self._deserialze_entity(entity_def, result)
        return None

    def search_entities(
        self, entity_def: Type[Entity], search_filter: Dict[str, Any] = dict()
    ) -> List[Entity]:
        if issubclass(entity_def, Noun):
            return self.search_noun(entity_def, search_filter)
        elif issubclass(entity_def, Relationship):
            return self.search_relationships(entity_def, search_filter)
        else:
            raise NotImplementedError()

    def build_where_clause(self, table, condition: Dict[str, Any]):
        if "and" in condition:
            subs = [
                self.build_where_clause(table, sub_condition)
                for sub_condition in condition["and"]
            ]
            return and_(*subs)

        elif "or" in condition:
            subs = [
                self.build_where_clause(table, sub_condition)
                for sub_condition in condition["or"]
            ]
            return or_(*subs)
        else:
            attribute, operator_key = itemgetter("attribute", "operator")(condition)
            where_sql = table.c.content[attribute].as_string().op(operator_key)
            if "value" in condition:
                where_sql = where_sql(condition["value"])
            elif "attribute_target" in condition:
                where_sql = where_sql(
                    table.c.content[condition["attribute_target"]].as_string()
                )

            return where_sql

    def search_noun(
        self, entity_def: Type[Noun], search_filter: Dict[str, Any] = dict()
    ) -> List[Noun]:
        self._validate_search_criteria(entity_def.entity_definition(), search_filter)
        table = self.tables[Noun]
        if len(search_filter) > 0:
            query = select(table.c.id, table.c.content).where(
                table.c.name == entity_def.get_namespace_name(),
                self.build_where_clause(table, search_filter),
            )
            with Session(self._engine) as session:
                results = session.execute(query).fetchall()
                if len(results) > 0:
                    return self._deserialze_entities(entity_def, results)

        return []

    def search_relationships(
        self, entity_def: Type[Relationship], search_filter: Dict[str, Any]
    ) -> List[Relationship]:
        raise NotImplementedError()

    def list_entities(self, loader: DefaultLoader, id: str = None) -> List[Noun]:
        columns = self.tables[Noun].columns
        query = select(columns.id, columns.name, columns.content).where(
            columns.is_deleted == False
        )

        if id is not None:
            query = query.where(columns.id == id)

        ret = []
        with Session(self._engine) as session:
            results = session.execute(query).fetchall()

            if len(results) > 0:
                for row in results:
                    entity_class = loader.get(row["name"])
                    if entity_class is None:
                        raise Exception(f"No entity type found for name {row['name']}")
                    ret.append(entity_class(identifier=row["id"], **row["content"]))

        return ret

    def put_entity(self, entity: Type[Entity]):
        if isinstance(entity, Noun):
            return self.put_noun(entity)
        else:
            return self.put_relationship(entity)

    def get_upsert_statement(self, entity: Entity):
        table = self.tables[Relationship]
        if isinstance(entity, Noun):
            table = self.tables[Noun]

        if entity.identifier is None:
            return insert(table)
        return update(table).where(table.c.id == entity.identifier)

    def put_noun(self, entity: Noun) -> Noun:
        statement = self.get_upsert_statement(entity)
        if not hasattr(entity, "identifier") or entity.identifier is None:
            entity.identifier = gen_new_key()

        with Session(self._engine) as session:
            entity_dict = entity.serialize()
            if "identifier" in entity_dict:
                del entity_dict["identifier"]

            # Prepare statement data
            statement_data = {
                "id": entity.identifier,
                "name": entity.__class__.get_namespace_name(),
                "content": entity_dict,
            }

            # Handle optional timestamp attributes
            if hasattr(entity, "_created") and entity._created is not None:
                statement_data["created_at"] = entity._created
                # Remove from content to avoid duplication
                if "_created" in entity_dict:
                    del entity_dict["_created"]

            if hasattr(entity, "_updated") and entity._updated is not None:
                statement_data["updated_at"] = entity._updated
                # Remove from content to avoid duplication
                if "_updated" in entity_dict:
                    del entity_dict["_updated"]
            else:
                # Default to current time if _updated doesn't exist
                statement_data["updated_at"] = datetime.now(timezone.utc)

            session.execute(statement, statement_data)
            session.commit()
        return entity

    def put_relationship(self, relationship: Relationship) -> Relationship:
        statement = self.get_upsert_statement(relationship)
        if not hasattr(relationship, "identifier") or relationship.identifier is None:
            relationship.identifier = gen_new_key()
        with Session(self._engine) as session:
            rel_dict = relationship.serialize()
            if "identifier" in rel_dict:
                del rel_dict["identifier"]
            del rel_dict["ref_from"]
            del rel_dict["ref_to"]
            from_id = (
                relationship.ref_from
                if isinstance(relationship.ref_from, str)
                else relationship.ref_from.identifier
            )
            to_id = (
                relationship.ref_to
                if isinstance(relationship.ref_to, str)
                else relationship.ref_to.identifier
            )

            # Prepare statement data
            statement_data = {
                "id": relationship.identifier,
                "name": relationship.__class__.get_namespace_name(),
                "content": rel_dict,
                "from_name": relationship.ref_from_type().get_namespace_name(),
                "from_id": from_id,
                "to_name": relationship.ref_to_type().get_namespace_name(),
                "to_id": to_id,
            }

            # Handle optional timestamp attributes
            if hasattr(relationship, "_created") and relationship._created is not None:
                statement_data["created_at"] = relationship._created
                # Remove from content to avoid duplication
                if "_created" in rel_dict:
                    del rel_dict["_created"]

            if hasattr(relationship, "_updated") and relationship._updated is not None:
                statement_data["updated_at"] = relationship._updated
                # Remove from content to avoid duplication
                if "_updated" in rel_dict:
                    del rel_dict["_updated"]
            else:
                # Default to current time if _updated doesn't exist
                statement_data["updated_at"] = datetime.now(timezone.utc)

            session.execute(statement, statement_data)
            session.commit()
        return relationship

    def delete_entity(self, entity_def: Type[Entity], id) -> None:
        with Session(self._engine) as session:
            table = self.tables[Relationship]
            if issubclass(entity_def, Noun):
                statement = (
                    update(table)
                    .where(or_(table.c.from_id == id, table.c.to_id == id))
                    .values(is_deleted=True)
                )

                session.execute(statement)
                table = self.tables[Noun]

            statement = (
                update(table)
                .where(
                    and_(
                        table.c.id == id,
                        table.c.name == entity_def.get_namespace_name(),
                    )
                )
                .values(is_deleted=True)
            )
            session.execute(statement)

            session.commit()

    def _get_relationships(
        self, relationship_def: Type[Relationship], id, from_to: str
    ) -> List[Relationship]:
        if from_to not in ["from", "to"]:
            raise Exception(f'argument, from_to, must be "from" or "to", was {from_to}')
        results = []
        with Session(self._engine) as session:
            columns = self.tables[Relationship].columns
            noun_from = aliased(self.tables[Noun])
            noun_to = aliased(self.tables[Noun])
            query = (
                session.query(columns.id, columns.content, noun_from.c.id, noun_to.c.id)
                .join(
                    noun_from,
                    and_(
                        noun_from.c.id == columns.from_id,
                        noun_from.c.name == columns.from_name,
                    ),
                )
                .join(
                    noun_to,
                    and_(
                        noun_to.c.id == columns.to_id, noun_to.c.name == columns.to_name
                    ),
                )
                .filter(
                    and_(
                        columns[f"{from_to}_id"] == id,
                        columns.name == relationship_def.get_namespace_name(),
                        columns.is_deleted == False,
                    )
                )
            )
            data = session.execute(query).fetchall()
            if len(data) > 0:
                for row in data:
                    rel_id, rel_content, from_id, to_id = row
                    rel = Entity.deserialize(
                        relationship_def,
                        {
                            **{
                                "identifier": rel_id,
                                "ref_from": from_id,
                                "ref_to": to_id,
                            },
                            **rel_content,
                        },
                    )
                    results.append(rel)
                # return self._deserialze_entities(relationship_def, results)

        return results

    def get_relationships_from(
        self, relationship_def: Relationship, id: int
    ) -> List[Relationship]:
        return self._get_relationships(relationship_def, id, "from")

    def get_relationships_to(
        self, relationship_def: Relationship, id: int
    ) -> List[Relationship]:
        return self._get_relationships(relationship_def, id, "to")

    def upsert_entities(self, entities):
        return NotImplementedError()

    def native_query_nouns(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    def native_query_relationships(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    def get_stats(self) -> Dict:
        """
        Get database statistics for monitoring and diagnostics.

        Returns:
            Dictionary with database statistics including file size,
            cache settings, WAL info, etc.

        Example:
            >>> engine = SqliteEngine("/path/to/db.db")
            >>> stats = engine.get_stats()
            >>> print(f"Database size: {stats['file_size_mb']:.2f} MB")
        """
        from ..utils.sqlite_utils import get_database_stats

        # Extract db path from URI (sqlite+pysqlite:///path/to/db.db)
        db_path = self._db_uri.replace("sqlite+pysqlite:///", "")
        return get_database_stats(pathlib.Path(db_path))

    def vacuum(self, analyze: bool = True) -> Dict[str, float]:
        """
        Vacuum database to reclaim space and optimize structure.

        Args:
            analyze: Whether to run ANALYZE after VACUUM (default: True)

        Returns:
            Dictionary with size_before_mb, size_after_mb, reclaimed_mb

        Example:
            >>> engine = SqliteEngine("/path/to/db.db")
            >>> result = engine.vacuum()
            >>> print(f"Reclaimed {result['reclaimed_mb']:.2f} MB")
        """
        from ..utils.sqlite_utils import vacuum_database

        db_path = self._db_uri.replace("sqlite+pysqlite:///", "")
        return vacuum_database(pathlib.Path(db_path), analyze=analyze)

    def checkpoint_wal(self, mode: str = "PASSIVE") -> Optional[Dict[str, int]]:
        """
        Checkpoint the WAL (Write-Ahead Log) file.

        Args:
            mode: Checkpoint mode - PASSIVE, FULL, RESTART, or TRUNCATE

        Returns:
            Dictionary with checkpoint results or None if not in WAL mode

        Example:
            >>> engine = SqliteEngine("/path/to/db.db")
            >>> result = engine.checkpoint_wal("PASSIVE")
            >>> if result:
            ...     print(f"Moved {result['moved_frames']} frames")
        """
        from ..utils.sqlite_utils import checkpoint_wal

        db_path = self._db_uri.replace("sqlite+pysqlite:///", "")
        return checkpoint_wal(pathlib.Path(db_path), mode=mode)

    def check_integrity(self, quick: bool = False) -> bool:
        """
        Check database integrity.

        Args:
            quick: If True, do quick check. If False, do full check

        Returns:
            True if database is OK, False otherwise

        Example:
            >>> engine = SqliteEngine("/path/to/db.db")
            >>> if engine.check_integrity():
            ...     print("Database is healthy")
        """
        from ..utils.sqlite_utils import check_database_integrity

        db_path = self._db_uri.replace("sqlite+pysqlite:///", "")
        return check_database_integrity(pathlib.Path(db_path), quick=quick)

    def clean_db(
        self,
        nouns: List[str],
        relationships: List[str],
        before_timestamp: Optional[str] = None,
    ) -> None:
        """
        Clean database by deleting all entities of specified types.

        Args:
            nouns: List of noun type names to delete
            relationships: List of relationship type names to delete

        Example:
            >>> engine = SqliteEngine("/path/to/db.db")
            >>> engine.clean_db(nouns=["File", "User"], relationships=["Owns"])
        """
        with Session(self._engine) as session:
            table = self.tables[Relationship]
            where_clause = table.c.name.in_(relationships)
            if before_timestamp is not None:
                where_clause = and_(where_clause, table.c.created_at < before_timestamp)
            if len(relationships) > 0:
                statement = delete(table).where(where_clause)
                session.execute(statement)

            table = self.tables[Noun]
            where_clause = table.c.name.in_(nouns)
            if before_timestamp is not None:
                where_clause = and_(where_clause, table.c.created_at < before_timestamp)
            if len(nouns) > 0:
                statement = delete(table).where(where_clause)
                session.execute(statement)

            session.commit()
            self.vacuum(analyze=True)

    def close(self):
        """
        Properly dispose of engine resources.

        This releases database connections, caches, and other resources.
        Important for preventing memory leaks in long-running applications.
        """
        if hasattr(self, "_engine"):
            logger.info("Disposing SQLite engine resources")
            self._engine.dispose()

    def __del__(self):
        """Destructor - cleanup if not already done."""
        try:
            self.close()
        except:
            # Avoid errors during garbage collection
            pass

    def begin_transaction(self) -> None:
        pass

    def commit_transaction(self) -> None:
        pass

    def rollback_transaction(self) -> None:
        pass
