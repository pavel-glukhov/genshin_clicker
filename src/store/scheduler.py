import datetime
from random import randint
from typing import Callable
from datetime import datetime, timedelta
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import load_config

JOB_STORES = {
    'default': SQLAlchemyJobStore(url=f'sqlite:///{load_config().sessions_folder}\\jobs.sqlite')
}

scheduler = AsyncIOScheduler(
    jobstores=JOB_STORES,
)


def create_task(
        chat_id: int | str,
        task_func: Callable,
        hours_random_range: tuple[int, int] = (0, 2),
        minutes_random_range: tuple[int, int] = (0, 59),
        seconds_random_range: tuple[int, int] = (0, 59)
) -> None:
    """
    Creates a task to run in 24 hours with a random offset.

    :param chat_id: chat id (used as the job id)
    :param task_func: the function to be executed
    :param hours_random_range: range of random hour offset (e.g., (0, 2))
    :param minutes_random_range: range of random minute offset (e.g., (0, 59))
    :param seconds_random_range: range of random second offset (e.g., (0, 59))
    """

    base_time = datetime.now() + timedelta(days=1)

    random_hours = randint(*hours_random_range)
    random_minutes = randint(*minutes_random_range)
    random_seconds = randint(*seconds_random_range)

    run_time = base_time + timedelta(
        hours=random_hours,
        minutes=random_minutes,
        seconds=random_seconds
    )

    if scheduler.get_job(str(chat_id)):
        scheduler.remove_job(str(chat_id))

    scheduler.add_job(
        task_func,
        'date',
        run_date=run_time,
        id=str(chat_id),
        args=[chat_id],
        misfire_grace_time=18000
    )


def update_task(
        chat_id: int | str,
        hours_range: tuple[int, int] = (12, 14),
        minutes_range: tuple[int, int] = (0, 59)
) -> None:
    """
    Reschedules an existing task for the given chat_id with a random delay.

    The new execution time will be current time + random hours + random minutes.

    :param chat_id: ID of the chat (used as the job ID)
    :param hours_range: range of hours to add (inclusive)
    :param minutes_range: range of minutes to add (inclusive)
    """
    current_datetime = datetime.now()
    random_delay = timedelta(
        hours=randint(*hours_range),
        minutes=randint(*minutes_range)
    )
    new_datetime = current_datetime + random_delay

    scheduler.reschedule_job(
        job_id=str(chat_id),
        trigger='date',
        run_date=new_datetime
    )
