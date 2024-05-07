from . import controller
from .consumer import AIOConsumer
from config import cfg

def get_runner_consumer() -> AIOConsumer:
    return AIOConsumer(cfg, consume_topic=cfg.query_topic)

def get_state_consumer() -> AIOConsumer:
    return AIOConsumer(cfg, consume_topic=cfg.state_topic)

async def preprocess():
    consumer_runner: AIOConsumer = get_runner_consumer()
    # consumer_state: AIOConsumer = get_state_consumer()
    await consumer_runner.consume() 
    return