"""
Tests for SqliteStorage
"""

import pytest
import sqlite3
from pathlib import Path

from other_agents_mcp.sqlite_storage import SqliteStorage


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """테스트용 임시 데이터베이스 경로를 제공합니다."""
    return tmp_path / "test_tasks.db"


@pytest.fixture
def storage(db_path: Path) -> SqliteStorage:
    """테스트용 SqliteStorage 인스턴스를 생성합니다."""
    return SqliteStorage(db_path=db_path)


@pytest.mark.asyncio
async def test_initialization_creates_table(db_path: Path):
    """__init__이 호출될 때 'tasks' 테이블이 생성되는지 확인합니다."""
    # 연결을 닫기 위해 storage 인스턴스를 생성하고 즉시 소멸시킵니다.
    _ = SqliteStorage(db_path=db_path)

    # 데이터베이스에 직접 연결하여 테이블 존재 여부 확인
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
        result = cursor.fetchone()
        assert result is not None, "tasks 테이블이 생성되지 않았습니다."
        assert result[0] == "tasks"


@pytest.mark.asyncio
async def test_create_and_get_task(storage: SqliteStorage):
    """작업을 생성하고 올바르게 조회되는지 확인합니다."""
    task_id = "test-task-1"
    created_task = await storage.create_task(task_id)

    assert created_task.task_id == task_id
    assert created_task.status == "running"

    retrieved_task = await storage.get_task(task_id)
    assert retrieved_task is not None
    assert retrieved_task.task_id == task_id
    assert retrieved_task.status == "running"
    assert retrieved_task.created_at is not None


@pytest.mark.asyncio
async def test_get_nonexistent_task(storage: SqliteStorage):
    """존재하지 않는 작업을 조회할 때 None이 반환되는지 확인합니다."""
    retrieved_task = await storage.get_task("non-existent-id")
    assert retrieved_task is None


@pytest.mark.asyncio
async def test_update_task(storage: SqliteStorage):
    """작업 상태를 업데이트하고 올바르게 반영되는지 확인합니다."""
    task_id = "test-task-2"
    await storage.create_task(task_id)

    # 업데이트할 Task 객체 가져오기
    task = await storage.get_task(task_id)
    assert task is not None

    # 상태 업데이트
    task.status = "completed"
    task.result = {"output": "some result"}
    await storage.update_task(task)

    # 업데이트된 Task 다시 조회
    updated_task = await storage.get_task(task_id)
    assert updated_task is not None
    assert updated_task.status == "completed"
    assert updated_task.result == {"output": "some result"}
    assert updated_task.error is None


@pytest.mark.asyncio
async def test_get_all_tasks(storage: SqliteStorage):
    """여러 작업을 생성하고 모두 조회되는지 확인합니다."""
    task_ids = ["task-a", "task-b", "task-c"]
    for tid in task_ids:
        await storage.create_task(tid)

    all_tasks = await storage.get_all_tasks()
    assert len(all_tasks) == len(task_ids)

    retrieved_ids = {t.task_id for t in all_tasks}
    assert retrieved_ids == set(task_ids)


@pytest.mark.asyncio
async def test_recover_tasks(db_path: Path):
    """서버 재시작 시 'running' 상태의 작업이 'failed'로 복구되는지 확인합니다."""
    # 1. 초기 저장소 인스턴스로 'running' 상태의 작업을 생성합니다.
    storage1 = SqliteStorage(db_path=db_path)
    await storage1.create_task("running-task-1")
    await storage1.create_task("running-task-2")

    # 2. 완료된 작업도 하나 생성합니다. 이 작업은 변경되지 않아야 합니다.
    completed_task = await storage1.create_task("completed-task")
    completed_task.status = "completed"
    completed_task.result = "done"
    await storage1.update_task(completed_task)

    # 3. 새로운 저장소 인스턴스를 생성하여 서버 재시작을 시뮬레이션합니다.
    storage2 = SqliteStorage(db_path=db_path)
    await storage2.recover_tasks()

    # 4. 상태를 확인합니다.
    task1 = await storage2.get_task("running-task-1")
    assert task1 is not None
    assert task1.status == "failed"
    assert task1.error == "Task failed due to server restart."

    task2 = await storage2.get_task("running-task-2")
    assert task2 is not None
    assert task2.status == "failed"

    task3 = await storage2.get_task("completed-task")
    assert task3 is not None
    assert task3.status == "completed"
    assert task3.result == "done"
