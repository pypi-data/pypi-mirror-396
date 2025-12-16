"""Task Manager

비동기 작업을 관리하고 상태를 추적합니다.
"""

import time
import asyncio
import uuid
from functools import partial
from typing import Literal, Optional, Any, Dict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from . import config
from .logger import get_logger
from .file_handler import get_cli_semaphore

logger = get_logger(__name__)


# 작업 상태 정의
TaskStatus = Literal["running", "completed", "failed", "not_found"]


@dataclass
class Task:
    """비동기 작업의 데이터 모델"""

    task_id: str
    status: TaskStatus = "running"
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    @property
    def elapsed_time(self) -> float:
        if self.completed_at:
            return self.completed_at - self.created_at
        return time.time() - self.created_at


class Storage(ABC):
    """작업 저장소의 추상 베이스 클래스 (인터페이스)"""

    @abstractmethod
    async def create_task(self, task_id: str) -> Task:
        """새 작업을 저장소에 생성하고 반환합니다."""
        pass

    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """ID로 작업을 조회합니다."""
        pass

    @abstractmethod
    async def update_task(self, task: Task) -> None:
        """작업의 상태를 업데이트합니다."""
        pass

    @abstractmethod
    async def get_all_tasks(self) -> list[Task]:
        """모든 작업을 반환합니다."""
        pass


class InMemoryStorage(Storage):
    """인-메모리 작업 저장소 (MVP용)"""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    async def create_task(self, task_id: str) -> Task:
        task = Task(task_id=task_id)
        self._tasks[task_id] = task
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    async def update_task(self, task: Task) -> None:
        if task.task_id in self._tasks:
            self._tasks[task.task_id] = task

    async def get_all_tasks(self) -> list[Task]:
        return list(self._tasks.values())


class TaskManager:
    """비동기 작업 관리자"""

    def __init__(self, storage: Storage):
        self._storage = storage
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Task Manager를 시작하고 주기적인 정리 작업을 스케줄링합니다."""
        # SQLite 사용 시, 시작할 때 'running' 상태의 작업을 복구
        try:
            from .sqlite_storage import SqliteStorage
            if isinstance(self._storage, SqliteStorage):
                await self._storage.recover_tasks()
        except ImportError:
            pass  # Should not happen if configured correctly

        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def stop(self):
        """Task Manager를 중지하고 모든 백그라운드 작업을 취소합니다."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None
        for task in self._running_tasks.values():
            task.cancel()
        self._running_tasks.clear()

    async def start_task(self, coro_func: partial) -> str:
        """함수를 백그라운드 작업으로 시작하고 task_id를 반환합니다."""
        task_id = str(uuid.uuid4())

        # 새 작업을 저장소에 즉시 생성
        task = await self._storage.create_task(task_id)

        background_task = asyncio.create_task(self._run_and_update(task, coro_func))
        self._running_tasks[task_id] = background_task
        return task_id

    async def start_async_task(self, coro, task_id: Optional[str] = None) -> str:
        """비동기 코루틴을 백그라운드 작업으로 시작하고 task_id를 반환합니다.

        Args:
            coro: 실행할 코루틴 객체
            task_id: 선택적 task_id (지정하지 않으면 UUID 생성)

        Returns:
            task_id 문자열
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        # 새 작업을 저장소에 즉시 생성
        task = await self._storage.create_task(task_id)

        background_task = asyncio.create_task(self._run_async_and_update(task, coro))
        self._running_tasks[task_id] = background_task
        return task_id

    async def _run_async_and_update(self, task: Task, coro):
        """비동기 코루틴을 실행하고 결과를 저장소에 업데이트합니다."""
        task_id = task.task_id
        try:
            # 세마포어를 사용하여 동시 실행 수 제한
            async with get_cli_semaphore():
                result = await coro
            
            task.status = "completed"
            task.result = result
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
        finally:
            task.completed_at = time.time()
            await self._storage.update_task(task)
            self._running_tasks.pop(task_id, None)

    async def _run_and_update(self, task: Task, coro_func: partial):
        """코루틴을 실행하고 결과를 저장소에 업데이트합니다."""
        task_id = task.task_id
        try:
            # 세마포어를 사용하여 동시 실행 수 제한
            async with get_cli_semaphore():
                # functools.partial로 감싸진 동기 함수를 스레드에서 실행
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, coro_func)

            task.status = "completed"
            task.result = result
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
        finally:
            task.completed_at = time.time()
            await self._storage.update_task(task)
            self._running_tasks.pop(task_id, None)

    async def get_task_status(self, task_id: str, timeout: float = 0.0) -> Dict[str, Any]:
        """task_id로 작업 상태를 조회합니다.
        
        Args:
            task_id: 작업 ID
            timeout: 상태가 running일 경우 대기할 최대 시간 (초). 0이면 즉시 반환.
        """
        task = await self._storage.get_task(task_id)
        if not task:
            return {"status": "not_found", "error": "Task ID not found or expired."}

        # Long-polling: 작업이 진행 중이고 timeout이 설정된 경우 대기
        if task.status == "running" and timeout > 0:
            if task_id in self._running_tasks:
                try:
                    # 실제 asyncio 태스크가 완료될 때까지 대기
                    # shield를 사용하여 대기 중 취소되어도 원본 태스크는 유지
                    await asyncio.wait_for(
                        asyncio.shield(self._running_tasks[task_id]), 
                        timeout=timeout
                    )
                    # 대기 후 상태 다시 조회
                    task = await self._storage.get_task(task_id)
                    # task가 없을 수 있음 (극히 드문 경우)
                    if not task:
                        return {"status": "not_found", "error": "Task disappeared after wait."}
                except asyncio.TimeoutError:
                    # 타임아웃: 현재 상태(running) 그대로 반환
                    pass
                except Exception as e:
                    logger.error(f"Error waiting for task {task_id}: {e}")

        response: Dict[str, Any] = {"status": task.status}
        if task.status == "running":
            response["elapsed_time"] = round(task.elapsed_time, 2)
        elif task.status == "completed":
            response["result"] = task.result
        else:  # failed
            response["error"] = task.error

        return response

    async def _periodic_cleanup(self, interval: int = 600, ttl: int = 3600):
        """주기적으로 오래된 완료된 작업을 정리합니다."""
        while True:
            await asyncio.sleep(interval)
            now = time.time()
            tasks = await self._storage.get_all_tasks()
            for task in tasks:
                if task.status in ["completed", "failed"] and task.completed_at:
                    if now - task.completed_at > ttl:
                        # In-memory storage에서는 직접 삭제
                        if isinstance(self._storage, InMemoryStorage):
                            self._storage._tasks.pop(task.task_id, None)


# 싱글톤 인스턴스
_task_manager_instance: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """Task Manager 싱글톤 인스턴스를 반환합니다."""
    global _task_manager_instance
    if _task_manager_instance is None:
        if config.STORAGE_TYPE == "sqlite":
            logger.info(f"Using SqliteStorage at: {config.SQLITE_DB_PATH}")
            from .sqlite_storage import SqliteStorage
            storage: Storage = SqliteStorage(db_path=config.SQLITE_DB_PATH)
        else:
            logger.info("Using InMemoryStorage")
            storage = InMemoryStorage()

        _task_manager_instance = TaskManager(storage=storage)
    return _task_manager_instance