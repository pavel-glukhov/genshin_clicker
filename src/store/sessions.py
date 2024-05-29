from pathlib import Path


def is_session_exists(chat_id: int):
    session_path = Path(f'sessions\\{chat_id}.pkl')
    if session_path.exists():
        return True
    return False
