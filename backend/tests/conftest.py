import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.services.seed_data import seed_initial_data

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_initial_data(db)
    db.close()
    yield

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
