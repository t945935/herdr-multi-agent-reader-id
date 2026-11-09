from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator

from . import db


@asynccontextmanager
async def lifespan(app):
    db.init_db()
    yield


app = FastAPI(title="Pengelola Tugas Herdr", lifespan=lifespan)
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

VALIDATION_MESSAGES = {
    "missing": "Kolom wajib ini belum diisi",
    "string_type": "Nilai harus berupa teks",
    "bool_type": "Nilai harus berupa boolean",
    "extra_forbidden": "Kolom tambahan tidak diizinkan",
    "int_parsing": "Nilai harus berupa bilangan bulat",
}


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    details = []
    for error in exc.errors():
        context = error.get("ctx") or {}
        if error["type"] == "value_error" and "error" in context:
            message = str(context["error"])
        else:
            message = VALIDATION_MESSAGES.get(error["type"], "Nilai tidak valid")
        details.append({"loc": error.get("loc", []), "msg": message, "type": error.get("type", "validation_error")})
    return JSONResponse(status_code=422, content={"detail": details})



class CreateTask(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str
    description: str = ""

    @field_validator("title")
    @classmethod
    def title_valid(cls, value):
        if not value.strip():
            raise ValueError("Judul tugas tidak boleh kosong")
        return value.strip()


class PatchTask(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

    @field_validator("title", "description", "completed")
    @classmethod
    def explicit_null_invalid(cls, value):
        if value is None:
            raise ValueError("Nilai null eksplisit tidak didukung")
        return value

    @field_validator("title")
    @classmethod
    def title_valid(cls, value):
        return CreateTask.title_valid(value)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/tasks")
def list_tasks():
    return db.get_tasks()


@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    task = db.get_task(task_id)
    if task is None:
        raise HTTPException(404, "Tugas tidak ditemukan")
    return task


@app.post("/api/tasks", status_code=201)
def create_task(body: CreateTask):
    return db.create_task(**body.model_dump())


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, body: PatchTask):
    task = db.update_task(task_id, **body.model_dump(exclude_unset=True))
    if task is None:
        raise HTTPException(404, "Tugas tidak ditemukan")
    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if not db.delete_task(task_id):
        raise HTTPException(404, "Tugas tidak ditemukan")
    return Response(status_code=204)
