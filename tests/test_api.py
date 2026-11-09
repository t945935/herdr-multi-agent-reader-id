import pytest
from fastapi.testclient import TestClient

from examples.task_manager import db
from examples.task_manager.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    with TestClient(app) as c:
        yield c


def test_crud_menyimpan_dan_menyajikan_frontend(client):
    assert client.get("/").status_code == 200
    for path in ["/static/app.js", "/static/style.css", "/openapi.json"]:
        assert client.get(path).status_code == 200
    assert client.get("/api/tasks").json() == []
    body = {"title": " Selesaikan proyek <script> ", "description": "Teks Bahasa Indonesia dengan tanda kutip ' dan aksara é"}
    response = client.post("/api/tasks", json=body)
    assert response.status_code == 201
    item = response.json()
    assert item["title"] == body["title"].strip() and item["completed"] is False
    task_id = item["id"]
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": True, "description": ""})
    assert response.status_code == 200 and response.json()["completed"] is True
    assert response.json()["description"] == ""
    # A second application lifespan reopens the same disk database.
    with TestClient(app) as reopened:
        assert reopened.get(f"/api/tasks/{task_id}").json()["completed"] is True
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


@pytest.mark.parametrize("body", [{}, {"title": " "}, {"title": None}, {"title": 3}, {"title": "ok", "unknown": 1}])
def test_create_menolak_payload_tidak_valid(client, body):
    response = client.post("/api/tasks", json=body)
    assert response.status_code == 422
    if body.get("title") == " ":
        assert "Judul tugas tidak boleh kosong" in response.json()["detail"][0]["msg"]


@pytest.mark.parametrize("body", [{"title": " "}, {"title": None}, {"completed": "true"}, {"completed": None}, {"description": None}, {"extra": 1}])
def test_validasi_patch(client, body):
    task_id = client.post("/api/tasks", json={"title": "A"}).json()["id"]
    assert client.patch(f"/api/tasks/{task_id}", json=body).status_code == 422


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_tugas_tidak_ditemukan(client, method):
    kwargs = {"json": {"title": "diperbarui"}} if method == "patch" else {}
    assert getattr(client, method)("/api/tasks/999", **kwargs).status_code == 404


def test_beberapa_catatan_tetap_independen(client):
    for name in ["Tugas A", "Tugas B", "Tugas C"]:
        assert client.post("/api/tasks", json={"title": name}).status_code == 201
    assert [r["title"] for r in client.get("/api/tasks").json()] == ["Tugas A", "Tugas B", "Tugas C"]
