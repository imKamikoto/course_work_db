import configparser
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()
engine = None
SessionLocal = None

def load_db_config(path: str = "../config.ini") -> dict:
    config = configparser.ConfigParser()
    read_files = config.read(path)
    if not read_files:
        raise RuntimeError(f"Не удалось прочитать файл конфигурации: {path}")

    db = config["db"]
    return {
        "host": db.get("host", "localhost"),
        "port": db.getint("port", 5432),
        "dbname": db["dbname"],
        "user": db["user"],
        "password": db["password"],
    }

def init_db(config_path: str = "../config.ini") -> None:
    global engine, SessionLocal

    cfg = load_db_config(config_path)

    database_url = (
        f"postgresql+pg8000://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    )

    engine = create_engine(database_url, echo=False, future=True)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        engine.dispose()
        raise RuntimeError(f"Не удалось подключиться к БД: {e}") from e

def get_session():
    if SessionLocal is None:
        raise RuntimeError("DB не инициализирована")
    return SessionLocal()