"""SQLite Storage for Task Manager

`sqlite3`를 사용하여 Task 객체를 영속적으로 저장하는 저장소 구현.
"""

import asyncio
import sqlite3
import json
import time
from pathlib import Path
from typing import Optional, List

from .task_manager import Storage, Task


class SqliteStorage(Storage):
    """SQLite를 사용하여 작업을 저장하는 클래스"""

    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결을 반환합니다."""
        return sqlite3.connect(self._db_path)

    def _create_table(self):
        """'tasks' 테이블이 없으면 생성하고 WAL 모드를 활성화합니다."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # WAL 모드 활성화 (동시성 향상)
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    created_at REAL NOT NULL,
                    completed_at REAL
                )
            """
            )
            conn.commit()

    async def create_task(self, task_id: str) -> Task:
        """새 작업을 데이터베이스에 생성하고 Task 객체를 반환합니다."""
        task = Task(task_id=task_id)

        def _db_insert():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (task_id, status, created_at) VALUES (?, ?, ?)",
                    (task.task_id, task.status, task.created_at),
                )
                conn.commit()

        await asyncio.to_thread(_db_insert)
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """ID로 작업을 데이터베이스에서 조회합니다."""

        def _db_select():
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
                row = cursor.fetchone()
                return self._row_to_task(row) if row else None

        return await asyncio.to_thread(_db_select)

    async def update_task(self, task: Task) -> None:
        """작업의 상태를 데이터베이스에 업데이트합니다."""

        def _db_update():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE tasks
                    SET status = ?, result = ?, error = ?, completed_at = ?
                    WHERE task_id = ?
                    """,
                    (
                        task.status,
                        json.dumps(task.result) if task.result is not None else None,
                        task.error,
                        task.completed_at,
                        task.task_id,
                    ),
                )
                conn.commit()

        await asyncio.to_thread(_db_update)

    async def get_all_tasks(self) -> List[Task]:
        """데이터베이스의 모든 작업을 반환합니다."""

        def _db_select_all():
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks")
                rows = cursor.fetchall()
                return [self._row_to_task(row) for row in rows if row]

        return await asyncio.to_thread(_db_select_all)

    async def recover_tasks(self) -> None:
        """'running' 상태인 모든 작업을 'failed'로 복구합니다."""

        def _db_recover():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE tasks
                    SET status = ?, error = ?, completed_at = ?
                    WHERE status = ?
                    """,
                    (
                        "failed",
                        "Task failed due to server restart.",
                        time.time(),
                        "running",
                    ),
                )
                conn.commit()

        await asyncio.to_thread(_db_recover)

    def _row_to_task(self, row: sqlite3.Row) -> Optional[Task]:
        """데이터베이스 row를 Task 객체로 변환합니다."""
        if not row:
            return None

        result_str = row["result"]
        result = None
        if result_str:
            try:
                result = json.loads(result_str)
            except (json.JSONDecodeError, TypeError):
                # result가 JSON 형식이 아닌 일반 문자열일 경우를 대비
                result = result_str

        return Task(
            task_id=row["task_id"],
            status=row["status"],
            result=result,
            error=row["error"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
        )
