import random
from typing import Optional

from aiohttp import TCPConnector
from app.store.vk_api.dataclasses import Update, UpdateObject, Message, UpdateMessage

from app.store.vk_api.poller import Poller

from app.web.app import Application

from app.base.base_accessor import BaseAccessor
from aiohttp.client import ClientSession

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: 'Application', *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: 'Application'):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()

        except Exception as e:
            self.logger.error('Exception', exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info('start polling')
        await self.poller.start()
        # await self.app.store.vk_api.send_message(
        #     Message(
        #         text='Запущен!',
        #         user_id=int(self.app.config.bot.admin)
        #     )
        # )

    async def disconnect(self, app: 'Application'):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
                self._build_query(
                    host=API_PATH,
                    method="groups.getLongPollServer",
                    params={
                        "group_id": self.app.config.bot.group_id,
                        "access_token": self.app.config.bot.token,
                    },
                )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self):
        async with self.session.get(
                self._build_query(
                    host=self.server,
                    method="",
                    params={
                        "act": "a_check",
                        "key": self.key,
                        "ts": self.ts,
                        "wait": 10,
                    },
                )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])
            updates = []
            for update in raw_updates:
                updates.append(
                    Update(
                        type=update["type"],
                        object=UpdateObject(
                            message=UpdateMessage(
                                from_id=update['object']['message']['from_id'],
                                id=update["object"]['message']["id"],
                                text=update["object"]['message']['text'],
                                peer_id=update["object"]['message']['peer_id']
                            )),
                    )
                )
        # await self.app.store.bots_manager.handle_updates(updates)
        return updates

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
                self._build_query(
                    host=API_PATH,
                    method="messages.send",
                    params={
                        "peer_id": message.peer_id,
                        "random_id": random.randint(1, 2 ** 32),
                        "message": message.text,
                        "access_token": self.app.config.bot.token,
                    },
                )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_user(self, id: int):
        async with self.session.get(
                self._build_query(
                    host=API_PATH,
                    method='users.get',
                    params={
                        'user_ids': id,
                        'name_case': 'nom',
                        "access_token": self.app.config.bot.token
                    }
                )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
        return data

    async def get_Conversation_Members(self, peer_id):
        async with self.session.get(
                self._build_query(
                    host=API_PATH,
                    method='messages.getConversationMembers',
                    params={
                        'peer_id': peer_id,
                        'group_id': self.app.config.bot.group_id,
                        "access_token": self.app.config.bot.token
                    }
                )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
        return data
