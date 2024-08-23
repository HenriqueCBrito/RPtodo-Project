import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from pymongo import MongoClient

from rptodo import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

class DBResponse(NamedTuple):
    todo_list: List[Dict[str, Any]]
    error: int

class JSONDatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_todos(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    data = json.load(db)
                    return DBResponse(data, SUCCESS)
                except json.JSONDecodeError:  # Catch JSON errors
                    return DBResponse([], JSON_ERROR)
        except FileNotFoundError:  # Catch file not found errors
            print(f"Error: The database file {self._db_path} was not found.")
            return DBResponse([], DB_READ_ERROR)
        except OSError:  # Catch other OS-related errors
            print(f"Error: Unable to read the database file {self._db_path}.")
            return DBResponse([], DB_READ_ERROR)

    def write_todos(self, todo_list: List[Dict[str, Any]]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(todo_list, db, indent=4)
            return DBResponse(todo_list, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(todo_list, DB_WRITE_ERROR)

class MongoDBHandler:
    def __init__(self):
        try:
            self.client = MongoClient("localhost", 27017)
            self.db = self.client.todoappdb
            self.items = self.db.items
        except Exception as e:
            print(f"Error: Unable to connect to MongoDB: {e}")
            raise e

    def read_todos(self) -> DBResponse:
        try:
            items_data = list(self.items.find())
            return DBResponse(items_data, SUCCESS)
        except Exception as e:
            print(f"Error: Unable to load data from MongoDB: {e}")
            return DBResponse([], DB_READ_ERROR)

    def write_todos(self, todo_list: List[Dict[str, Any]]) -> DBResponse:
        try:
            self.items.delete_many({})  # Clear existing data
            # add if to check for error here
            self.items.insert_many(todo_list)
            return DBResponse(todo_list, SUCCESS)
        except Exception:
            return DBResponse(todo_list, DB_WRITE_ERROR)
