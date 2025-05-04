import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.models.project import Project
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
import os
from typing import AsyncGenerator

# Создаем тестовую базу данных
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_project(client, test_session):
    project_data = {
        "name": "Test Project",
        "user_id": 0
    }
    response = await client.post("/projects/", json=project_data)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["name"] == "Test Project"
    assert data["user_id"] == 0
    assert "created_at" in data

@pytest.mark.asyncio
async def test_get_projects(client, test_session):
    # Создаем тестовые проекты
    projects_data = [
        {"name": "Test Project 1", "user_id": 0},
        {"name": "Test Project 2", "user_id": 0},
        {"name": "Test Project 3", "user_id": 23}
    ]
    
    for project in projects_data:
        response = await client.post("/projects/", json=project)
        assert response.status_code == 200
    
    # Тестируем получение проектов для пользователя с telegram_id=0
    response = await client.get("/projects/?telegram_id=0")
    assert response.status_code == 200, response.text
    data = response.json()
    
    # Проверяем, что вернулись все проекты пользователя
    assert len(data) == 2  # Должно быть 2 проекта для user_id=0
    
    # Проверяем содержимое проектов
    for project in data:
        assert project["user_id"] == 0
        assert "Test Project" in project["name"]
        assert "id" in project
        assert "created_at" in project
        
    # Тестируем получение проектов для пользователя с telegram_id=23
    response = await client.get("/projects/?telegram_id=23")
    assert response.status_code == 200, response.text
    data = response.json()
    
    # Проверяем, что вернулся один проект
    assert len(data) == 1
    
    # Проверяем содержимое проекта
    project = data[0]
    assert project["user_id"] == 23
    assert "Test Project" in project["name"]
    assert "id" in project
    assert "created_at" in project
