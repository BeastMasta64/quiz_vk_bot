from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message
from app.web.app import Application
from consts import GAME_EXISTS, WHAT


class BotManager:
    def __init__(self, app: 'Application'):
        self.app = app
        self.bot = None
        self.logger = getLogger('handler')

    async def handle_updates(self, updates: list[Update]):
        for update in updates:

            text = update.object.message.text

            game = await self.app.store.game_db_accessor.get_game(peer_id=update.object.message.peer_id)
            if game:
                if text == '/s':
                    await self.app.store.game_logic_accessor.end_game(game=game)
                elif text == '/g':
                    await self.app.store.vk_api.send_message(message=Message(
                        peer_id=update.object.message.peer_id,
                        text=GAME_EXISTS
                    ))
                    await self.app.store.game_logic_accessor.ask_question(game=game, new=False)
                else:
                    correct = await self.app.store.game_logic_accessor.check_answer(game=game, vk_text=text)
                    if correct:
                        await self.app.store.game_logic_accessor.if_answer_is_correct(game=game, update=update)

            elif not game and text == '/g':
                await self.app.store.game_logic_accessor.start_game(update.object.message.peer_id)
            else:
                await self.app.store.vk_api.send_message(message=Message(
                    peer_id=update.object.message.peer_id,
                    text=WHAT
                ))
