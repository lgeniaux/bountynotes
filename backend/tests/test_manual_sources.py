from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

import app.services.source_service as source_service
from app.db.session import get_session
from app.main import app


def test_manual_source_flow(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Session:
        with Session(engine) as session:
            yield session

    class FakePreprocessingResult:
        clean_content = "Manual test content"
        summary = "LLM summary"
        techs = ["FastAPI"]
        tags = ["xss"]
        cwes = ["CWE-79"]
        cves = []
        chunks = []

    def fake_preprocess_source_content(content: str) -> FakePreprocessingResult:
        assert content == "Manual test content"
        return FakePreprocessingResult()

    indexed_chunk_calls: list[tuple[int | None, int]] = []

    def fake_index_source_chunks(source, chunks):
        indexed_chunk_calls.append((source.id, len(chunks)))
        return []

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(source_service, "preprocess_source_content", fake_preprocess_source_content)
    monkeypatch.setattr(source_service, "index_source_chunks", fake_index_source_chunks)

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
            assert detail_response.json()["summary"] == "LLM summary"
            assert detail_response.json()["techs"] == ["FastAPI"]
            assert detail_response.json()["tags"] == ["xss"]
            assert detail_response.json()["cwes"] == ["CWE-79"]
            assert detail_response.json()["cves"] == []
            assert detail_response.json()["status"] == "ready"
            assert detail_response.json()["processed_at"] is not None
            assert indexed_chunk_calls == [(created_source["id"], 0)]

            missing_response = client.get("/sources/999999")
            assert missing_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_manual_source_processing_marks_source_failed_when_preprocessing_raises(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Session:
        with Session(engine) as session:
            yield session

    def fake_preprocess_source_content(content: str):
        raise ValueError("DEEPSEEK_API_KEY is not configured")

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(source_service, "preprocess_source_content", fake_preprocess_source_content)

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/sources/manual",
                json={
                    "title": "Strict llm source",
                    "raw_content": "XSS write-up for CWE-79 linked to CVE-2024-12345.",
                },
            )

            assert create_response.status_code == 201
            created_source = create_response.json()

            detail_response = client.get(f"/sources/{created_source['id']}")
            assert detail_response.status_code == 200
            assert detail_response.json()["status"] == "failed"
            assert detail_response.json()["error_message"] == "DEEPSEEK_API_KEY is not configured"
    finally:
        app.dependency_overrides.clear()


def test_manual_source_creation_rejects_whitespace_only_raw_content(tmp_path: Path) -> None:
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

            assert create_response.status_code == 422
            error = create_response.json()
            assert error["detail"][0]["loc"] == ["body", "raw_content"]
            assert error["detail"][0]["type"] == "string_too_short"

            list_response = client.get("/sources")
            assert list_response.status_code == 200
            assert list_response.json() == []
    finally:
        app.dependency_overrides.clear()
