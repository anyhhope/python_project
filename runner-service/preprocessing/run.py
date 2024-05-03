from . import controller
from consumer import AIOConsumer
from config import cfg

def get_runner_consumer() -> AIOConsumer:
    return AIOConsumer(cfg, consume_topic=cfg.query_topic)

async def preprocess():
    consumer: AIOConsumer = get_runner_consumer()
    await consumer.consume(controller.process)
    return