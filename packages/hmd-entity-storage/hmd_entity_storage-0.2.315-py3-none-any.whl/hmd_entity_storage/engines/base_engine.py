import os
import random
import time
from abc import ABC, abstractmethod
from typing import Type, Dict, List, Any, Tuple

from hmd_meta_types import Noun, Relationship, Entity


def get_env_var(env_var_name, throw=True):
    value = os.environ.get(env_var_name)
    if not value and throw:
        raise Exception(f"Environment variable {env_var_name} not populated.")
    return value


def gen_new_key() -> str:
    """Generate a new unique primary key.

    This method is intended to create a unique integer primary key that
    has a fairly large range of values.

    :return: Primary key.
    """
    secs = int(time.time_ns())
    secs = secs << 8 & 4294967295

    instance_name = get_env_var("HMD_INSTANCE_NAME")
    region = get_env_var("HMD_REGION")
    environment = get_env_var("HMD_ENVIRONMENT")
    customer_code = get_env_var("HMD_CUSTOMER_CODE")
    id_val = str((secs * 1000) + random.randrange(-999, 9999, 1))
    return f"{instance_name}-{environment}-{region}-{customer_code}-{id_val}"


class BaseEngine(ABC):
    @abstractmethod
    def get_entity(self, entity_def: Type[Entity], id_: str) -> Entity:
        raise NotImplementedError()

    @abstractmethod
    def get_entities(self, entity_def: Type[Entity], ids_: List[str]) -> List[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def search_entities(
        self, entity_def: Type[Entity], search_filter: Dict[str, Any]
    ) -> List[Entity]:
        raise NotImplementedError()

    @abstractmethod
    def list_entities(
        self, class_cache: Dict[str, Type[Entity]], id_: str = None
    ) -> List[Noun]:
        raise NotImplementedError()

    @abstractmethod
    def put_entity(self, entity: Entity) -> Entity:
        raise NotImplementedError()

    @abstractmethod
    def delete_entity(self, entity_def: Type[Entity], entity_id: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_relationships_from(
        self, relationship_def: Type[Relationship], id_: str
    ) -> List[Relationship]:
        raise NotImplementedError()

    @abstractmethod
    def get_relationships_to(
        self, relationship_def: Type[Relationship], id_: str
    ) -> List[Relationship]:
        raise NotImplementedError()

    operators = [">=", ">", "<=", "<", "=", "!="]

    @classmethod
    def _validate_search_criteria(cls, entity_definition: Dict, search_filter: Dict):
        if len(search_filter) == 0:
            return
        if "and" in search_filter or "or" in search_filter:
            assert len(search_filter) == 1, f"and/or node must be the only entry"
            sub_clauses = search_filter[list(search_filter.keys())[0]]
            assert isinstance(sub_clauses, list), f"and/or must have a list value"
            for clause in sub_clauses:
                cls._validate_search_criteria(entity_definition, clause)
        else:
            assert (
                "attribute" in search_filter
            ), f"no 'attribute' key in condition; keys: {', '.join(search_filter.keys())}"
            assert (
                "operator" in search_filter
            ), f"no 'operator' key in condition; keys: {', '.join(search_filter.keys())}"
            assert (
                "value" in search_filter or "attribute_target" in search_filter
            ), f"no 'value' or 'attribute_target' key in condition; keys: {', '.join(search_filter.keys())}"
            valid_keys = ["attribute", "operator", "value", "attribute_target"]
            assert all(
                key in valid_keys for key in search_filter
            ), f"invalid key in condition: {', '.join([key for key in search_filter if key not in valid_keys])}"

            attribute_names = list(entity_definition["attributes"].keys()) + [
                "_updated",
                "_created",
            ]
            assert (
                search_filter["attribute"] in attribute_names
            ), f"Invalid attribute: {search_filter['attribute']}; valid attributes are: {', '.join(attribute_names)}"
            if "attribute_target" in search_filter:
                assert (
                    search_filter["attribute_target"] in attribute_names
                ), f"Invalid attribute: {search_filter['attribute_target']}; valid attributes are: {', '.join(attribute_names)}"
            assert (
                search_filter["operator"] in cls.operators
            ), f"Invalid operator: {search_filter['operator']}; valid operators are: {', '.join(cls.operators)}"

    @abstractmethod
    def upsert_entities(
        self, entities: Dict[str, List[Entity]]
    ) -> Dict[str, List[Entity]]:
        raise NotImplementedError()

    @abstractmethod
    def native_query_nouns(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    @abstractmethod
    def native_query_relationships(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    @abstractmethod
    def begin_transaction(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def commit_transaction(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def rollback_transaction(self) -> None:
        raise NotImplementedError()
