from typing import Optional

from aiohttp.web import Application as AiohttpApplication

from app.web.logger import setup_logging

from app.store.database.database import Database

from app.store import Store, setup_store
from aiohttp_apispec import setup_aiohttp_apispec

from app.web.config import Config, setup_config
from app.web.middlewares import setup_middlewares


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None

app = Application()

def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path=config_path)
    setup_aiohttp_apispec(
        app, title="Vk Quiz Bot", url="/docs/json", swagger_path="/docs"
    )
    setup_store(app)
    setup_middlewares(app)
    return app
