from .schema import MessageConsume
from producer import AIOProducer
from config import cfg


def get_query_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.query_topic)

async def process(message_consumed: MessageConsume):
    print(f"Message {message_consumed} consumed")
    return 