from typing import Callable, Dict
from .hmd_entity_storage import build_entity_engine, build_local_entity_engine
from .engines import (
    BaseEngine,
    PostgresEngine,
    DynamoDbEngine,
    GremlinEngine,
    SqliteEngine,
    gen_new_key,
)


ENGINE_TYPES = ["dynamo", "postgres", "gremlin"]
POSTGRES_ENGINE = ENGINE_TYPES[1]
DYNAMO_ENGINE = ENGINE_TYPES[0]
GREMLIN_ENGINE = ENGINE_TYPES[2]


def make_postgres_engine(config: Dict, get_db_info: Callable) -> PostgresEngine:
    dbinfo = get_db_info(config)
    return PostgresEngine(
        dbinfo["host"], dbinfo["user"], dbinfo["password"], dbinfo["db_name"]
    )


def make_dynamo_engine(config: Dict) -> DynamoDbEngine:
    pitr = config.get("point_in_time_recovery")
    if pitr:
        assert pitr in ["enabled", "disabled"], (
            f'Dynamo configuration: "point_in_time_recovery" must be '
            f'one of "enabled", "disabled", was {pitr}.'
        )
    return DynamoDbEngine(config["dynamo_table"], config.get("dynamo_url"), pitr)


def make_gremlin_engine(config: Dict) -> GremlinEngine:
    return GremlinEngine(
        host=config["db_host"],
        port=config.get("db_port", 8182),
        user=config.get("db_user"),
        password=config.get("db_password", ""),
        protocol=config.get("db_protocol", "wss"),
        with_strategies=config.get("with_strategies", True),
    )


def get_engine_methods(get_db_info: Callable) -> Dict[str, Callable]:
    """
    Return a dictionary of engine methods based on the engine type.
    """
    return {
        POSTGRES_ENGINE: lambda config: make_postgres_engine(config, get_db_info),
        DYNAMO_ENGINE: make_dynamo_engine,
        GREMLIN_ENGINE: make_gremlin_engine,
    }


def get_db_engines(engine_config, get_db_info: Callable) -> Dict[str, BaseEngine]:
    """
    Get the database engines based on the engine configuration.
    """
    engine_methods = get_engine_methods(get_db_info)
    if not isinstance(engine_config, dict):
        raise Exception("Engine configuration must be a dictionary.")
    if not engine_config:
        raise Exception("Engine configuration cannot be empty.")

    if not all(
        isinstance(engine_config[engine_name], dict) for engine_name in engine_config
    ):
        raise Exception("Engine configuration must be a dictionary of dictionaries.")
    if not all(
        "engine_type" in engine_config[engine_name] for engine_name in engine_config
    ):
        raise Exception(
            "Engine configuration must contain 'engine_type' for each engine."
        )
    if not all(
        "engine_config" in engine_config[engine_name] for engine_name in engine_config
    ):
        raise Exception(
            "Engine configuration must contain 'engine_config' for each engine."
        )

    for engine_name in engine_config:
        eng_conf = engine_config[engine_name]
        if eng_conf["engine_type"] not in ENGINE_TYPES:
            Exception(f"Engine type, {eng_conf['engine_type']}, not supported.")
    return {
        engine_name: engine_methods[engine_config[engine_name]["engine_type"]](
            engine_config[engine_name]["engine_config"]
        )
        for engine_name in engine_config
    }
