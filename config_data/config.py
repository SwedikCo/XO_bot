from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str

@dataclass
class DB:
    dbname: str
    user: str
    password: str
    host: str

@dataclass
class Config:
    tg_bot: TgBot
    tg_db: DB 

def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                    tg_db=DB(dbname=env('DB_NAME'), 
                                user=env('DB_USER'), 
                                password=env('DB_PASS'), 
                                host=env('DB_HOST')))
