from app.base.base_accessor import BaseAccessor
from app.game.models import GameModel
from app.store.vk_api.dataclasses import Message, Update
from consts import lets_start_text, ask_question_text, end_question_text, CORRECT


class GameLogicAccessor(BaseAccessor):
    async def start_game(self, peer_id: int):
        game = await self.app.store.game_db_accessor.create_game(peer_id=peer_id)
        members_data = await self.app.store.vk_api.get_Conversation_Members(peer_id=peer_id)
        players = await self.app.store.game_db_accessor.add_players(members_data=members_data)
        await self.app.store.game_db_accessor.add_playerscores(players=players, game=game)

        game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
        await self.app.store.vk_api.send_message(message=Message(
            text=lets_start_text(theme=game.theme.title),
            peer_id=game.peer_id
        ))

        await self.ask_question(game, new=True)

    async def ask_question(self, game: GameModel, new: bool):
        if new:
            game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
        await self.app.store.vk_api.send_message(
            message=Message(
                peer_id=game.peer_id,
                text=ask_question_text(game=game)
            )
        )

    async def check_answer(self, game: GameModel, vk_text: str) -> bool:
        if vk_text.isdigit():
            answer_n = int(vk_text)
            return game.question.is_answer_right(answer_n=answer_n)
        return False

    async def if_answer_is_correct(self, game: GameModel, update: Update):
        await self.app.store.game_db_accessor.add_points(vk_id=update.object.message.from_id,
                                                         game=game)
        await self.app.store.vk_api.send_message(message=Message(
            peer_id=update.object.message.peer_id,
            text=CORRECT
        ))
        if game.questions_remain:
            await self.app.store.game_db_accessor.set_new_question(game=game)
            game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
            await self.app.store.game_logic_accessor.ask_question(game=game, new=False)
        else:
            game = await self.app.store.game_db_accessor.get_game(peer_id=game.peer_id)
            await self.app.store.game_logic_accessor.end_game(game=game)

    async def end_game(self, game: GameModel):

        await self.app.store.vk_api.send_message(
            message=Message(
                text=end_question_text(game=game),
                peer_id=game.peer_id
            )
        )
        await self.app.store.game_db_accessor.end_game(game=game)
