from redis.asyncio import Redis
from tp_helper.base_queues.base_stream_queue_repo import BaseStreamQueueRepo

from tp_shared.nsis_service.schemas.nsis_result_message import (
    NsisResultMessage,
)


class NsisResultsStreamQueueRepo(BaseStreamQueueRepo):
    QUEUE_NAME = "nsis:service:results:stream"

    def __init__(self, redis_client: Redis):
        super().__init__(
            redis_client, schema=NsisResultMessage, queue_name=self.QUEUE_NAME
        )
