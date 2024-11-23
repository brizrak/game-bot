from environs import Env
from dataclasses import dataclass


const_path = "C:\\Users\\Admin\\PycharmProjects\\game-bot\\app\\колода52"
const_path1 = "C:\\Users\\Admin\\PycharmProjects\\game-bot\\app\\users_result"
@dataclass
class Config:
    BOT_TOKEN: str


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        BOT_TOKEN=env.str("BOT_TOKEN"),
    )
