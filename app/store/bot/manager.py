import datetime
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

            game = await self.app.store.game_db_accessor.get_game(peer_id=update.object.message.peer_id)
            if game:
                if text == '/s':
                    await self.app.store.game_logic_accessor.end_game(game=game)
                if text == '/g':
                    await self.app.store.vk_api.send_message(message=Message(
                        peer_id=update.object.message.peer_id,
                        text='Игра уже создана!\n'
                             'Напишите /s, чтобы остановить игру.\n\n'
                             'Итак, мой вопрос:'
                    ))
                    await self.app.store.game_logic_accessor.ask_question(game=game, new=False)
                else:
                    correct = await self.app.store.game_logic_accessor.check_answer(game=game, vk_text=text)
                    if correct:
                        await self.app.store.game_db_accessor.add_points(vk_id=update.object.message.from_id,
                                                                         game=game)
                        await self.app.store.vk_api.send_message(message=Message(
                            peer_id=update.object.message.peer_id,
                            text='Правильно!'
                        ))
                        if game.questions_remain:
                            await self.app.store.game_db_accessor.set_new_question(game=game)
                            game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
                            await self.app.store.game_logic_accessor.ask_question(game=game, new=False)
                        else:
                            game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
                            await self.app.store.game_logic_accessor.end_game(game=game)

            elif not game and text == '/g':
                await self.app.store.game_logic_accessor.start_game(update.object.message.peer_id)
            else:
                await self.app.store.vk_api.send_message(message=Message(
                    peer_id=update.object.message.peer_id,
                    text='а?'
                ))
