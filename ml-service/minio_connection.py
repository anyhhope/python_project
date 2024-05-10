from minio import Minio
from config import cfg

s3 = Minio(
    f"{cfg.minio_host}:{cfg.minio_port}",
    access_key=cfg.minio_access_key,
    secret_key=cfg.minio_secret_key,
    secure=False,
)

if not s3.bucket_exists(cfg.minio_bucket):
    s3.make_bucket(cfg.minio_bucket, "eu-west-1", True)