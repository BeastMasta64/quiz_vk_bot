import datetime
from typing import List

from asyncpg import UniqueViolationError
from sqlalchemy import func, and_

from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel, QuestionModel, ThemeModel, AnswerModel, PlayerScoreModel, PlayerModel


class GameDbAccessor(BaseAccessor):
    async def get_theme(self) -> ThemeModel:
        theme = await ThemeModel.query.order_by(func.random()).gino.first()
        return theme

    async def get_questions(self, theme: ThemeModel) -> List[QuestionModel]:
        questions = await QuestionModel.query.where(QuestionModel.theme_id == theme.id).order_by(
            func.random()).limit(6).gino.all()
        return questions

    async def create_game(self, peer_id: int) -> GameModel:
        theme = await self.get_theme()
        questions = await self.get_questions(theme=theme)

        questions_id = [q.id for q in questions]

        game = await GameModel.create(
            theme_id=theme.id,
            peer_id=peer_id,
            asked_question=questions_id.pop(),
            questions_remain=questions_id
        )

        return game

    async def get_game(self, peer_id: int) -> GameModel:
        game = await (
            GameModel.outerjoin(QuestionModel, GameModel.asked_question == QuestionModel.id)
                .outerjoin(PlayerScoreModel, GameModel.id == PlayerScoreModel.game_id)
                .outerjoin(AnswerModel, QuestionModel.id == AnswerModel.question_id)
                .outerjoin(PlayerModel, PlayerScoreModel.vk_id == PlayerModel.vk_id)
                .select()
                .where(and_(GameModel.peer_id == peer_id, GameModel.expire_date > datetime.datetime.now()))
                .gino
                .load(GameModel.distinct(GameModel.id)
                      .load(question=QuestionModel.load(answers=AnswerModel))
                      .load(player_scores=PlayerScoreModel.load(player=PlayerModel))
                      )
                .all()
        )
        if game:
            return game[0]
        return game

    async def add_points(self, vk_id: int, game: GameModel):
        points_for_correct = 10
        await PlayerScoreModel.update.values(points=PlayerScoreModel.points + points_for_correct).where(
            and_(PlayerScoreModel.vk_id == vk_id, PlayerScoreModel.game_id == game.id)).gino.status()

    async def add_players(self, members_data) -> List[PlayerModel]:
        members = members_data['response']['items']
        members_ids = [member['member_id'] for member in members]
        players = []
        for member_id in members_ids:
            if member_id < 0:
                pass
            else:
                vk_user = await self.app.store.vk_api.get_user(member_id)

                try:
                    player = await PlayerModel.create(
                        vk_id=member_id,
                        name=vk_user['response'][0]['first_name'],
                        last_name=vk_user['response'][0]['last_name']
                    )
                except UniqueViolationError:
                    player = await PlayerModel.query.where(PlayerModel.vk_id == member_id).gino.first()
                players.append(player)
        return players

    async def add_playerscores(self, players: List[PlayerModel], game: GameModel):
        for player in players:
            await PlayerScoreModel.create(
                game_id=game.id,
                vk_id=player.vk_id
            )

    async def set_new_question(self, game: GameModel):
        questions_remain = game.questions_remain
        new_question = questions_remain.pop()
        await game.update(asked_question=new_question, questions_remain=questions_remain).apply()

    async def end_game(self, game: GameModel):
        await game.update(expire_date=datetime.datetime.now()).apply()
