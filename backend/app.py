import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path

app = FastAPI()

ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
public_file_abspath = os.path.join(ROOT_PATH, "public")
public_file_abspath = Path(public_file_abspath).as_posix()
os.makedirs(public_file_abspath, exist_ok=True)


@app.get("/api")
def index():
    return JSONResponse({"status": 200, "msg": "ok"})


app.mount("/", StaticFiles(directory=public_file_abspath), name="public")
