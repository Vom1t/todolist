

from datetime import datetime

from pydantic import BaseModel, Field


class Chat(BaseModel):
    """Модель чата """

    id: str
    first_name: str
    type: str


class MessageFrom(BaseModel):
    """Модель пользователя """

    id: int
    is_bot: bool
    username: str | None
    first_name: str | None


class Message(BaseModel):
    """Модель сообщения"""

    message_id: int
    from_: MessageFrom | None = Field(..., alias='from')
    chat: Chat
    date: datetime
    text: str | None

    class Config:
        # чтобы использовать alias вместо имени поля
        allow_population_by_field_name = True


class MessageInfo(BaseModel):
    """Модель бота полученных сообщений"""

    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):
    """Модель бота для получения сообщений"""

    ok: bool
    result: list[MessageInfo]


class SendMessageResponse(BaseModel):
    """Модель бота для отправки сообщений"""

    ok: bool
    result: Message
