import asyncio
import enum
import json
import socket

from . import common


async def send(conn: socket.socket, *data: enum.Enum | str):
    await asyncio.get_event_loop().sock_sendall(
        conn,
        b"".join(
            (len(st := (dat.encode("utf-8"))).to_bytes(4, "big") + st if isinstance(dat, str) else dat.value.to_bytes())
            for dat in data
        ),
    )


async def recv(conn, max: int):
    return await asyncio.get_event_loop().sock_recv(conn, max)


class Tasks:
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.id = 0

    def task(self, name: str, max_prog: int = 0, unit: str = ""):
        self.id += 1
        return Task(self.conn, self.id, name, max_prog, unit)

    async def done(self):
        await send(self.conn, common.TaskManager.DONE)


class Task:
    def __init__(
        self,
        conn: socket.socket,
        id: int,
        name: str,
        max_prog: int = 0,
        unit: str = "",
    ):
        self.conn = conn
        self.id = id
        self.name = name
        self.progress = 0
        self.max_progress = max_prog
        self.unit = unit

    async def start(self):
        await send(
            self.conn,
            common.TaskManager.STARTED,
            json.dumps(
                {
                    "id": self.id,
                    "name": self.name,
                    "prog": self.progress,
                    "max_prog": self.max_progress,
                    "unit": self.unit,
                },
            ),
        )

    async def set_progress(self, prog: int):
        self.progress = prog
        await self._update_prog()

    async def update(self, step_size: int):
        self.progress += step_size
        await self._update_prog()

    async def reset(self, step_size: int):
        self.progress = 0
        await self._update_prog()

    async def finish(self):
        self.progress = 0
        await send(
            self.conn,
            common.TaskManager.FINISHED,
            json.dumps({"id": self.id}),
        )

    async def fail(self):
        self.progress = 0
        await send(
            self.conn,
            common.TaskManager.FAILED,
            json.dumps({"id": self.id}),
        )

    async def set_max(self, max_progress: int):
        self.max_progress = max_progress
        await send(
            self.conn,
            common.TaskManager.SET_MAX,
            json.dumps(
                {
                    "id": self.id,
                    "max_prog": max_progress,
                },
            ),
        )

    async def _update_prog(self):
        await send(
            self.conn,
            common.TaskManager.SET_PROG,
            json.dumps(
                {
                    "id": self.id,
                    "prog": self.progress,
                },
            ),
        )

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.fail()
        else:
            await self.finish()
