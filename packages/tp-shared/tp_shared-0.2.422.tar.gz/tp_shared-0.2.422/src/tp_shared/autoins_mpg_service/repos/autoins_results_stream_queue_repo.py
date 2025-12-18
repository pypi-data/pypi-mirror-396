from redis.asyncio import Redis
from tp_helper.base_queues.base_stream_queue_repo import BaseStreamQueueRepo

# from src.config import config
from tp_shared.autoins_mpg_service.schemas.autoins_result_message import (
    AutoinsResultMessage,
)


class AutoinsResultsStreamQueueRepo(BaseStreamQueueRepo):
    QUEUE_NAME = "autoins:service:results:stream"

    def __init__(self, redis_client: Redis):
        super().__init__(
            redis_client=redis_client,
            schema=AutoinsResultMessage,
            queue_name=self.QUEUE_NAME,
        )
