import uuid

from tp_helper.base_items.base_schema import BaseSchema

from tp_shared.telegram_hub.types.telegram_hub_types import ChatMessageErrorType


class AccountResultMessage(BaseSchema):
    user_id: int
    username: str | None
    first_name: str | None = None
    last_name: str | None = None


class ChatMessageResultMessage(BaseSchema):
    account: AccountResultMessage | None = None
    message_id: int
    notification_id: uuid.UUID
    user_id: int | None = None
    member_id: uuid.UUID | None = None
    sent_at: int
    error_type: ChatMessageErrorType | None = None
    error_message: str | None = None
