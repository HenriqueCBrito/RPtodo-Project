import configparser
from pathlib import Path
import typer

from rptodo import (
    DB_WRITE_ERROR, DIR_ERROR, FILE_ERROR, SUCCESS, __app_name__
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def init_app(db_path: str, db_type: str = "json") -> int:
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code

    database_code = _create_database(db_path, db_type)
    if database_code != SUCCESS:
        return database_code

    return SUCCESS

def _init_config_file() -> int:
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR

    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_ERROR

    return SUCCESS

def _create_database(db_path: str, db_type: str) -> int:
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"database": db_path, "db_type": db_type}

    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR

    if db_type == "json":
        return init_json_database(Path(db_path))
    elif db_type == "mongodb":
        return init_mongodb_database()
    else:
        return DB_WRITE_ERROR

def init_json_database(db_path: Path) -> int:
    try:
        db_path.write_text("[]")  # Empty to-do list
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR

def init_mongodb_database() -> int:
    try:
        # MongoDB automatically creates the database on first use, so no action is needed here
        return SUCCESS
    except Exception:
        return DB_WRITE_ERROR

def get_database_handler(config_file: Path):
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    db_path = config_parser["General"]["database"]
    db_type = config_parser["General"]["db_type"]

    if db_type == "json":
        from rptodo.database import JSONDatabaseHandler
        return JSONDatabaseHandler(Path(db_path))
    elif db_type == "mongodb":
        from rptodo.database import MongoDBHandler
        return MongoDBHandler()
    else:
        raise ValueError("Unsupported database type.")
