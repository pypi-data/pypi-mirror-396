from redis.asyncio import Redis
from tp_helper.base_queues.base_stream_queue_repo import BaseStreamQueueRepo

from tp_shared.telegram_hub.schemas.telegram_hub_schemas import (
    TelegramHubChatMessageResultMessage,
)
from tp_shared.telegram_hub.types.telegram_hub_types import SystemType


class TelegramHubChatMessagesResultStreamQueueRepo(BaseStreamQueueRepo):
    QUEUE_NAME = "telegram:hub:chat:messages:results"

    def __init__(self, redis_client: Redis, system_type: SystemType | None = None):
        queue_name = self.QUEUE_NAME
        if system_type is not None:
            queue_name += f":{system_type}"
        super().__init__(
            redis_client=redis_client,
            schema=TelegramHubChatMessageResultMessage,
            queue_name=queue_name,
        )
