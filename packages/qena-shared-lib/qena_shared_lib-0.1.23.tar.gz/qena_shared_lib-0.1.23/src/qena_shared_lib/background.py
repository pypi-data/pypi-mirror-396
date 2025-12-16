from asyncio import (
    Queue,
    Task,
    gather,
)
from typing import Any
from uuid import uuid4

from prometheus_client import Enum as PrometheusEnum
from starlette.background import BackgroundTask

from .logging import LoggerFactory
from .remotelogging import BaseRemoteLogSender
from .utils import AsyncEventLoopMixin

__all__ = [
    "Background",
    "BackgroundTask",
]


class Background(AsyncEventLoopMixin):
    _BACKGROUND_RUNNER_STATE = PrometheusEnum(
        name="background_runner_state",
        documentation="Background runner state",
        states=["running", "stopped"],
    )

    def __init__(
        self,
        remote_logger: BaseRemoteLogSender,
    ) -> None:
        self._queue: Queue[tuple[BackgroundTask | None, str | None]] = Queue()
        self._started = False
        self._stopped = False
        self._remote_logger = remote_logger
        self._logger = LoggerFactory.get_logger("background")
        self._tasks: dict[str, Task[Any]] = {}

    async def _task_manager(
        self, task: BackgroundTask, task_id: str | None = None
    ) -> None:
        self._logger.info(
            "running %s: %s with %s", task_id, task.func.__name__, task.args
        )

        if task_id is None:
            task_id = str(uuid4())

        try:
            self._tasks[task_id] = self.loop.create_task(
                task.func(*task.args, **task.kwargs)
            )

            await self._tasks[task_id]
        except Exception:
            self._remote_logger.exception(
                message=f"exception occured while running background task {task.func.__name__} with id {task_id}",
                tags=["background", "task_execution_failed", task_id],
                extra={"serviceType": "background", "taskId": task_id},
            )
        finally:
            self._logger.info("finished running %s", task.func.__name__)
            self._tasks.pop(task_id, None)

    def _run(self, task: BackgroundTask, task_id: str | None = None) -> None:
        if not self._stopped and (
            task_id is None or task_id not in self._tasks
        ):
            self.loop.create_task(self._task_manager(task, task_id))

    async def _run_tasks(self) -> None:
        while not self._stopped or not self._queue.empty():
            task, task_id = await self._queue.get()

            if task is None and task_id is None:
                break

            if task is not None:
                self._run(task=task, task_id=task_id)

        tasks = [t for _, t in self._tasks.items() if not t.done()]

        await gather(*tasks)

    def add_task(
        self, task: BackgroundTask, task_id: str | None = None
    ) -> None:
        self._queue.put_nowait((task, task_id))

    def start(self) -> None:
        if self._started:
            raise RuntimeError("background runner already running")

        self.loop.create_task(self._run_tasks())
        self._BACKGROUND_RUNNER_STATE.state("running")

        self._started = True

    def stop(self) -> None:
        if self._stopped:
            raise RuntimeError("background runner already stopped")

        self._stopped = True
        self._queue.put_nowait((None, None))
        self._BACKGROUND_RUNNER_STATE.state("stopped")

    def is_alive(self, task_id: str) -> bool:
        if task_id in self._tasks and not self._tasks[task_id].done():
            return True

        return False

    def count(self) -> int:
        return len(self._tasks)
