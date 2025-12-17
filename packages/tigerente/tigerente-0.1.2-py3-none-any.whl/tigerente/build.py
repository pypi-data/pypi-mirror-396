import asyncio
import base64
import hashlib
import json
import logging
import math
import os
import shutil
import subprocess
import tempfile
import time
import zlib
from pathlib import Path

import mpy_cross
import yaml

from .bleio import BLEIOConnector
from .comm import Task, Tasks


class ForceReconnect(BaseException): ...


mpy_cross.set_version("1.20", 6)
mpy_cross.fix_perms()


async def expect_OK(bleio: BLEIOConnector, ignore=b"="):
    while True:
        await asyncio.sleep(0.001)
        packet = bleio.get_packet()
        if not packet:
            continue
        nxt, _ = packet
        if nxt in ignore:
            continue
        if nxt != b"K":
            logging.warning(f"Expecting OK, Invalid response {nxt}, resetting connection")
            await bleio.send_packet(b"$")
            raise ForceReconnect
        return True


async def send_file(bleio: BLEIOConnector, file, task: Task | None = None):
    data = file.read()
    data = zlib.compress(data)
    data = base64.b64encode(data)
    if task is not None:
        await task.set_max(len(data))
    while True:
        await asyncio.sleep(0.001)
        chunk = data[:110]
        data = data[110:]
        if not chunk:
            break
        await bleio.send_packet(b"C", chunk)
        await expect_OK(bleio)
        if task is not None:
            await task.update(len(chunk))
    await bleio.send_packet(b"E")


def build_py(src: Path, dest: Path, src_dir: Path):
    result = subprocess.run(
        [mpy_cross.mpy_cross, src.relative_to(src_dir), "-o", dest],
        check=False,
        cwd=src_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        logging.warning(result.stdout.decode("utf-8"))
        logging.error(result.stderr.decode("utf-8"))
        return False
    return True


def copy_py(src: Path, dest: Path, src_dir: Path):
    shutil.copy(src, dest)
    return True


def build_yaml(src: Path, dest: Path, src_dir: Path):
    with src.open() as f:
        data = yaml.safe_load(f)
    dest.write_text(json.dumps(data))
    return True


file_builders = {".py": (build_py, ".mpy"), ".yaml": (build_yaml, ".json")}


def build(src_dir: Path, build_dir: Path):
    for file in src_dir.glob("**"):
        if file.is_dir():
            if file == src_dir:
                continue
            folder = build_dir / file.relative_to(src_dir)
            if file.exists():
                os.makedirs(folder, exist_ok=True)
            else:
                os.rmdir(folder)
            continue
        # Skip stup files
        if file.suffix == ".pyi":
            continue
        builder, new_suffix = file_builders.get(file.suffix, (None, None, None))
        if not builder:
            logging.warning(f"Unable to build {file.suffix} file.")
            continue
        wanted_dest = build_dir / file.with_suffix(new_suffix).relative_to(src_dir)

        if not file.exists():
            os.remove(wanted_dest)
            continue

        result = builder(file, wanted_dest, src_dir)
        if not result:
            logging.error(f"Failed to build {file.relative_to(src_dir).as_posix()}.")
            return False
    return True


async def sync_path(
    bleio: BLEIOConnector,
    file: Path,
    root_dir: Path,
    tasks: Tasks,
):
    path = file.relative_to(root_dir).as_posix()
    if path == ".":
        return

    if not file.exists():
        await bleio.send_packet(b"R", ("/" + path).encode())
    elif file.is_dir():
        await bleio.send_packet(b"D", ("/" + path).encode())
        await expect_OK(bleio)
    else:
        hashv = hashlib.sha256(file.read_bytes()).hexdigest()
        await bleio.send_packet(b"F", ("/" + path + " " + hashv).encode())
        while True:
            await asyncio.sleep(0.001)
            packet = bleio.get_packet()
            if packet is None:
                continue
            nxt, _ = packet
            if nxt == b"=":
                continue
            if nxt == b"K":
                break
            if nxt != b"U":
                logging.warning(
                    f"Expecting OK or U, Invalid response {nxt}, resetting connection",
                )
                await bleio.send_packet(b"$")
                raise ForceReconnect

            max_ = math.ceil(file.stat().st_size * (4 / 3))
            async with tasks.task(f"Sync file {path}...", max_, "B") as task:
                with file.open("rb") as f:
                    await send_file(bleio, f, task)


async def sync_dir(
    bleio: BLEIOConnector,
    dir: Path,
    tasks: Tasks,
):
    await bleio.send_packet(b"Y")
    await expect_OK(bleio)

    files = tuple(dir.glob("**"))
    max_prog = len(files)
    async with tasks.task("Sync directory...", max_prog, "files") as task:
        for file in files:
            await sync_path(bleio, file, dir, tasks)
            await task.update(1)

    await bleio.send_packet(b"N")
    await expect_OK(bleio)


async def sync_stream(bleio: BLEIOConnector, timeout=10):
    otm = time.time()
    otm_packet = str(otm).encode()
    await bleio.send_packet(b"=", otm_packet)
    while time.time() < otm + timeout:
        await asyncio.sleep(0.001)
        resp = bleio.get_packet()
        if resp is None:
            await bleio.send_packet(b"=", otm_packet)
            await asyncio.sleep(1)
            continue
        nxt, tm = resp
        if nxt == b"=" and tm == otm_packet:
            return
    raise TimeoutError(f"Hub failed to sync after {timeout} seconds.")


async def folder_sync(
    bleio: BLEIOConnector,
    src_dir: Path,
    tasks: Tasks,
):
    with tempfile.TemporaryDirectory() as BUILD_DIR:
        logging.info(BUILD_DIR)
        await sync_stream(bleio, 10)

        success = build(src_dir, Path(BUILD_DIR))
        if not success:
            return False
        await sync_dir(bleio, Path(BUILD_DIR), tasks)

        await bleio.send_packet(b"P")
        await expect_OK(bleio)
    return True
