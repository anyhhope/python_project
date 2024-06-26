from aiokafka import AIOKafkaProducer
from config import Config, cfg
import json

def serializer(value):
    return json.dumps(value).encode(encoding="utf-8")

class AIOProducer():

    def __init__(self,  cfg: Config, produce_topic: str):
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=f'{cfg.kafka_host}:{cfg.kafka_port}',
            value_serializer=serializer,
            compression_type="gzip"
        )
        self.__produce_topic = produce_topic

    async def start(self) -> None:
        await self.__producer.start()

    async def stop(self) -> None:
        await self.__producer.stop()

    async def send(self, value) -> None:
        await self.start()
        try:
            await self.__producer.send(
                topic=self.__produce_topic,
                value=value,
            )
        finally:
            await self.stop()


def get_query_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.query_topic)

def get_state_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.state_topic)