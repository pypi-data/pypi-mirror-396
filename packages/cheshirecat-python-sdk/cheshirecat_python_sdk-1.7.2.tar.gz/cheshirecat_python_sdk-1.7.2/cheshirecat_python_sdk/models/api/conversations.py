from typing import List
from pydantic import BaseModel

from cheshirecat_python_sdk.models.api.nested.memories import ConversationMessage


class ConversationDeleteOutput(BaseModel):
    deleted: bool


class ConversationHistoryOutput(BaseModel):
    history: List[ConversationMessage]


class ConversationsResponse(BaseModel):
    chat_id: str
    name: str
    num_messages: int


class ConversationNameChangeOutput(BaseModel):
    changed: bool