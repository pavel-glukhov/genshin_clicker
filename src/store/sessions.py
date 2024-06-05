from pathlib import Path

from src.config import load_config


def is_session_exists(chat_id: int) -> bool:
    session_path = Path(f'{load_config().sessions_folder}\\{chat_id}.pkl')
    if session_path.exists():
        return True
    return False
