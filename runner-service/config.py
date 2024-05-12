from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    logging_level: str = "info"

    kafka_host: str
    kafka_port: int
    query_topic: str
    frames_topic: str
    state_topic: str


cfg = Config()  