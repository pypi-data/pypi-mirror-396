"""Tests for increasing code coverage of task_manager.py"""

import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock
from other_agents_mcp.task_manager import (
    TaskManager,
    InMemoryStorage,
    Task,
    get_task_manager,
)
from other_agents_mcp.sqlite_storage import SqliteStorage
from other_agents_mcp import config


class TestInMemoryStorageCoverage:
    """InMemoryStorage 커버리지 테스트"""

    @pytest.mark.asyncio
    async def test_storage_operations(self):
        storage = InMemoryStorage()

        # 1. Create
        task = await storage.create_task("task-1")
        assert task.task_id == "task-1"
        assert task.status == "running"

        # 2. Get
        fetched = await storage.get_task("task-1")
        assert fetched == task

        # 3. Update
        task.status = "completed"
        task.result = "Done"
        await storage.update_task(task)

        fetched_updated = await storage.get_task("task-1")
        assert fetched_updated.status == "completed"
        assert fetched_updated.result == "Done"

        # 4. Get All
        all_tasks = await storage.get_all_tasks()
        assert len(all_tasks) == 1
        assert all_tasks[0].task_id == "task-1"

        # 5. Update Non-existent (should not fail)
        fake_task = Task(task_id="fake")
        await storage.update_task(fake_task)
        assert await storage.get_task("fake") is None


class TestTaskManagerCoverage:
    """TaskManager 커버리지 테스트"""

    @pytest.fixture
    async def manager(self):
        storage = InMemoryStorage()
        mgr = TaskManager(storage)
        await mgr.start()
        yield mgr
        await mgr.stop()

    @pytest.mark.asyncio
    async def test_periodic_cleanup(self, manager):
        """_periodic_cleanup 메서드 테스트"""
        # 완료된 지 오래된 작업 생성
        old_task = await manager._storage.create_task("old-task")
        old_task.status = "completed"
        old_task.completed_at = time.time() - 4000  # 1시간 이상 경과
        await manager._storage.update_task(old_task)

        # 최신 작업 생성
        new_task = await manager._storage.create_task("new-task")
        new_task.status = "completed"
        new_task.completed_at = time.time()
        await manager._storage.update_task(new_task)

        # cleanup 태스크 시작 (짧은 주기로)
        cleanup_task = asyncio.create_task(manager._periodic_cleanup(interval=0.1, ttl=3600))

        # 잠시 대기
        await asyncio.sleep(0.2)

        # cleanup 태스크 취소
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

        # 확인: old_task는 삭제되고 new_task는 남아있어야 함
        assert await manager._storage.get_task("old-task") is None
        assert await manager._storage.get_task("new-task") is not None

    @pytest.mark.asyncio
    async def test_get_task_status_error(self, manager):
        """get_task_status: failed 상태 테스트"""
        task = await manager._storage.create_task("fail-task")
        task.status = "failed"
        task.error = "Something went wrong"
        await manager._storage.update_task(task)

        status = await manager.get_task_status("fail-task")
        assert status["status"] == "failed"
        assert status["error"] == "Something went wrong"

    @pytest.mark.asyncio
    async def test_get_task_status_running(self, manager):
        """get_task_status: running 상태 및 elapsed_time 테스트"""
        await manager._storage.create_task("run-task")
        # created_at은 기본값 (현재시간)

        await asyncio.sleep(0.1)

        status = await manager.get_task_status("run-task")
        assert status["status"] == "running"
        assert status["elapsed_time"] > 0

    @pytest.mark.asyncio
    async def test_get_task_status_long_polling(self, manager):
        """get_task_status: timeout(long polling) 테스트"""
        
        # 1. 1초 뒤에 끝나는 작업 시작
        async def slow_task():
            await asyncio.sleep(1.0)
            return "finished"

        task_id = await manager.start_async_task(slow_task())
        
        # 2. Timeout 0.5초로 호출 -> 여전히 running이어야 함 (0.5초 대기 후 반환)
        start_time = time.time()
        status = await manager.get_task_status(task_id, timeout=0.5)
        elapsed = time.time() - start_time
        
        assert status["status"] == "running"
        assert 0.4 < elapsed < 0.7  # 대략 0.5초 대기했는지 확인

        # 3. Timeout 1.5초(잔여 시간)로 호출 -> completed 반환
        status_done = await manager.get_task_status(task_id, timeout=1.5)
        assert status_done["status"] == "completed"
        assert status_done["result"] == "finished"

    @pytest.mark.asyncio
    async def test_singleton_getter(self):
        """get_task_manager 싱글톤 테스트"""
        # Reset singleton
        import other_agents_mcp.task_manager

        other_agents_mcp.task_manager._task_manager_instance = None

        # 1. Default (InMemory)
        with patch.object(config, "STORAGE_TYPE", "memory"):
            mgr1 = get_task_manager()
            assert isinstance(mgr1._storage, InMemoryStorage)

            mgr2 = get_task_manager()
            assert mgr1 is mgr2

        # Reset again
        other_agents_mcp.task_manager._task_manager_instance = None

        # 2. Sqlite
        # SqliteStorage 클래스 자체를 모킹하면 isinstance 체크에서 실패하므로
        # __init__ 메서드만 모킹하여 실제 파일 생성을 방지합니다.
        with (
            patch.object(config, "STORAGE_TYPE", "sqlite"),
            patch(
                "other_agents_mcp.sqlite_storage.SqliteStorage.__init__", return_value=None
            ) as MockInit,
            patch(
                "other_agents_mcp.sqlite_storage.SqliteStorage.recover_tasks",
                new_callable=AsyncMock,
            ) as MockRecover,
        ):

            mgr3 = get_task_manager()

            # isinstance 체크가 통과해야 함
            assert isinstance(mgr3._storage, SqliteStorage)
            MockInit.assert_called_once()

            # recover_tasks 호출 확인 (start 시점)
            await mgr3.start()
            MockRecover.assert_called_once()
            await mgr3.stop()

    @pytest.mark.asyncio
    async def test_start_cleanup_twice(self, manager):
        """start를 두 번 호출해도 cleanup task가 하나만 생성되는지 확인"""
        # fixture에서 이미 start()가 호출되어 cleanup_task가 생성됨
        original_task = manager._cleanup_task
        assert original_task is not None

        # 다시 start 호출
        await manager.start()

        # cleanup_task가 변경되지 않았음을 확인
        assert manager._cleanup_task is original_task

    @pytest.mark.asyncio
    async def test_run_and_update_exception(self, manager):
        """_run_and_update 예외 발생 테스트"""

        def failing_func():
            raise ValueError("Boom")

        task_id = await manager.start_task(failing_func)

        # Wait for completion
        await asyncio.sleep(0.1)

        task = await manager._storage.get_task(task_id)
        assert task.status == "failed"
        assert "Boom" in task.error
