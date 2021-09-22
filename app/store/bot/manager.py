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
            if text == '/t':
                data = await self.app.store.vk_api.get_user(user_id)
                print(data)
                print(type(data))
            if text == '/g':
                await self.app.store.game_logic_accessor.start_game(user_id=user_id)
            else:
                print('else')
                print(type(user_id))
                game = await self.app.store.game_db_accessor.get_game(user_id=user_id)
                print(f'game {game}\n'
                      f'{game.id}')
                if game:
                    correct_guess = await self.app.store.game_logic_accessor.check_answer(game=game, text=text, vk_id=user_id)
                    if correct_guess:
                        await self.app.store.game_logic_accessor.ask_question(game)
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            text=update.object.message.text,
                            user_id=update.object.message.from_id
                        )
                    )
