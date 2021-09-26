from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel
from app.store.vk_api.dataclasses import Message


class GameLogicAccessor(BaseAccessor):
    async def start_game(self, peer_id: int):
        game = await self.app.store.game_db_accessor.create_game(peer_id=peer_id)
        members_data = await self.app.store.vk_api.get_Conversation_Members(peer_id=peer_id)

        players = await self.app.store.game_db_accessor.add_players(members_data=members_data)
        await self.app.store.game_db_accessor.add_playerscores(players=players, game=game)
        await self.ask_question(game, new=True)

    async def ask_question(self, game: GameModel, new: bool):
        if new:
            game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
        text = f'''{game.question.text}<br><br>
        
        1) {game.question.answers[0].text}<br>
        2) {game.question.answers[1].text}<br>
        3) {game.question.answers[2].text}<br>
        4) {game.question.answers[3].text}
'''
        await self.app.store.vk_api.send_message(
            message=Message(
                peer_id=game.peer_id,
                text=text
            )
        )

    async def check_answer(self, game: GameModel, vk_text: str) -> bool:
        answer = game.question.get_right_answer()
        if vk_text == str(answer.id - 4 * (game.question.id - 1)):
            return True
        return False

    async def end_game(self, game: GameModel):
        winners = game.return_winners()
        winners_str = ''
        for winner in winners:
            winners_str += f'{winner.name} {winner.last_name}, '
        text = 'Поздравляем победителей! <br><br>' + winners_str[:-2] + f' - {winners[0].points} баллов!'
        await self.app.store.vk_api.send_message(
            message=Message(
                text=text,
                peer_id=game.peer_id
            )
        )
        await self.app.store.game_db_accessor.end_game(game=game)
