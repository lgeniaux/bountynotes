from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.db.session import get_session
from app.main import app


def test_manual_source_flow(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Session:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/sources/manual",
                json={
                    "title": "Test source",
                    "raw_content": "Manual test content",
                },
            )

            assert create_response.status_code == 201
            created_source = create_response.json()
            assert created_source["title"] == "Test source"
            assert created_source["source_type"] == "manual"
            assert created_source["status"] == "pending"
            assert created_source["error_message"] is None
            assert created_source["processed_at"] is None

            list_response = client.get("/sources")
            assert list_response.status_code == 200
            listed_sources = list_response.json()
            assert len(listed_sources) == 1
            assert listed_sources[0]["id"] == created_source["id"]
            assert listed_sources[0]["status"] == "ready"
            assert listed_sources[0]["error_message"] is None
            assert listed_sources[0]["processed_at"] is not None

            detail_response = client.get(f"/sources/{created_source['id']}")
            assert detail_response.status_code == 200
            assert detail_response.json()["raw_content"] == "Manual test content"
            assert detail_response.json()["clean_content"] == "Manual test content"
            assert detail_response.json()["status"] == "ready"
            assert detail_response.json()["processed_at"] is not None

            missing_response = client.get("/sources/999999")
            assert missing_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_manual_source_processing_marks_source_failed_when_content_is_empty(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Session:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/sources/manual",
                json={
                    "title": "Whitespace source",
                    "raw_content": "   ",
                },
            )

            assert create_response.status_code == 201
            created_source = create_response.json()
            assert created_source["status"] == "pending"

            detail_response = client.get(f"/sources/{created_source['id']}")
            assert detail_response.status_code == 200
            assert detail_response.json()["status"] == "failed"
            assert (
                detail_response.json()["error_message"]
                == "Source content is empty after normalization"
            )
            assert detail_response.json()["processed_at"] is None
    finally:
        app.dependency_overrides.clear()
