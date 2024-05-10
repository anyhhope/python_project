from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    logging_level: str = "info"

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str


    kafka_host: str
    kafka_port: int
    query_topic: str
    frames_topic: str
    state_topic: str

    ml_model_path: str

    minio_host: str
    minio_port: int
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str

    @property
    def build_postgres_dsn(self) -> str:
        res = (
            "postgresql://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return res


cfg = Config()  