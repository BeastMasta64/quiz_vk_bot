import os
from unittest.mock import AsyncMock
import pytest
from aiohttp.test_utils import TestClient, loop_context

from app.store import Store
from app.web.app import setup_app
from app.web.config import Config
from app.store import Database
import sqlalchemy
import logging


@pytest.fixture(scope="session")
def loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def server():
    app = setup_app(
        config_path='C:/PycharmProjects/kts_project/config.yml')

    app.on_startup.clear()
    app.on_shutdown.clear()
    app.store.vk_api = AsyncMock()
    app.store.vk_api.send_message = AsyncMock()
    app.store.vk_api.get_user = AsyncMock()
    app.store.vk_api.get_Conversation_Members = AsyncMock()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)


    return app


@pytest.fixture
def store(server) -> Store:
    return server.store


# @pytest.fixture(autouse=True, scope="function")
# async def clear_db(server):
#     yield
#     db = server.database.db
#     for table in db.sorted_tables:
#         await db.status(db.text(f"TRUNCATE {table.name} CASCADE"))
#         try:
#             row = await db.status(
#                 db.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1")
#             )
#         except Exception:
#             pass


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture(autouse=True)
def cli(aiohttp_client, loop, server) -> TestClient:
    return loop.run_until_complete(aiohttp_client(server))



