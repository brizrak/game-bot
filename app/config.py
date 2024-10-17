from environs import Env
from dataclasses import dataclass


@dataclass
class Config:
    BOT_TOKEN: str


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        BOT_TOKEN=env.str("BOT_TOKEN"),
    )
