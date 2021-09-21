from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel
from app.store.vk_api.dataclasses import Message


class GameLogicAccessor(BaseAccessor):
    async def start_game(self, user_id: int):
        game = await self.app.store.game_db_accessor.create_game(user_id=user_id)
        await self.ask_question(game)

    async def ask_question(self, game: GameModel):
        theme_id = game.theme_id
        question = await self.app.store.game_db_accessor.get_question(theme_id=theme_id)
        question_text = question.text
        user_id = game.user_id
        await self.app.store.vk_api.send_message(
            message=Message(
                user_id=user_id,
                text=question_text
            )
        )

    async def check_answer(self, game: GameModel, text: str):
        pass
