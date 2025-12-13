from pathlib import Path
import socket

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

import app.clients.exa_client as exa_client_module
import app.services.source_service as source_service
import app.services.url_ingestion_service as url_ingestion_service
from app.db.session import get_session
from app.main import app
from app.services.url_ingestion_service import UrlContentFetchError, UrlIngestionResult


def test_url_source_flow(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Session:
        with Session(engine) as session:
            yield session

    def fake_ingest_url_content(url: str) -> UrlIngestionResult:
        assert url == "https://example.com/writeup"
        return UrlIngestionResult(
            raw_content="Fetched article text",
            clean_content="Fetched article text",
        )

    class FakePreprocessingResult:
        clean_content = "Fetched article text"
        summary = "URL summary"
        techs = ["HTTP"]
        tags = ["reference"]
        cwes = []
        cves = []
        chunks = []

    def fake_preprocess_source_content(content: str) -> FakePreprocessingResult:
        assert content == "Fetched article text"
        return FakePreprocessingResult()

    indexed_chunk_calls: list[tuple[int | None, int]] = []

    def fake_index_source_chunks(source, chunks):
        indexed_chunk_calls.append((source.id, len(chunks)))
        return []

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(source_service, "ingest_url_content", fake_ingest_url_content)
    monkeypatch.setattr(source_service, "preprocess_source_content", fake_preprocess_source_content)
    monkeypatch.setattr(source_service, "index_source_chunks", fake_index_source_chunks)

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/sources/url",
                json={
                    "title": "Example write-up",
                    "url": "https://example.com/writeup",
                },
            )

            assert create_response.status_code == 201
            created_source = create_response.json()
            assert created_source["title"] == "Example write-up"
            assert created_source["source_type"] == "url"
            assert created_source["status"] == "pending"
            assert created_source["raw_content"] == "Fetched article text"
            assert created_source["clean_content"] == "Fetched article text"
            assert created_source["error_message"] is None
            assert created_source["processed_at"] is None

            list_response = client.get("/sources")
            assert list_response.status_code == 200
            listed_sources = list_response.json()
            assert len(listed_sources) == 1
            assert listed_sources[0]["id"] == created_source["id"]
            assert listed_sources[0]["source_type"] == "url"
            # TestClient waits for background tasks, so this source is already processed here.
            assert listed_sources[0]["status"] == "ready"
            assert listed_sources[0]["processed_at"] is not None

            detail_response = client.get(f"/sources/{created_source['id']}")
            assert detail_response.status_code == 200
            assert detail_response.json()["raw_content"] == "Fetched article text"
            assert detail_response.json()["clean_content"] == "Fetched article text"
            assert detail_response.json()["summary"] == "URL summary"
            assert detail_response.json()["techs"] == ["HTTP"]
            assert detail_response.json()["tags"] == ["reference"]
            assert detail_response.json()["cwes"] == []
            assert detail_response.json()["cves"] == []
            assert detail_response.json()["status"] == "ready"
            assert detail_response.json()["processed_at"] is not None
            assert indexed_chunk_calls == [(created_source["id"], 0)]
    finally:
        app.dependency_overrides.clear()


def test_url_source_rejects_forbidden_target(tmp_path: Path) -> None:
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
            response = client.post(
                "/sources/url",
                json={
                    "title": "Local target",
                    "url": "http://localhost/internal",
                },
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "localhost is not allowed"
    finally:
        app.dependency_overrides.clear()


def test_url_source_returns_bad_gateway_when_fetch_fails(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Session:
        with Session(engine) as session:
            yield session

    def fake_ingest_url_content(url: str) -> UrlIngestionResult:
        raise UrlContentFetchError(f"Could not fetch content for {url}")

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(source_service, "ingest_url_content", fake_ingest_url_content)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/sources/url",
                json={
                    "title": "Broken page",
                    "url": "https://example.com/unreachable",
                },
            )

            assert response.status_code == 502
            assert (
                response.json()["detail"]
                == "Could not fetch content for https://example.com/unreachable"
            )
    finally:
        app.dependency_overrides.clear()


def test_url_source_returns_bad_gateway_when_exa_sdk_raises_unexpected_error(
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

    class FakeExa:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key

        def get_contents(self, urls: list[str], text: dict[str, object]) -> object:
            raise RuntimeError("provider timeout")

    def fake_getaddrinfo(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(url_ingestion_service.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(exa_client_module, "Exa", FakeExa)
    # Set the API key so this test hits the provider failure path, not config validation.
    monkeypatch.setattr(exa_client_module.settings, "exa_api_key", "test-key")

    try:
        with TestClient(app) as client:
            response = client.post(
                "/sources/url",
                json={
                    "title": "Slow page",
                    "url": "https://example.com/timeout",
                },
            )

            assert response.status_code == 502
            assert response.json()["detail"] == "Could not fetch URL content from Exa"
    finally:
        app.dependency_overrides.clear()
