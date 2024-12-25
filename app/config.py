from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='allow')

    BOT_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    PACK_PATH: str
    RESULT_PATH: str

    def dsn(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


config = Config()
