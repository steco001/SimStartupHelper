import shlex
import subprocess
import threading
import time
from typing import Callable


class ProcessManager:
    def __init__(self, status_callback: Callable[[str | None, bool], None] = None):
        self._processes: dict[str, subprocess.Popen] = {}
        self._timers: list[threading.Timer] = []
        self._monitor_thread: threading.Thread | None = None
        self._monitor_active = False
        self._status_callback = status_callback

    def start_profile(self, programs: list[dict]):
        self._cancel_timers()
        for i, program in enumerate(programs):
            key = f"{i}_{program['name']}"
            t = threading.Timer(program.get("delay", 0), self._launch, args=[key, program])
            self._timers.append(t)
            t.start()
        if not self._monitor_active:
            self._start_monitor()

    def start_stopped(self, programs: list[dict]):
        for i, program in enumerate(programs):
            key = f"{i}_{program['name']}"
            proc = self._processes.get(key)
            if proc is None or proc.poll() is not None:
                t = threading.Timer(0, self._launch, args=[key, program])
                self._timers.append(t)
                t.start()

    def stop_all(self):
        self._cancel_timers()
        self._monitor_active = False
        for proc in list(self._processes.values()):
            proc.terminate()
        deadline = time.time() + 3.0
        for proc in list(self._processes.values()):
            remaining = max(0.0, deadline - time.time())
            try:
                proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                proc.kill()
        self._processes.clear()
        if self._status_callback:
            self._status_callback(None, False)

    def get_key(self, index: int, name: str) -> str:
        return f"{index}_{name}"

    def _launch(self, key: str, program: dict):
        try:
            args = shlex.split(program.get("args", "")) if program.get("args") else []
            proc = subprocess.Popen([program["path"]] + args)
            self._processes[key] = proc
            if self._status_callback:
                self._status_callback(key, True)
        except (OSError, ValueError):
            if self._status_callback:
                self._status_callback(key, False)

    def _cancel_timers(self):
        for t in self._timers:
            t.cancel()
        self._timers.clear()

    def _start_monitor(self):
        self._monitor_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        while self._monitor_active:
            for key, proc in list(self._processes.items()):
                if self._status_callback:
                    self._status_callback(key, proc.poll() is None)
            time.sleep(2)
