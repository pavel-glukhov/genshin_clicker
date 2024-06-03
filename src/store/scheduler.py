import datetime
from random import randint
from typing import Callable

from aiogram.types import Message
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.config import load_config
JOB_STORES = {
    'default': SQLAlchemyJobStore(url=f'sqlite:///{load_config().sessions_folder}\\jobs.sqlite')
}

scheduler = AsyncIOScheduler(
    jobstores=JOB_STORES,
)


# TODO убрать chat_id
def create_task(chat_id: int | str,task_func: Callable) -> None:
    hour, minute, second = random_time()
    scheduler.add_job(task_func,
                      'cron',
                      hour=hour,
                      minute=minute,
                      id=str(chat_id),
                      args=[chat_id],
                      misfire_grace_time=18000)


def update_task(chat_id: int | str, trigger_kwargs) -> None:
    scheduler.reschedule_job(job_id=str(chat_id),
                             **trigger_kwargs)


def random_time(hour_from: int = 00,
                hour_to: int = 23,
                minutes_from: int = 0,
                minutes_to: int = 59,
                seconds_from: int = 0,
                seconds_to: int = 59,
                ) -> tuple[int, int, int]:
    random_hour = randint(hour_from, hour_to)
    random_minute = randint(minutes_from, minutes_to)
    random_second = randint(seconds_from, seconds_to)
    return random_hour, random_minute, random_second


def random_datetime() -> datetime:
    current_datetime = datetime.datetime.now()
    random_hour, random_minute, random_second = random_time(hour_from=current_datetime.time().hour)
    random_time_obj = datetime.time(random_hour, random_minute, random_second)
    result = datetime.datetime.combine(current_datetime.date(), random_time_obj)
    return result
