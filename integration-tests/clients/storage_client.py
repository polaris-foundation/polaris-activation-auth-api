from behave.runner import Context
from environs import Env
from sqlalchemy import create_engine


def setup_storage(context: Context) -> None:
    env: Env = Env()
    host: str = env.str("DATABASE_HOST", "dhos-activation-auth-api-db")
    port: int = env.int("DATABASE_PORT", 5432)
    user_name: str = env.str("DATABASE_USER", "dhos-activation-auth-api")
    password: str = env.str("DATABASE_PASSWORD", "dhos-activation-auth-api")
    db_name: str = env.str("DATABASE_NAME", "dhos-activation-auth-api")

    engine = create_engine(
        f"postgresql://{user_name}:{password}@{host}:{port}/{db_name}"
    )

    connection = engine.connect()
    connection = connection.execution_options(isolation_level="READ UNCOMMITTED")
    context.db = connection


def patient_has_activation_record(context: Context, patient_uuid: str) -> bool:
    activation_code_results = (
        context.db.execute(
            f"SELECT count(*) FROM patient_activation WHERE patient_id='{patient_uuid}' limit 1;"
        )
        .first()
        .values()
    )
    return activation_code_results[0] > 0
