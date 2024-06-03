import os
from dataclasses import dataclass

from dotenv import load_dotenv

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(ROOT_PATH, '.env')
load_dotenv(dotenv_path)


@dataclass
class Config:
    token: str
    sessions_folder: str


def load_config():
    return Config(
        token=os.getenv('TELEGRAM_TOKEN'),
        sessions_folder=os.path.join(ROOT_PATH, 'sessions')
    )
