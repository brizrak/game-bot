from pydantic_settings import BaseSettings, SettingsConfigDict
from environs import Env
from dataclasses import dataclass

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='allow')

const_path = "C:\\Users\\Admin\\PycharmProjects\\game-bot\\app\\колода52"
const_path1 = "C:\\Users\\Admin\\PycharmProjects\\game-bot\\app\\users_result"
@dataclass
class Config:
    BOT_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    def dsn(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


config = Config()
