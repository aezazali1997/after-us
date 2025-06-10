from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except Exception as e:
    config = Config()


DATABASE_URL = config("DATABASE_URL", cast=Secret)
