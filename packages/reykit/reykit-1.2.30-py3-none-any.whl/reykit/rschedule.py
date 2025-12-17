# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-09
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Schedule methods.
"""


from typing import Any
from collections.abc import Callable
from types import ModuleType
from inspect import ismodule
from functools import wraps as functools_wraps
from enum import StrEnum
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.job import Job
from reydb import rorm, DatabaseEngine
from reykit.rtime import now

from .rbase import Base, throw


__all__ = (
    'ScheduleStatusEnum',
    'DatabaseORMTableSchedule',
    'Schedule'
)


class ScheduleStatusEnum(StrEnum):
    """
    Schedule status enumeration type.
    """

    START = 'start'
    'Schedule stated.'
    SUCCESS = 'success'
    'Schedule successded.'
    FAIL = 'fail'
    'Schedule failed.'


class DatabaseORMTableSchedule(rorm.Table):
    """
    Database "schedule" table ORM model.
    """

    __name__ = 'schedule'
    __comment__ = 'Schedule execute record table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', arg_default=now, index_n=True, comment='Record update time.')
    status: str = rorm.Field(rorm.ENUM(ScheduleStatusEnum), field_default=ScheduleStatusEnum.START, not_null=True, comment='Schedule status.')
    task: str = rorm.Field(rorm.types.VARCHAR(100), not_null=True, comment='Schedule task function name.')
    note: str = rorm.Field(rorm.types.VARCHAR(500), comment='Schedule note.')


class Schedule(Base):
    """
    Schedule type.
    Can create database used "self.build_db" method.
    """


    def __init__(
        self,
        max_workers: int = 10,
        max_instances: int = 1,
        coalesce: bool = True,
        block: bool = False,
        db_engine: DatabaseEngine | None = None,
        echo: bool = False
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        max_workers : Maximum number of synchronized executions.
        max_instances : Maximum number of synchronized executions of tasks with the same ID.
        coalesce : Whether to coalesce tasks with the same ID.
        block : Whether to block.
        db_engine : Database engine.
            - "None": Not use database.
            - "Database": Automatic record to database.
        echo : Whether to print the report.
        """

        # Build.
        self.db_engine = db_engine
        self.echo = echo

        ## Scheduler.
        executor = ThreadPoolExecutor(max_workers)
        executors = {'default': executor}
        job_defaults = {
            'coalesce': coalesce,
            'max_instances': max_instances
        }
        if block:
            scheduler = BlockingScheduler(
                executors=executors,
                job_defaults=job_defaults
            )
        else:
            scheduler = BackgroundScheduler(
                executors=executors,
                job_defaults=job_defaults
            )
        self.scheduler = scheduler

        ## Build Database.
        if self.db_engine is not None:
            self.build_db()


    def build_db(self) -> None:
        """
        Check and build database tables.
        """

        # Check.
        if self.db_engine is None:
            throw(ValueError, self.db_engine)

        # Parameter.

        ## Table.
        tables = [DatabaseORMTableSchedule]

        ## View stats.
        views_stats = [
            {
                'table': 'stats_schedule',
                'items': [
                    {
                        'name': 'count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "schedule"'
                        ),
                        'comment': 'Schedule count.'
                    },
                    {
                        'name': 'past_day_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "schedule"\n'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                        ),
                        'comment': 'Schedule count in the past day.'
                    },
                    {
                        'name': 'past_week_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "schedule"\n'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                        ),
                        'comment': 'Schedule count in the past week.'
                    },
                    {
                        'name': 'past_month_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "schedule"\n'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                        ),
                        'comment': 'Schedule count in the past month.'
                    },
                    {
                        'name': 'task_count',
                        'select': (
                            'SELECT COUNT(DISTINCT "task")\n'
                            'FROM "schedule"'
                        ),
                        'comment': 'Task count.'
                    },
                    {
                        'name': 'last_time',
                        'select': (
                            'SELECT COALESCE(MAX("update_time"), MAX("create_time"))\n'
                            'FROM "schedule"'
                        ),
                        'comment': 'Schedule last record time.'
                    }
                ]
            }
        ]

        # Build.
        self.db_engine.build.build(tables=tables, views_stats=views_stats, skip=True)

        # ## Error.
        self.db_engine.error.build_db()


    def run(self) -> None:
        """
        Run the scheduler to start.
        """

        # Echo.
        if self.echo:
            print('Run scheduler.')

        # Pause.
        self.scheduler.start()


    def stop(self) -> None:
        """
        Stop started scheduler.
        """

        # Echo.
        if self.echo:
            print('Stop scheduler.')

        # Pause.
        self.scheduler.pause()


    def start(self) -> None:
        """
        Start stopped scheduler.
        """

        # Echo.
        if self.echo:
            print('Start scheduler.')

        # Resume.
        self.scheduler.resume()


    def tasks(self) -> list[Job]:
        """
        Return to task list.

        Returns
        -------
        Task list.
        """

        # Get.
        jobs = self.scheduler.get_jobs()

        return jobs


    __iter__ = tasks


    def wrap_record_db(
        self,
        task: Callable,
        note: str | None
    ) -> None:
        """
        Decorator, record to database.

        Parameters
        ----------
        task : Task.
        note : Task note.
        """


        @functools_wraps(task)
        def _task(*args, **kwargs) -> None:
            """
            Decorated function.

            Parameters
            ----------
            args : Position arguments of function.
            kwargs : Keyword arguments of function.
            """

            # Parameter.
            nonlocal task, note

            # Status executing.
            data = {
                'update_time': ':NOW()',
                'task': task.__name__,
                'note': note
            }
            result = self.db_engine.execute.insert(
                'schedule',
                data,
                returning='id'
            )
            id_: int = result.scalar()

            # Try execute.
            try:
                task(*args, **kwargs)

            # Status occurred error.
            except BaseException:
                data = {
                    'id': id_,
                    'update_time': ':NOW()',
                    'status': ScheduleStatusEnum.FAIL
                }
                self.db_engine.execute.update(
                    'schedule',
                    data
                )
                raise

            # Status completed.
            else:
                data = {
                    'id': id_,
                    'update_time': ':NOW()',
                    'status': ScheduleStatusEnum.SUCCESS
                }
                self.db_engine.execute.update(
                    'schedule',
                    data
                )

        return _task


    def wrap_echo(
        self,
        task: Callable,
        name: str
    ) -> None:
        """
        Decorator, print report.

        Parameters
        ----------
        task : Task.
        name : Task name.
        """


        @functools_wraps(task)
        def _task(*args, **kwargs) -> None:
            """
            Decorated function.

            Parameters
            ----------
            args : Position arguments of function.
            kwargs : Keyword arguments of function.
            """

            # Parameter.
            nonlocal task

            # Execute and echo.
            print(f'Execute | {name}')
            task(*args, **kwargs)
            print(f'Finish  | {name}')


        return _task


    def add_task(
        self,
        task: Callable | ModuleType,
        plan: dict[str, Any],
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        note: str | None = None
    ) -> Job:
        """
        Add task.

        Parameters
        ----------
        task : Task.
            - "Callable": Use this function.
            - "ModuleType": Use this "main" function of module.
        plan : Plan trigger keyword arguments.
        args : Task position arguments.
        kwargs : Task keyword arguments.
        note : Task note.

        Returns
        -------
        Task instance.
        """

        # Parameter.
        task_name = task.__name__
        *_, task_name = task_name.rsplit('.', 1)
        if ismodule(task):
            task = getattr(task, 'main')
        if plan is None:
            plan = {}
        trigger = plan.get('trigger')
        trigger_args = {
            key: value
            for key, value in plan.items()
            if key != 'trigger'
        }

        # Database.
        if self.db_engine is not None:
            task = self.wrap_record_db(task, note)
            task = self.db_engine.error.wrap(task, note)

        # Echo.
        if self.echo:
            task = self.wrap_echo(task, task_name)

        # Add.
        job = self.scheduler.add_job(
            task,
            trigger,
            args,
            kwargs,
            name=task_name,
            **trigger_args
        )

        # Echo.
        if self.echo:
            print(f'Add    | {task_name}')

        return job


    def update_task(
        self,
        task: Job | str,
        plan: dict[str, Any],
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        note: str | None = None
    ) -> None:
        """
        Update task.

        Parameters
        ----------
        task : Task instance or ID.
        plan : Plan trigger keyword arguments.
        args : Task position arguments.
        kwargs : Task keyword arguments.
        note : Task note.
        """

        # Parameter.
        if type(task) == Job:
            task_id = task.id
            task_name = task.name
        else:
            task_id = task
            task = self.scheduler.get_job(task_id)
            task_name = task.name
        if plan is None:
            plan = {}
        trigger = plan.get('trigger')
        trigger_args = {
            key: value
            for key, value in plan.items()
            if key != 'trigger'
        }

        # Modify plan.
        if plan != {}:
            self.scheduler.reschedule_job(
                task_id,
                trigger=trigger,
                **trigger_args
            )

        # Modify arguments.
        if (
            args != ()
            or kwargs != {}
        ):
            self.scheduler.modify_job(
                task_id,
                args=args,
                kwargs=kwargs
            )

        # Echo.
        if self.echo:
            print(f'Update | {task_name}')


    def remove_task(
        self,
        task: Job | str
    ) -> None:
        """
        Remove task.

        Parameters
        ----------
        task : Task instance or ID.
        """

        # Parameter.
        if type(task) == Job:
            task_id = task.id
            task_name = task.name
        else:
            task_id = task
            task = self.scheduler.get_job(task_id)
            task_name = task.name

        # Remove.
        self.scheduler.remove_job(task_id)

        # Echo.
        if self.echo:
            print(f'Remove | {task_name}')


    def stop_task(
        self,
        task: Job | str   
    ) -> None:
        """
        Stop started task.

        Parameters
        ----------
        task : Task instance or ID.
        """

        # Parameter.
        if type(task) == Job:
            task_id = task.id
            task_name = task.name
        else:
            task_id = task
            task = self.scheduler.get_job(task_id)
            task_name = task.name

        # Pause.
        self.scheduler.pause_job(task_id)

        # Echo.
        if self.echo:
            print(f'Stop   | {task_name}')


    def start_task(
        self,
        task: Job | str
    ) -> None:
        """
        Start stopped task.

        Parameters
        ----------
        task : Task instance or ID.
        """

        # Parameter.
        if type(task) == Job:
            task_id = task.id
            task_name = task.name
        else:
            task_id = task
            task = self.scheduler.get_job(task_id)
            task_name = task.name

        # Resume.
        self.scheduler.resume_job(task_id)

        # Echo.
        if self.echo:
            print(f'Start  | {task_name}')
