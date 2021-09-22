from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSON, ARRAY

from app.store.database.gino import db


@dataclass
class Theme:
    id: Optional[int]
    title: str


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Game:
    id: int
    theme_id: int
    # round: int
    completed: bool
    chat_id: int
    used_questions: List["Question"]


@dataclass
class PlayerScore:
    id: int
    game_id: int
    vk_id: int
    points: int


@dataclass
class Player:
    vk_id: int
    name: str
    last_name: str


class ThemeModel(db.Model):
    __tablename__ = "themes"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode(), unique=True, nullable=False)


class AnswerModel(db.Model):
    __tablename__ = "answers"

    text = db.Column(db.Unicode(), primary_key=True, nullable=False)
    question_id = db.Column(db.Integer(), db.ForeignKey('questions.id', ondelete="CASCADE"), nullable=False)
    is_correct = db.Column(db.Boolean(), nullable=False)


class QuestionModel(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Unicode(), unique=True, nullable=False)
    theme_id = db.Column(db.Integer(), db.ForeignKey('themes.id', ondelete="CASCADE"), nullable=False)

    def __init__(self, **kw):
        super().__init__(**kw)

        self._answers: List[AnswerModel] = list()

    @property
    def answers(self) -> List[AnswerModel]:
        return self._answers

    @answers.setter
    def answers(self, val: Optional[AnswerModel]):
        if val is not None:
            self._answers.append(val)

class GameModel(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer(), primary_key=True)
    theme_id = db.Column(db.Integer(), db.ForeignKey('themes.id'), nullable=False)
    completed = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer(), nullable=False)
    questions_id = db.Column(ARRAY(Integer), nullable=False)



class PlayerScoreModel(db.Model):
    __tablename__ = "players_scores"

    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer(), db.ForeignKey('games.id'), nullable=False)
    vk_id = db.Column(db.Integer(), db.ForeignKey('players.vk_id'), nullable=False)
    points = db.Column(db.Integer(), default=0)

class PlayerModel(db.Model):
    __tablename__ = "players"

    vk_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)





