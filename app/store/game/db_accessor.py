from sqlalchemy import func
from sqlalchemy.orm import load_only

from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel, QuestionModel, ThemeModel
from app.store.database.gino import db


class GameDbAccessor(BaseAccessor):
    async def get_theme(self):
        theme = await ThemeModel.query.order_by(func.random()).gino.first()
        return theme

    async def create_game(self, user_id: str):
        theme = await self.get_theme()
        game = await GameModel.create(
            theme_id=theme.id,
            user_id=user_id,
            used_questions=[1, 2]
        )
        return game

    async def get_question(self, theme_id: int):
        question = await QuestionModel.query.where(QuestionModel.theme_id == theme_id).order_by(func.random()).gino.first()
        return question

    async def get_game(self, user_id: int):
        game = await GameModel.query.where(GameModel.user_id == user_id).gino.first()
        return game
