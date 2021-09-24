from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    peer_id: int
    text: str



@dataclass
class UpdateMessage:
    from_id: int
    peer_id: int
    text: str
    id: int



@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject

