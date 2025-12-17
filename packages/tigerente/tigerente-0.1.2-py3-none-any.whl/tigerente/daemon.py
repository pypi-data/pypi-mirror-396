import asyncio
import json
import logging
import socket
import time
import traceback
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import bleak

from . import build, common
from .bleio import BLEIOConnector
from .comm import Tasks, recv, send
from .storage import config

SHOULD_EXIT = False

conn_state = common.ConnectionState.DISCONNECTED
bleio: BLEIOConnector | None = None
scan_lock = asyncio.Lock()
running_progresses = {}


@asynccontextmanager
async def scan_locked():
    await scan_lock.acquire()
    yield
    scan_lock.release()


async def scan_for_devices():
    global bleio
    while not SHOULD_EXIT:
        async with scan_locked():
            logging.info("Starting scan...")
            devices = await bleak.BleakScanner.discover(common.DEVICE_SEARCH_ROUND)
        scan_time = time.time()
        if bleio is not None and bleio.address in config.cached_devices:
            config.cache_device(
                bleio.address,
                config.cached_devices[bleio.address]["name"],
                scan_time,
            )
        for device in devices:
            if device.name is None or not device.name.startswith("GSG-"):
                continue
            config.cache_device(device.address, device.name[4:], scan_time)
        logging.info("Finished scan.")
        await asyncio.sleep(common.DEVICE_SEARCH_PAUSE)
    logging.info("STOPPED SCAN")


async def stay_connected():
    global bleio, conn_state
    while not SHOULD_EXIT:
        if bleio is not None and not bleio._ble.is_connected:
            bleio = None
            conn_state = common.ConnectionState.DISCONNECTED

        if bleio is not None and bleio.address != config.target_device:
            with suppress(BaseException):
                conn_state = common.ConnectionState.DISCONNECTING
                await bleio.disconnect()
                conn_state = common.ConnectionState.DISCONNECTED
            bleio = None

        if bleio is None and config.target_device is not None and config.target_device in get_near_devices():
            async with scan_locked():
                conn_state = common.ConnectionState.CONNECTING
                bleio = BLEIOConnector(config.target_device)
                try:
                    await bleio.connect()
                    conn_state = common.ConnectionState.CONNECTED
                except Exception as e:
                    traceback.print_exception(e)
                    conn_state = common.ConnectionState.DISCONNECTED
                    bleio = None
        await asyncio.sleep(common.DEVICE_CONNECT_PAUSE)
    logging.info("STOPPED CONNECT")


def get_near_devices():
    return {
        address: device
        for address, device in config.cached_devices.items()
        if (device.get("last_seen") or 0) > time.time() - common.DEVICE_TOO_OLD
    }


async def handle_client(conn: socket.socket):
    global bleio
    packet = common.read_into(await recv(conn, 1), common.Querys)
    match packet:
        case common.Querys.GET_ALL_DEVICES:
            await send(
                conn,
                json.dumps(
                    config.cached_devices,
                ),
            )
        case common.Querys.GET_NEAR_DEVICES:
            await send(
                conn,
                json.dumps(get_near_devices()),
            )
        case common.Querys.GET_DEVICE_BY_ADDRESS:
            mac_address = (await recv(conn, 17)).decode("utf-8")
            await send(
                conn,
                json.dumps(config.cached_devices.get(mac_address)),
            )
        case common.Querys.GET_TARGET_DEVICE:
            if config.target_device is not None:
                await send(
                    conn,
                    json.dumps(
                        config.cached_devices.get(config.target_device)
                        or {
                            "name": "Unkown",
                            "last_seen": 0,
                            "address": config.target_device,
                        },
                    ),
                )
            else:
                await send(conn, "null")
        case common.Querys.SET_TARGET_DEVICE:
            mac_address = (await recv(conn, 17)).decode("utf-8")
            config.target_device = mac_address
            await send(conn, common.Success.OK)
        case common.Querys.UNSET_TARGET_DEVICE:
            config.target_device = None
            await send(conn, common.Success.OK)
        case common.Querys.KILL_DAEMON_PROCESS:
            global SHOULD_EXIT
            SHOULD_EXIT = True
            await send(conn, common.Success.OK)
        case common.Querys.GET_CONNECTION_STATE:
            if (
                conn_state == common.ConnectionState.CONNECTED
                and bleio is not None
                and bleio.address != config.target_device
            ):
                await send(conn, common.ConnectionState.INVALID)
            else:
                await send(conn, conn_state)
        case common.Querys.HUB_REBOOT:
            if bleio is not None:
                with suppress(BaseException):
                    await bleio.send_packet(b"&")
                await send(conn, common.Success.OK)
            else:
                await send(conn, common.Success.FAILED)
        case common.Querys.HUB_SYNC:
            dir_ = (await recv(conn, 1024)).decode("utf-8")

            if bleio is not None:
                await send(conn, common.Success.OK)
                tasks = Tasks(conn)
                success = await build.folder_sync(bleio, Path(dir_), tasks)
                await tasks.done()
                if success:
                    await send(conn, common.Success.OK)
                else:
                    await send(conn, common.Success.FAILED)
            else:
                await send(conn, common.Success.FAILED)
        case common.Querys.HUB_START_PROGRAM:
            if bleio is not None:
                with suppress(BaseException):
                    await bleio.send_packet(b"P")
                await send(conn, common.Success.OK)
            else:
                await send(conn, common.Success.FAILED)
        case common.Querys.HUB_STOP_PROGRAM:
            if bleio is not None:
                with suppress(BaseException):
                    await bleio.send_packet(b"X")
                await send(conn, common.Success.OK)
            else:
                await send(conn, common.Success.FAILED)
        case _:
            await send(conn, common.Success.FAILED)

    conn.close()


async def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    loop = asyncio.get_event_loop()
    logging.info(f"listening on {common.HOST}:{common.PORT}")
    server.bind((common.HOST, common.PORT))
    server.listen()
    server.setblocking(False)

    loop.create_task(stay_connected())
    loop.create_task(scan_for_devices())

    while not SHOULD_EXIT:
        conn, _ = await loop.sock_accept(server)
        loop.create_task(handle_client(conn))

    logging.info("STOPPED SERVER")

    async with scan_locked():
        if bleio is not None:
            await bleio.disconnect()
    logging.info("STOPPED CONNECTION")
    server.close()


def run_daemon():
    asyncio.run(main())


if __name__ == "__main__":
    run_daemon()
