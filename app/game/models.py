import datetime
from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY

from app.store.database.gino import db


@dataclass
class Winner:
    vk_id: int
    game_id: int
    points: int
    name: str
    last_name: str


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
class _Game:
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
class _Player:
    vk_id: int
    name: str
    last_name: str


class ThemeModel(db.Model):
    __tablename__ = "themes"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode(), unique=True, nullable=False)


class AnswerModel(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Unicode(), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    question_id = db.Column(db.Integer(), db.ForeignKey('questions.id', ondelete="CASCADE"), nullable=False)


class QuestionModel(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Unicode(), unique=True, nullable=False)
    theme_id = db.Column(db.Integer(), db.ForeignKey('themes.id', ondelete="CASCADE"), nullable=False)

    def __init__(self, **kw):
        super().__init__(**kw)

        self._answers: List[AnswerModel] = list()

    def is_answer_right(self, answer_n: int) -> bool:
        if self._answers[answer_n - 1].correct:
            return True
        return False

    @property
    def answers(self) -> List[AnswerModel]:
        return self._answers

    @answers.setter
    def answers(self, val: Optional[AnswerModel]):
        if val is not None:
            self._answers.append(val)


class PlayerModel(db.Model):
    __tablename__ = "players"

    vk_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)


class PlayerScoreModel(db.Model):
    __tablename__ = "players_scores"

    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer(), db.ForeignKey('games.id', ondelete="CASCADE"), nullable=False)
    vk_id = db.Column(db.Integer(), db.ForeignKey('players.vk_id', ondelete="CASCADE"), nullable=False)
    points = db.Column(db.Integer(), default=0)

    def __init__(self, **kw):
        super().__init__(**kw)

        self._player: Optional[PlayerModel] = None

    @property
    def player(self) -> Optional[PlayerModel]:
        return self._player

    @player.setter
    def player(self, val):
        if val is not None:
            self._player = val


class GameModel(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer(), primary_key=True)
    theme_id = db.Column(db.Integer(), db.ForeignKey('themes.id', ondelete="CASCADE"), nullable=False)
    expire_date = db.Column(db.DateTime(), default=datetime.datetime.now() + datetime.timedelta(hours=10))
    peer_id = db.Column(db.Integer(), nullable=False)
    asked_question = db.Column(db.Integer(), db.ForeignKey('questions.id'), nullable=False)
    questions_remain = db.Column(ARRAY(Integer), nullable=False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._theme: Optional[ThemeModel] = None
        self._player_scores: List[PlayerScoreModel] = list()
        self.scores_id: List[int] = list()
        self._question: Optional[QuestionModel] = None

    def return_winners(self) -> List[Winner]:
        scores = [score.points for score in self._player_scores]
        try:
            max_points = max(scores)
        except:
            max_points = 0
        winners = []
        for playerscore in self._player_scores:
            if playerscore.points == max_points:
                winners.append(Winner(
                    vk_id=playerscore.vk_id,
                    game_id=self.id,
                    points=max_points,
                    name=playerscore._player.name,
                    last_name=playerscore._player.last_name
                ))

        return winners

    @property
    def player_scores(self) -> List[PlayerScoreModel]:
        return self._player_scores

    @player_scores.setter
    def player_scores(self, val: Optional[PlayerScoreModel]):
        if val.id not in self.scores_id and val is not None:
            self.scores_id.append(val.id)
            self._player_scores.append(val)

    @property
    def theme(self) -> Optional[ThemeModel]:
        return self._theme

    @theme.setter
    def theme(self, val):
        if val is not None:
            self._theme = val

    @property
    def question(self) -> Optional[QuestionModel]:
        return self._question

    @question.setter
    def question(self, val):
        if val is not None:
            self._question = val
