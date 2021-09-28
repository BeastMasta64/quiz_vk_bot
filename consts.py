from app.game.models import GameModel


def lets_start_text(theme: str) -> str:
    text = 'Начнем пожалуй!<br>' \
           'Выбираю тему...<br>' \
           f'Тема: {theme}.'
    return text


QUESTION_QUANTITY = 6


def ask_question_text(game: GameModel) -> str:
    question = QUESTION_QUANTITY - len(game.questions_remain)

    text = f'Вопрос {question}/6<br>' \
           f'{game.question.text}<br><br>'

    for i, answer in enumerate(game.question.answers):
        text += f'{i + 1}) {answer.text}<br>'

    return text


def end_question_text(game: GameModel) -> str:
    winners = game.return_winners()
    winners_str = ''
    for winner in winners:
        winners_str += f'{winner.name} {winner.last_name}, '
    text = 'Поздравляем победителей!<br><br>' + winners_str[:-2] + f' - {winners[0].points} баллов!'
    return text


POINTS_FOR_CORRECT = 10

GAME_EXISTS = 'Игра уже создана!<br>' \
              'Напишите /s, чтобы остановить игру.<br>' \
              'Итак, мой вопрос:'

CORRECT = 'Правильно!'

WHAT = 'а?'