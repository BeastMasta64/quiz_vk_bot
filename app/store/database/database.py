import typing
from typing import Optional

import gino
from app.store.database.gino import db
from sqlalchemy.engine.url import URL

if typing.TYPE_CHECKING:
    from app.web.app import Application
from gino import Gino


class Database:
    db: Gino

    def __init__(self, app: 'Application'):
        self.app = app
        self.db: Optional[Gino] = None
        app.on_startup.append(self.connect)

    async def connect(self, *_, **kwargs):
        self._engine = await gino.create_engine(
            URL(
                drivername='asyncpg',
                host=self.app.config.database.host,
                database=self.app.config.database.database,
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                port=self.app.config.database.port
            ),
            min_size=1,
            max_size=1
        )
        self.db = db
        self.db.bind = self._engine

    async def disconnect(self, *_, **kwargs):
        pass
