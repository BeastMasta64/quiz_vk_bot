from unittest.mock import call

from pytest_mock import mocker

from app.store.vk_api.dataclasses import Update, UpdateObject, Message, UpdateMessage
import pytest


class TestGame3:
    async def test_no_game_no_go(self, store):
        await store.bots_manager.handle_updates(
            updates=[
                Update(
                    type='message_new',
                    object=UpdateObject(
                        message=UpdateMessage(
                            from_id=1,
                            peer_id=1,
                            id=1,
                            text='privet'
                        )

                    )
                )
            ]
        )
        assert store.vk_api.send_message.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0]
        assert message == call(message=Message(peer_id=1, text='а?'))

    async def test_no_game_but_go(self, store, mocker):
        await store.bots_manager.handle_updates(
            updates=[
                Update(
                    type='message_new',
                    object=UpdateObject(
                        message=UpdateMessage(
                            from_id=1,
                            peer_id=1,
                            id=1,
                            text='/go'
                        )

                    )
                )
            ]
        )
        def members(self):

            members = {'response': {
                'items': [
                    {'member_id': 1},
                    {'member_id': 2},
                    {'member_id': 3}
                ]
            }}
            return members

        mock_get_Conversation_Members = mocker.patch.object(store.vk_api, 'get_Conversation_Members', members)

        def mock_user(self, *args):
            response = {'response': [
                    {'first_name': str(*args),
                     'last_name': str(*args)
                     }

            ]}
            return response

        # mock_get_user = mocker.patch(store.vk_api, 'get_user', mock_user)

        assert store.vk_api.send_message.call_count == 2