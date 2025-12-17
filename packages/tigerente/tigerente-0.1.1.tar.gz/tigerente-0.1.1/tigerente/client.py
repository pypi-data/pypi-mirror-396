import datetime
import enum
import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import click
from rich import progress
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from . import common
from .daemon import run_daemon

console = Console()


def get_sock(start_new=True, max_retries=5, delay=5) -> socket.socket:
    has_started_daemon = False
    for i in range(max_retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((common.HOST, common.PORT))
            if has_started_daemon:
                time.sleep(5)
            return s
        except ConnectionRefusedError:
            if start_new:
                if i == 0:
                    console.print(
                        "[yellow]Please wait for the daemon to start up...[/]",
                    )
                subprocess.Popen(
                    [sys.argv[0], "daemon"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )
                has_started_daemon = True
        time.sleep(delay)
    raise TimeoutError("Could not connect to daemon.")


class _Response:
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.buffer = b""

    def get_success(self, timeout: int = 5):
        return self.get_enum(common.Success, timeout)

    def get_enum[T: enum.Enum](self, enum: type[T], timeout: int = 5) -> T:
        byte = self.recv(1)
        return common.read_into(byte, enum)

    def get_string(self, timeout: int = 5):
        length = int.from_bytes(self.recv(4, timeout), "big")
        return self.recv(length, timeout)

    def get_data(self, timeout: int = 5):
        return json.loads(self.get_string())

    def recv(self, bytes: int, timeout: int = 5):
        start = time.time()
        while time.time() < start + timeout:
            data = self.conn.recv(1)
            self.buffer += data
            if len(self.buffer) >= bytes:
                result, self.buffer = self.buffer[:bytes], self.buffer[bytes:]
                return result
        raise TimeoutError("No response from daemon")

    def progress(self, timeout: int = 5):
        return _ResponseProgress(self, timeout)


class _ResponseProgress:
    def __init__(self, resp: _Response, timeout: int = 5):
        self.resp = resp
        self.timeout = timeout
        self.success = True
        self.buffer = b""

    def __iter__(self):
        return self

    def __next__(self):
        packet = self.resp.get_enum(common.TaskManager, self.timeout)
        if packet == common.TaskManager.DONE:
            raise StopIteration
        if packet == common.TaskManager.FAILED:
            self.success = False
        data = self.resp.get_data(self.timeout)
        return packet, data


def send(command: common.Querys, args: str = "", start_new_daemon=True):
    s = get_sock(start_new=start_new_daemon)
    s.send(command.value.to_bytes() + args.encode("utf-8"))
    return _Response(s)


def get_all_devices():
    return send(common.Querys.GET_ALL_DEVICES).get_data()


def get_nearby_devices():
    return send(common.Querys.GET_NEAR_DEVICES).get_data()


def get_device_by_address(mac_address: str):
    return send(common.Querys.GET_DEVICE_BY_ADDRESS, mac_address).get_data()


def set_target_device(mac_address: str):
    success = send(common.Querys.SET_TARGET_DEVICE, mac_address).get_success()
    assert success == common.Success.OK


def unset_target_device():
    success = send(common.Querys.UNSET_TARGET_DEVICE).get_success()
    assert success == common.Success.OK


def get_target_device() -> dict[str, str] | None:
    return send(common.Querys.GET_TARGET_DEVICE).get_data()


def get_connection_state():
    return send(common.Querys.GET_CONNECTION_STATE).get_enum(common.ConnectionState)


def wait_until(target: common.ConnectionState):
    while True:
        state = get_connection_state()
        if state == target:
            break
        time.sleep(0.5)
        yield state


_STATE_MAP: dict[common.ConnectionState, str] = {
    common.ConnectionState.INVALID: "Waiting to disconnect from [blue]{old}[/]...",
    common.ConnectionState.DISCONNECTED: "Searching for [blue]{new}[/]...",
    common.ConnectionState.CONNECTING: "Connecting to [blue]{new}[/]...",
    common.ConnectionState.DISCONNECTING: "Disconnecting from [blue]{old}[/]...",
    common.ConnectionState.CONNECTED: "Connected to [blue]{new}[/].",
}


def ensure_correct_device(mac_address: str):
    old = get_target_device()
    set_target_device(mac_address)
    new = get_target_device()
    assert new is not None
    text = Text.from_markup("[grey70]([yellow]00:00[/]) Scheduling...[/]")
    start = datetime.datetime.now()
    with console.status(text) as status:
        for state in wait_until(common.ConnectionState.CONNECTED):
            took = datetime.datetime.now() - start
            status._spinner.text = Text.from_markup(
                f"[grey50]([yellow]{took.seconds // 60:0>2}:{took.seconds % 60:0>2}[/])[/] [grey70]"
                + _STATE_MAP[state].format(
                    new=new["name"],
                    old=(old["name"] if old is not None else "[dark_orange3]No device[/]"),
                )
                + (
                    "[/] [grey50]([grey70]This takes longer than it should. Is BT turned on?[/])[/]"
                    if took.seconds > 20 and state == common.ConnectionState.DISCONNECTED
                    else ""
                ),
            )
            if (
                took.seconds > 30
                and state == common.ConnectionState.DISCONNECTED
                and mac_address not in get_nearby_devices()
            ):
                console.print(
                    "[[bright_red]x[/]] [bright_red]Device not nearby.[/]",
                )
                sys.exit(0)
    return datetime.datetime.now() - start


_STATE_MAP_DICONNECT = {
    common.ConnectionState.INVALID: "Disconnecting from [blue]{old}[/]...",
    common.ConnectionState.DISCONNECTED: "Disconnected.",
    common.ConnectionState.CONNECTING: "Still connecting to [blue]{old}[/]...",
    common.ConnectionState.DISCONNECTING: "Disconnecting from [blue]{old}[/]...",
    common.ConnectionState.CONNECTED: "Waiting to disconnect from [blue]{old}[/]...",
}


def ensure_disconnect(feedback=False):
    old = get_target_device()
    unset_target_device()
    text = Text.from_markup("[grey70]([yellow]00:00[/]) Scheduling...[/]")
    start = datetime.datetime.now()
    with console.status(text) as status:
        for state in wait_until(common.ConnectionState.DISCONNECTED):
            took = datetime.datetime.now() - start
            status._spinner.text = Text.from_markup(
                f"[grey50]([yellow]{took.seconds // 60:0>2}:{took.seconds % 60:0>2}[/])[/] [grey70]"
                + _STATE_MAP_DICONNECT[state].format(
                    old=(old["name"] if old is not None else "[dark_orange3]No device[/]"),
                ),
            )
    if feedback:
        took = datetime.datetime.now() - start
        if took.seconds > 1:
            console.print(
                f"[[green]:heavy_check_mark:[/]] ({took.seconds // 60:0>2}:{took.seconds % 60:0>2}) [green]Disconnected.[/]",
            )
        else:
            console.print(
                "[[green]:heavy_check_mark:[/]] [green]Disconnected.[/]",
            )


def ensure_connected(dev: str | None, final_feedback=True):
    current_device = get_target_device()
    current_state = get_connection_state()
    took = None
    if dev is None:
        if current_device is not None:
            if current_state != common.ConnectionState.CONNECTED:
                devices = get_all_devices()
                took = ensure_correct_device(
                    current_device["address"],
                )
        else:
            devices = get_nearby_devices()
            if not devices:
                console.print("[[bright_red1]x[/]] [bright_red]No devices found.[/]")
                return None
            console.print("[grey70]These devices seem to be nearby:[/]")
            for device in devices.values():
                console.print(
                    f"[grey70]- [blue]{device['name']}[/] [grey50]({device['address']})[/][/]"
                    + (
                        "[grey70] ([green]connected[/])[/]"
                        if current_state == common.ConnectionState.CONNECTED
                        and current_device
                        and current_device["address"] == device["address"]
                        else ""
                    ),
                )
            name = Prompt.ask(
                "[grey70]Choose a device to connect to[/]",
                choices=[device["name"] for device in devices.values()],
                show_choices=False,
            )
            for device in devices.values():
                if device["name"] == name:
                    took = ensure_correct_device(device["address"])
                    break
            else:
                raise RuntimeError
    else:
        if (
            current_state == common.ConnectionState.CONNECTED
            and current_device is not None
            and (current_device["address"] == dev or current_device["name"] == dev)
        ):
            pass
        elif re.match(r"^([A-Z0-9]{2}:){5}[A-Z0-9]{2}$", dev):
            took = ensure_correct_device(dev)
        else:
            devices = get_all_devices()
            for device in devices.values():
                if device["name"] == dev:
                    took = ensure_correct_device(device["address"])
                    break
            else:
                console.print("[[bright_red]x[/]] [bright_red]Device not found.[/]")
                sys.exit(0)

    if final_feedback:
        current_device = get_target_device()
        assert current_device is not None
        console.print(
            f"[grey50][[blue]:information:[/]] You are connected to [blue]{current_device['name']}[/].[/]",
        )
    return took


@click.group()
def main(): ...


@main.command("daemon")
def daemon():
    run_daemon()


@main.command("start-daemon")
def start_daemon():
    console.print("Daemon is being started...")
    get_sock()


@main.command("kill-daemon")
def kill_daemon_():
    console.print("Daemon is being killed...")
    try:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((common.HOST, common.PORT))
            s.send(common.Querys.KILL_DAEMON_PROCESS.value.to_bytes())
            time.sleep(1)
    except ConnectionRefusedError:
        console.print("Daemon was killed...")


@main.command("connect")
@click.argument("name_or_mac", required=False, default=None)
def connect(name_or_mac: str | None):
    if name_or_mac is None:
        current_device = get_target_device()
        current_state = get_connection_state()
        devices = get_nearby_devices()
        if not devices:
            console.print("[[bright_red1]x[/]] [bright_red]No devices found.[/]")
            return
        console.print("[grey70]These devices seem to be nearby:[/]")
        for device in devices.values():
            console.print(
                f"[grey70]- [blue]{device['name']}[/] [grey50]({device['address']})[/][/]"
                + (
                    "[grey70] ([green]connected[/])[/]"
                    if current_state == common.ConnectionState.CONNECTED
                    and current_device
                    and current_device["address"] == device["address"]
                    else ""
                ),
            )
        name_or_mac = Prompt.ask(
            "[grey70]Choose a device to connect to[/]",
            choices=[device["name"] for device in devices.values()],
            show_choices=False,
        )
    took = ensure_connected(name_or_mac, final_feedback=False)
    current_device = get_target_device()
    if current_device is None:
        console.print("[[bright_red1]x[/]] [bright_red]Failed to connect.[/]")
        return
    if took is not None and took.seconds > 1:
        console.print(
            f"[grey50][[green]:heavy_check_mark:[/]] ([cyan]{took.seconds // 60:0>2}:{took.seconds % 60:0>2}[/]) [green]Connected to [blue]{current_device['name']}[/].[/][/]",
        )
    else:
        console.print(
            f"[grey50][[green]:heavy_check_mark:[/]] [green]Connected to [blue]{current_device['name']}[/].[/][/]",
        )


@main.command("disconnect")
def disconnect():
    current_device = get_target_device()
    current_state = get_connection_state()
    if current_state == common.ConnectionState.DISCONNECTED:
        console.print(
            "[[green]:heavy_check_mark:[/]] [green]You are already disconnected.[/]",
        )
        return
    if current_state == common.ConnectionState.CONNECTED and current_device:
        console.print(
            f"[grey50][[blue]:information:[/]] You were connected to [yellow]{current_device['name']}[/].[/]",
        )
    ensure_disconnect(feedback=True)


@main.command("reboot")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def reboot(dev: str):
    ensure_connected(dev)
    success = send(common.Querys.HUB_REBOOT).get_success()
    assert success == common.Success.OK


@main.command("sync")
@click.argument(
    "directory",
    metavar="DIRECTORY",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path, exists=True),
)
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def sync(directory: Path, dev: str):
    ensure_connected(dev)
    resp = send(common.Querys.HUB_SYNC, str(directory.absolute()))
    assert resp.get_success() == common.Success.OK
    prog = resp.progress()
    tasks = {}
    task_progress = {}
    with (
        progress.Progress(
            progress.SpinnerColumn(),
            progress.TextColumn("[grey70]{task.description}[/]"),
            progress.BarColumn(),
            progress.TaskProgressColumn(),
            progress.TimeElapsedColumn(),
            transient=False,
            console=console,
            expand=True,
        ) as step_progress,
        progress.Progress(
            progress.TextColumn("[grey70]{task.description}[/]"),
            progress.BarColumn(),
            progress.DownloadColumn(),
            progress.TimeRemainingColumn(),
            transient=True,
            console=console,
            expand=True,
        ) as byte_progress,
    ):
        for packet, data in prog:
            match packet:
                case common.TaskManager.STARTED:
                    task_progress[data["id"]] = byte_progress if data["unit"] == "B" else step_progress
                    tasks[data["id"]] = task_progress[data["id"]].add_task(
                        data["name"],
                        completed=data["prog"],
                        total=data["max_prog"],
                    )
                case common.TaskManager.SET_PROG:
                    task_progress[data["id"]].update(
                        tasks[data["id"]],
                        completed=data["prog"],
                    )
                case common.TaskManager.SET_MAX:
                    task_progress[data["id"]].update(
                        tasks[data["id"]],
                        total=data["max_prog"],
                    )
                case common.TaskManager.FINISHED:
                    task_progress[data["id"]].stop_task(tasks[data["id"]])
                    task_progress[data["id"]].stop_task(tasks[data["id"]])
                    if data["id"] != 1:
                        task_progress[data["id"]].remove_task(tasks[data["id"]])
                case common.TaskManager.FAILED:
                    task_progress[data["id"]].stop_task(tasks[data["id"]])
                    task_progress[data["id"]].remove_task(tasks[data["id"]])
                case _:
                    raise AssertionError

    if prog.success and resp.get_success() == common.Success.OK:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]] [green]Synced.[/]",
        )
    else:
        console.print(
            "[[bright_red]x[/]] [bright_red]Failed to sync.[/]",
        )


@main.command("start")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def start(dev: str):
    ensure_connected(dev)
    success = send(common.Querys.HUB_START_PROGRAM).get_success()
    console.print(success)


@main.command("stop")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def stop(dev: str):
    ensure_connected(dev)
    success = send(common.Querys.HUB_STOP_PROGRAM).get_success()
    console.print(success)
