from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import List, Optional


def _run(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def _is_wsl() -> bool:
    return (
        "WSL_DISTRO_NAME" in os.environ
        or "WSL_INTEROP" in os.environ
        or "WSLENV" in os.environ
    )


def _notify_via_notify_send(
    title: str,
    body: str,
    urgency: str,
    icon: Optional[str],
    expire_ms: Optional[int],
) -> bool:
    if shutil.which("notify-send") is None:
        return False
    cmd = [
        "notify-send",
        "--app-name",
        "any-notify",
        "--urgency",
        urgency,
    ]
    if expire_ms is not None:
        cmd += ["--expire-time", str(expire_ms)]
    if icon:
        cmd += ["--icon", icon]
    cmd += [title, body]
    proc = _run(cmd)
    return proc.returncode == 0


def _notify_via_gdbus(
    title: str,
    body: str,
    urgency: str,
    icon: Optional[str],
    expire_ms: Optional[int],
) -> bool:
    if shutil.which("gdbus") is None:
        return False
    app_icon = icon or ""
    expire = -1 if expire_ms is None else int(expire_ms)
    # org.freedesktop.Notifications.Notify(
    #   app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout)
    cmd = [
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.freedesktop.Notifications",
        "--object-path",
        "/org/freedesktop/Notifications",
        "--method",
        "org.freedesktop.Notifications.Notify",
        "any-notify",
        "0",
        app_icon,
        title,
        body,
        "[]",
        "{}",
        str(expire),
    ]
    proc = _run(cmd)
    return proc.returncode == 0


def _notify_via_powershell(
    title: str,
    body: str,
    urgency: str,
    expire_ms: Optional[int],
) -> bool:
    # Use a simple COM popup as a widely available fallback on Windows.
    if shutil.which("powershell.exe") is None:
        return False
    timeout_s = 5 if expire_ms is None else max(1, int(round(expire_ms / 1000)))

    def esc(s: str) -> str:
        return s.replace("'", "''")

    ps = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$null = $ws.Popup('{esc(body)}', {timeout_s}, '{esc(title)}', 0x40)"
    )
    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps]
    proc = _run(cmd)
    return proc.returncode == 0


def _fallback_stdout(title: str, body: str, urgency: str) -> bool:
    stream = sys.stdout
    print(f"[{urgency}] {title}: {body}", file=stream)
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send a desktop notification in a portable way."
    )
    parser.add_argument("message", help="Notification body/message")
    parser.add_argument(
        "-t", "--title", default="any-notify", help="Notification title"
    )
    parser.add_argument(
        "-u",
        "--urgency",
        choices=["low", "normal", "critical"],
        default="normal",
        help="Urgency/priority level",
    )
    parser.add_argument("-i", "--icon", help="Icon name or absolute path", default=None)
    parser.add_argument(
        "-T",
        "--timeout",
        type=int,
        default=None,
        help="Timeout in milliseconds (backend dependent)",
    )
    parser.add_argument(
        "-b",
        "--backend",
        choices=["auto", "notify-send", "gdbus", "wsl", "stdout"],
        default="auto",
        help="Force a specific backend or auto-detect",
    )
    args = parser.parse_args(argv)

    title = args.title
    body = args.message
    urgency = args.urgency
    icon = args.icon
    expire_ms = args.timeout

    tried: list[str] = []

    def try_backend(name: str, fn) -> bool:
        tried.append(name)
        try:
            return fn()
        except Exception:
            return False

    is_wsl = _is_wsl()

    if args.backend == "notify-send":
        ok = _notify_via_notify_send(title, body, urgency, icon, expire_ms)
        return 0 if ok else 1
    if args.backend == "gdbus":
        ok = _notify_via_gdbus(title, body, urgency, icon, expire_ms)
        return 0 if ok else 1
    if args.backend == "wsl":
        ok = _notify_via_powershell(title, body, urgency, expire_ms)
        return 0 if ok else 1
    if args.backend == "stdout":
        _fallback_stdout(title, body, urgency)
        return 0

    # auto
    order: list[str] = []
    if not is_wsl:
        order = ["notify-send", "gdbus", "stdout"]
    else:
        order = ["notify-send", "gdbus", "wsl", "stdout"]

    for name in order:
        if name == "notify-send":
            if try_backend(
                name,
                lambda: _notify_via_notify_send(title, body, urgency, icon, expire_ms),
            ):
                return 0
        elif name == "gdbus":
            if try_backend(
                name, lambda: _notify_via_gdbus(title, body, urgency, icon, expire_ms)
            ):
                return 0
        elif name == "wsl":
            if try_backend(
                name, lambda: _notify_via_powershell(title, body, urgency, expire_ms)
            ):
                return 0
        elif name == "stdout":
            _fallback_stdout(title, body, urgency)
            return 0

    # If somehow nothing worked
    _fallback_stdout(title, body, urgency)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
