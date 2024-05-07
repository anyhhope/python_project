from . import controller
from .consumer import AIOConsumer
from config import cfg
import asyncio

def get_runner_consumer() -> AIOConsumer:
    return AIOConsumer(cfg, consume_topic=cfg.query_topic)

async def preprocess():
    consumer_runner: AIOConsumer = get_runner_consumer()
    
    await asyncio.gather(
        consumer_runner.consume(),
        controller.consume_shutdown()
    )