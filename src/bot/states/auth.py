from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    username = State()
    password = State()
