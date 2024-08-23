import os
import typer

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Union
from starlette.requests import Request

from rptodo import SUCCESS, DB_READ_ERROR, ID_ERROR, __app_name__
from rptodo.database import JSONDatabaseHandler, MongoDBHandler
from rptodo.rptodo import Todoer
from configparser import ConfigParser

# Initialize Typer app and FastAPI app
app = typer.Typer()
fastapi_app = FastAPI()

# Setup paths and templates
CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
templates = Jinja2Templates(directory="/home/ricobrto/Documentos/rptodo_project/todo/templates")

# Load config
config_parser = ConfigParser()
config_parser.read(CONFIG_FILE_PATH)
db_path = config_parser["General"]["database"]
db_type = config_parser["General"]["db_type"]

# Initialize the database handler based on the config
db_handler: Union[JSONDatabaseHandler, MongoDBHandler]
if db_type == "json":
    db_handler = JSONDatabaseHandler(Path(db_path))
elif db_type == "mongodb":
    db_handler = MongoDBHandler()
else:
    raise ValueError(f"Unsupported database type: {db_type}")

todoer = Todoer(db_handler)

# CLI Commands
@app.command()
def init(db_path: str, db_type: str = "json"):
    """Initialize the application with the specified database."""
    config_parser["General"] = {"database": db_path, "db_type": db_type}
    with CONFIG_FILE_PATH.open("w") as file:
        config_parser.write(file)
    typer.echo("Configuration file created successfully.")

@app.command()
def add(description: List[str], priority: int = 2):
    """Add a new to-do item."""
    todo = todoer.add(description, priority)
    if todo.error:
        typer.echo(f"Error: {todo.error}")
    else:
        typer.echo(f"To-do added: {todo.todo['Description']}")

# FastAPI Endpoints
@fastapi_app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main page with the to-do list."""
    todos = todoer.get_todo_list()
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

@fastapi_app.post("/todos/")
async def add_todo(description: str, priority: int = 2):
    """Add a new to-do item via the API."""
    todo = todoer.add([description], priority)
    if todo.error:
        raise HTTPException(status_code=400, detail="Failed to add to-do")
    return {"status": "success", "todo": todo.todo}

@fastapi_app.post("/todos/{todo_id}/done")
async def mark_todo_done(todo_id: int):
    """Mark a to-do item as done via the API."""
    todo = todoer.set_done(todo_id)
    if todo.error == ID_ERROR:
        raise HTTPException(status_code=404, detail="To-do item not found")
    elif todo.error:
        raise HTTPException(status_code=400, detail="Failed to mark to-do as done")
    return {"status": "success", "todo": todo.todo}

@fastapi_app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a to-do item via the API."""
    todo = todoer.remove(todo_id)
    if todo.error == ID_ERROR:
        raise HTTPException(status_code=404, detail="To-do item not found")
    elif todo.error:
        raise HTTPException(status_code=400, detail="Failed to delete to-do")
    return {"status": "success", "todo": todo.todo}

if __name__ == "__main__":
    app()