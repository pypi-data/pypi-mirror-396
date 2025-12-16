import json
import re
import time
from typing import Any, Literal, Optional, Tuple

from .config import config
from .doc_store import DocStore as DocStoreMongo
from .doc_store import TaskEntity
from .interface import Task, TaskCount, TaskInput
from .redis_stream import RedisStreamConsumer, RedisStreamManager, RedisStreamProducer


def _build_stream(command: str, priority: int) -> str:
    return f"{command}{config.redis.separator}{priority}"

def _build_task_id(command: str, priority: int, message_id: str) -> str:
    """Build task_id: {command}{sep}{priority}{sep}{message_id}"""
    return _build_stream(command, priority) + config.redis.separator + message_id


def _parse_task_id(task_id: str) -> Optional[Tuple[str, int, str]]:
    """Parse task_id to (command, priority, message_id), returns None if invalid"""
    sep = re.escape(config.redis.separator)
    pattern = rf"^(.+?){sep}(\d+){sep}(.+)$"
    match = re.match(pattern, task_id)
    if not match:
        return None
    try:
        command, priority_str, message_id = match.groups()
        priority = int(priority_str)
        return (command, priority, message_id)
    except ValueError:
        return None


class DocStoreRedis(DocStoreMongo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = RedisStreamProducer()
        self.consumer_group = config.redis.consumer_group
        self.consumer_pool = {}
        self.manager = RedisStreamManager()

    def impersonate(self, username: str) -> "DocStoreRedis":
        """Impersonate another user for this DocStore instance."""
        # use __new__ to bypass __init__
        new_store = super().impersonate(username)
        assert isinstance(new_store, DocStoreRedis)
        new_store.producer = self.producer
        new_store.consumer_group = self.consumer_group
        new_store.consumer_pool = self.consumer_pool
        new_store.manager = self.manager
        return new_store

    def _get_or_create_consumer(self, stream: str) -> RedisStreamConsumer:
        key = f"{stream}:{self.consumer_group}"
        if key not in self.consumer_pool:
            self.consumer_pool[key] = RedisStreamConsumer(None, stream, self.consumer_group, create_group=True)
        return self.consumer_pool[key]

    def get_task(self, task_id: str) -> Task:
        """Get a task by task_id."""
        parsed = _parse_task_id(task_id)
        if parsed:
            command, priority, message_id = parsed
            stream = _build_stream(command, priority)
        else:
            # Old format: task_id is just message_id, need command parameter
            raise ValueError(f"Old format task_id detected: {task_id}.")
        
        fields = self.manager.get_message(stream, message_id)
        if not fields:
            raise ValueError(f"Task not found: {task_id}")
        return Task(
            id=task_id,
            rid=0,
            status="new",
            target=fields["target"],
            command=fields["command"],
            args=json.loads(fields["args"]),
            create_user=fields["create_user"],
        )

    def insert_task(self, target_id: str, task_input: TaskInput) -> Task:
        """Insert a new task into the database."""
        self._check_writable()
        if not target_id:
            raise ValueError("target_id must be provided.")
        if not isinstance(task_input, TaskInput):
            raise ValueError("task_input must be a TaskInput instance.")
        command = task_input.command
        if not command:
            raise ValueError("command must be a non-empty string.")
        args = task_input.args or {}
        if any(not isinstance(k, str) for k in args.keys()):
            raise ValueError("All keys in args must be strings.")
        
        priority = task_input.priority
        if priority < 0 or priority > config.redis.max_priority_level:
            raise ValueError(f"priority must be between 0 and {config.redis.max_priority_level}")

        task_entity = {
            "target": target_id,
            "command": command,
            "args": json.dumps(args),
            "create_user": self.username,
        }

        stream = _build_stream(command, priority)
        message_id = self.producer.add(stream, fields=task_entity)
        task_id = _build_task_id(command, priority, message_id)
        return Task(
            id=task_id,
            rid=0,
            status="new",
            target=task_entity["target"],
            command=task_entity["command"],
            args=args,
            create_user=task_entity["create_user"],
        )

    def grab_new_tasks(
        self,
        command: str,
        args: dict[str, Any] = {},
        create_user: str | None = None,
        num=10,
        hold_sec=3600,
        max_retries=10,
    ) -> list[Task]:
        tasks = []
        remaining = num

        # 从高优先级到低优先级读取新格式的 stream（max_priority_level, ..., 1, 0）
        for priority in range(config.redis.max_priority_level, -1, -1):
            if remaining <= 0:
                break
            stream = _build_stream(command, priority)
            consumer = self._get_or_create_consumer(stream)
            messages = consumer.read_or_claim(remaining, min_idle_ms=hold_sec * 1000)
            for message in messages:
                task_entity = message.fields
                # Use command from message to ensure task_id matches stored data
                msg_command = task_entity["command"]
                task_id = _build_task_id(msg_command, priority, message.id)
                tasks.append(Task(
                    id=task_id,
                    rid=0,
                    status="new",
                    target=task_entity["target"],
                    command=msg_command,
                    args=json.loads(task_entity["args"]),
                    create_user=task_entity["create_user"],
                    grab_time=int(time.time() * 1000),
                ))
                remaining -= 1
                if remaining <= 0:
                    break
        
        # 兼容老数据：读取老格式的 stream（只有 command，没有 priority）
        if remaining > 0:
            old_stream = command
            consumer = self._get_or_create_consumer(old_stream)
            messages = consumer.read_or_claim(remaining, min_idle_ms=hold_sec * 1000)
            for message in messages:
                task_entity = message.fields
                msg_command = task_entity["command"]
                # Old format: task_id is just message_id
                old_task_id = message.id
                tasks.append(Task(
                    id=old_task_id,
                    rid=0,
                    status="new",
                    target=task_entity["target"],
                    command=msg_command,
                    args=json.loads(task_entity["args"]),
                    create_user=task_entity["create_user"],
                    grab_time=int(time.time() * 1000),
                ))
                remaining -= 1
                if remaining <= 0:
                    break
        
        return tasks

    def update_task(
        self,
        task_id: str,
        grab_time: int,
        command: str,
        status: Literal["done", "error", "skipped"],
        error_message: str | None = None,
        task: Task | None = None,
    ):
        """Update a task after processing."""
        self._check_writable()
        if not command:
            raise ValueError("command must be provided.")
        if not task_id:
            raise ValueError("task ID must be provided.")
        if not grab_time:
            raise ValueError("grab_time must be provided.")
        if status not in ("done", "error", "skipped"):
            raise ValueError("status must be one of 'done', 'error', or 'skipped'.")
        if status == "error" and not error_message:
            raise ValueError("error_message must be provided if status is 'error'.")

        if status == "error":
            if not task:
                raise ValueError("task must be provided if status is 'error'.")
            task_entity = TaskEntity(
                target=task.target,
                command=task.command,
                args=task.args,
                status="error",
                create_user=task.create_user,
                update_user=None,
                grab_user=task.grab_user,
                grab_time=grab_time,
                error_message=error_message,
            )
            result = self._insert_elem(Task, task_entity)
            assert result is not None, "Task insertion failed, should not happen."

        parsed = _parse_task_id(task_id)
        if parsed:
            # New format: {command}{sep}{priority}{sep}{message_id}
            parsed_command, priority, message_id = parsed
            stream = _build_stream(parsed_command, priority)
        else:
            # Old format: task_id is just message_id, stream is just command
            message_id = task_id
            stream = command
        self._get_or_create_consumer(stream).ack([message_id])

    def count_tasks(self, command: str | None = None) -> list[TaskCount]:
        """Count tasks grouped by priority and status."""
        commands = []
        if command:
            commands.append(command)
        else:
            commands = set([key.split(config.redis.separator)[0] for key in self.manager.client.keys("*")])
        task_counts = []
        for command in commands:
            for priority in range(config.redis.max_priority_level, -1, -1):
                stream = _build_stream(command, priority)
                groups_info = self.manager.groups_info(stream)
                if not groups_info:
                    continue
                for group_info in groups_info:
                    if group_info["name"] == f"{self.consumer_group}":
                        read = group_info["entries-read"] if group_info["entries-read"] else 0
                        total = read + group_info["lag"]
                        pending = group_info["lag"]
                        running = group_info["pending"]
                        completed = read - group_info["pending"]
                        task_counts.append(TaskCount(command=command, priority=priority, total=total, pending=pending, running=running, completed=completed))
                        break
            # 兼容老数据
            stream = command
            groups_info = self.manager.groups_info(stream)
            if not groups_info:
                continue
            for group_info in groups_info:
                if group_info["name"] == f"{self.consumer_group}":
                    read = group_info["entries-read"] if group_info["entries-read"] else 0
                    total = read + group_info["lag"]
                    pending = group_info["lag"]
                    running = group_info["pending"]
                    completed = read - group_info["pending"]
                    task_counts.append(TaskCount(command=command, priority=-1, total=total, pending=pending, running=running, completed=completed))
        return task_counts