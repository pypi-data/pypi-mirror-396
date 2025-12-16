def build_entity_engine(
    host: str, user: str = "hmdroot", password: str = "", db_name: str = "hmd_entities"
):
    from .engines import PostgresEngine

    return PostgresEngine(host, user=user, password=password, db_name=db_name)


def build_local_entity_engine(database_path: str, echo: bool = False):
    from .engines import SqliteEngine

    return SqliteEngine(database_path, echo)
