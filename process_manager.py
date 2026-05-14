import shlex
import subprocess
import threading
import time
from typing import Callable


class ProcessManager:
    def __init__(self, status_callback: Callable = None):
        self._processes: dict[str, subprocess.Popen] = {}
        self._timers: list[threading.Timer] = []
        self._monitor_thread: threading.Thread | None = None
        self._monitor_active = False
        self._status_callback = status_callback
        self._lock = threading.Lock()

    def start_profile(self, programs: list[dict]):
        with self._lock:
            self._cancel_timers_locked()
            for i, program in enumerate(programs):
                key = f"{i}_{program['name']}"
                t = threading.Timer(program.get("delay", 0), self._launch, args=[key, program])
                self._timers.append(t)
                t.start()
            should_start_monitor = not self._monitor_active
        if should_start_monitor:
            self._start_monitor()

    def start_stopped(self, programs: list[dict]):
        for i, program in enumerate(programs):
            key = f"{i}_{program['name']}"
            with self._lock:
                proc = self._processes.get(key)
                should_restart = proc is None or proc.poll() is not None
            if should_restart:
                threading.Thread(target=self._launch, args=[key, program], daemon=True).start()

    def stop_all(self):
        with self._lock:
            self._cancel_timers_locked()
            self._monitor_active = False
            procs = list(self._processes.values())
            self._processes.clear()

        for proc in procs:
            proc.terminate()
        deadline = time.time() + 3.0
        for proc in procs:
            remaining = max(0.0, deadline - time.time())
            try:
                proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                proc.kill()

        thread = self._monitor_thread
        self._monitor_thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)

        if self._status_callback:
            self._status_callback(None, False)

    def get_key(self, index: int, name: str) -> str:
        return f"{index}_{name}"

    def is_running(self, key: str) -> bool:
        with self._lock:
            proc = self._processes.get(key)
        return proc is not None and proc.poll() is None

    def _launch(self, key: str, program: dict):
        try:
            args = shlex.split(program.get("args", "")) if program.get("args") else []
            proc = subprocess.Popen(
                [program["path"]] + args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with self._lock:
                self._processes[key] = proc
            if self._status_callback:
                self._status_callback(key, True)
        except Exception:
            if self._status_callback:
                self._status_callback(key, False)

    def _cancel_timers_locked(self):
        for t in self._timers:
            t.cancel()
        self._timers.clear()

    def _start_monitor(self):
        self._monitor_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        while self._monitor_active:
            with self._lock:
                items = list(self._processes.items())
            for key, proc in items:
                if self._status_callback:
                    self._status_callback(key, proc.poll() is None)
            time.sleep(2)
