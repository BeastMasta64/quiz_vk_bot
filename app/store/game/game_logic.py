from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel, QuestionModel
from app.store.vk_api.dataclasses import Message


class GameLogicAccessor(BaseAccessor):
    async def start_game(self, user_id: int):
        game = await self.app.store.game_db_accessor.get_game(user_id=user_id)
        if game:
            await game.update(completed=True).apply()
        game = await self.app.store.game_db_accessor.create_game(user_id=user_id)
        await self.app.store.game_db_accessor.add_player(vk_id=user_id, game_id=game.id)
        await self.ask_question(game)

    async def ask_question(self, game: GameModel):

        question = await self.app.store.game_db_accessor.get_next_question(game)
        if not question:
            await self.app.store.game_logic_accessor.end_game(game=game)
        question_text = question.text
        user_id = game.user_id
        await self.app.store.vk_api.send_message(
            message=Message(
                user_id=user_id,
                text=question_text
            )
        )

    async def check_answer(self, game: GameModel, text: str, vk_id: int):
        questions_id = game.questions_id
        question_id = questions_id.pop()
        answer = await self.app.store.game_db_accessor.get_answer(question_id)
        print(answer)
        print(text, type(text))
        print(answer.text, type(answer.text))

        if text == answer.text:
            print('ok')
            await game.update(questions_id=questions_id).apply()
            await self.app.store.game_db_accessor.add_points(vk_id=vk_id, game_id=game.id)
            return True
        return False


    async def end_game(self, game: GameModel):
        winner = await self.app.store.game_db_accessor.get_winner(game_id=game.id)
        await self.app.store.vk_api.send_message(
            message=Message(
                text=winner,
                user_id=game.user_id
            )
        )

