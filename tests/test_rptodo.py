import pytest
import json
from rptodo import SUCCESS, DB_READ_ERROR, ID_ERROR
from rptodo.rptodo import Todoer
from rptodo.database import JSONDatabaseHandler

@pytest.fixture
def mock_json_file(tmp_path):
    todo = [{"Description": "Get some milk.", "Priority": 2, "Done": False}]
    db_file = tmp_path / "todo.json"
    with db_file.open("w") as db:
        json.dump(todo, db, indent=4)
    return db_file

def test_add(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    result = todoer.add(["Clean", "the", "house"], priority=1)
    assert result.error == SUCCESS
    assert result.todo["Description"] == "Clean the house."
    assert result.todo["Priority"] == 1
    assert result.todo["Done"] == False

    todo_list = todoer.get_todo_list()
    assert len(todo_list) == 2  # A tarefa original + nova tarefa


def test_get_todo_list(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    todo_list = todoer.get_todo_list()
    assert len(todo_list) == 1  # Apenas a tarefa mock inicial
    assert todo_list[0]["Description"] == "Get some milk."

def test_set_done(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    result = todoer.set_done(1)
    assert result.error == SUCCESS
    assert result.todo["Done"] == True

    todo_list = todoer.get_todo_list()
    assert todo_list[0]["Done"] == True

def test_set_done_invalid_id(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    result = todoer.set_done(99)  # ID inválido
    assert result.error == ID_ERROR

def test_remove(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    result = todoer.remove(1)
    assert result.error == SUCCESS
    assert result.todo["Description"] == "Get some milk."

    todo_list = todoer.get_todo_list()
    assert len(todo_list) == 0  # Tarefa removida

def test_remove_invalid_id(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    result = todoer.remove(99)  # ID inválido
    assert result.error == ID_ERROR

def test_remove_all(mock_json_file):
    db_handler = JSONDatabaseHandler(mock_json_file)
    todoer = Todoer(db_handler)

    result = todoer.remove_all()
    assert result.error == SUCCESS

    todo_list = todoer.get_todo_list()
    assert len(todo_list) == 0 