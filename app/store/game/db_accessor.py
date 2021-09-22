from sqlalchemy import func, and_
from sqlalchemy.orm import load_only

from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel, QuestionModel, ThemeModel, AnswerModel, PlayerScoreModel, PlayerModel
from app.store.database.gino import db


class GameDbAccessor(BaseAccessor):
    async def get_theme(self):
        theme = await ThemeModel.query.order_by(func.random()).gino.first()
        return theme

    async def create_game(self, user_id: str):
        theme = await self.get_theme()
        questions = await QuestionModel.query.where(QuestionModel.theme_id == theme.id).order_by(
            func.random()).gino.all()
        questions_id = []

        for question in questions:
            questions_id.append(question.id)

        game = await GameModel.create(
            theme_id=theme.id,
            user_id=user_id,
            questions_id=questions_id

        )

        return game

    async def get_next_question(self, game: GameModel):
        questions_id = game.questions_id
        if not questions_id:
            return None
        question_id = questions_id.pop()
        question = await QuestionModel.query.where(
            QuestionModel.id == question_id).gino.first()
        print(f'get next {question_id}')
        return question

    async def get_game(self, user_id: int):
        game = await GameModel.query.where(and_(GameModel.user_id == user_id, GameModel.completed == False)).gino.first()
        print(game)
        return game

    async def get_answer(self, question_id):
        answer = await AnswerModel.query.where(
            and_(AnswerModel.question_id == question_id, AnswerModel.is_correct == True)).gino.first()
        return answer

    async def add_points(self, vk_id, game_id):
        print(f'add points {vk_id} {game_id}')
        await PlayerScoreModel.update.values(points=PlayerScoreModel.points + 10).where(
            and_(PlayerScoreModel.vk_id == vk_id, PlayerScoreModel.game_id == game_id)).gino.status()

    async def add_player(self, vk_id, game_id):
        player = await PlayerModel.query.where(PlayerModel.vk_id == vk_id).gino.first()
        if not player:
            vk_user = await self.app.store.vk_api.get_user(vk_id)
            print(vk_user)
            name = vk_user['response'][0]['first_name']
            last_name = vk_user['response'][0]['last_name']
            await PlayerModel.create(
                vk_id=vk_id,
                name=name,
                last_name=last_name
            )
        await PlayerScoreModel.create(
            game_id=game_id,
            vk_id=vk_id
        )

    async def get_winner(self, game_id):
        winner = await PlayerScoreModel.select('points').where(PlayerScoreModel.game_id == game_id).gino.scalar()
        return winner
