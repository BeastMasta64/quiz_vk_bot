

from app.store.database.database import Database
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: 'Application'):
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.bot.manager import BotManager
        from app.store.game.db_accessor import GameDbAccessor
        from app.store.game.game_logic import GameLogicAccessor

        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)
        self.game_db_accessor = GameDbAccessor(app)
        self.game_logic_accessor = GameLogicAccessor(app)

def setup_store(app: 'Application'):
    app.database = Database(app)
    app.store = Store(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)