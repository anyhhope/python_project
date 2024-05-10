from . import controller
from consumer import AIOConsumer
from config import cfg

def get_frame_consumer() -> AIOConsumer:
    return AIOConsumer(cfg, consume_topic=cfg.frames_topic)

async def consume_frames_to_ml():
    consumer: AIOConsumer = get_frame_consumer()
    await consumer.consume(controller.process)
    return