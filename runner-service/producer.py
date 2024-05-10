from aiokafka import AIOKafkaProducer
from config import Config, cfg
import asyncio
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
        self.is_started = False

    async def start(self) -> None:
        await self.__producer.start()
        print("Producer started")

    async def stop(self) -> None:
        await self.__producer.stop()
        print("Producer stopped")

    async def send(self, value, topic=None) -> None:
        if not self.is_started:
            await self.start()
            self.is_started = True

        if topic:
            await self.__producer.send(
                topic=topic,
                value=value,
            )
        else:
            print('here')
            await self.__producer.send(
                topic=self.__produce_topic,
                value=value,
            )



def get_frame_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.frames_topic)



def get_state_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.state_topic)


async def produce(producer: AIOProducer, message_to_produce, topic=None):
    try:
        if topic:
            await producer.send(value=message_to_produce, topic=topic)
            print(f"Produced {topic}")
        else:
            print(f"Produced")
            await producer.send(value=message_to_produce)
    except Exception as e:
        print(f"An error occurred: {e}")