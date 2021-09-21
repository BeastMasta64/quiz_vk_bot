from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message
from app.web.app import Application


class BotManager:
    def __init__(self, app: 'Application'):
        self.app = app
        self.bot = None
        self.logger = getLogger('handler')

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            text = update.object.message.text
            user_id = update.object.message.from_id
            if text == '/game':
                await self.app.store.game_logic_accessor.start_game(user_id=user_id)

            else:
                game = await self.app.store.game_db_accessor.get_game(user_id=user_id)
                if game:
                    await self.app.store.game_logic_accessor.check_answer(game=game, text=text)
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            text=update.object.message.text,
                            user_id=update.object.message.from_id
                        )
                    )
