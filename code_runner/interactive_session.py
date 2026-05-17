"""
Интерактивное выполнение Python с живым stdout/stderr и inline input().
"""
from __future__ import annotations

import os
import secrets
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field

from .error_friendly import explain_stderr
from .host import child_preexec, minimal_child_env, runner_temp_dir

INTERACTIVE_MARKER = "\n\uffffEDU_CONSOLE_INPUT_WAIT\uffff\n"
DEFAULT_SESSION_TIMEOUT_SEC = 180.0
MAX_TOTAL_STDIO_CHARS = 600_000

HARNESS_TEMPLATE = '''# -*- coding: utf-8 -*-
"""Служебная обёртка для интерактивного input() в учебной консоли."""
import builtins as _builtins
import sys as _sys

_MARKER = {marker!r}

def _edu_input(prompt=""):
    p = "" if prompt is None else str(prompt)
    if p:
        _sys.stdout.write(p)
        _sys.stdout.flush()
    _sys.stdout.write(_MARKER)
    _sys.stdout.flush()
    line = _sys.stdin.readline()
    if line == "":
        raise EOFError("ввод закончился")
    return line.rstrip("\\r\\n")

_builtins.input = _edu_input

_user_path = _sys.argv[1]
with open(_user_path, encoding="utf-8") as _uf:
    _code = _uf.read()
exec(compile(_code, _user_path, "exec"), {{"__name__": "__main__", "__builtins__": _builtins}})
'''


@dataclass
class InteractiveSession:
    run_id: str
    user_path: str
    harness_path: str
    proc: subprocess.Popen[str]
    stdin_lines_sent: list[str] = field(default_factory=list)
    _stdout_feed: list[str] = field(default_factory=list)
    _stderr_chunks: list[str] = field(default_factory=list)
    _stderr_parts: list[str] = field(default_factory=list)
    _stdout_parse_buffer: str = ""
    _waiting_input: bool = False
    _done: bool = False
    _timed_out: bool = False
    _closed: bool = False
    _output_chars: int = 0
    _last_activity_monotonic: float = field(default_factory=time.monotonic)
    started_monotonic: float = field(default_factory=time.monotonic)
    _deadline_monotonic: float = field(default_factory=lambda: time.monotonic() + DEFAULT_SESSION_TIMEOUT_SEC)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _stdout_thread: threading.Thread | None = None
    _stderr_thread: threading.Thread | None = None
    _watchdog_thread: threading.Thread | None = None

    @classmethod
    def start(cls, code: str) -> InteractiveSession:
        run_id = secrets.token_hex(12)
        tmp_dir = runner_temp_dir()
        fd_u, user_path = tempfile.mkstemp(suffix=".py", prefix="edu_user_", dir=tmp_dir)
        fd_h, harness_path = tempfile.mkstemp(suffix=".py", prefix="edu_harness_", dir=tmp_dir)
        try:
            with os.fdopen(fd_u, "w", encoding="utf-8", newline="\n") as uf:
                uf.write(code)
            with os.fdopen(fd_h, "w", encoding="utf-8", newline="\n") as hf:
                hf.write(HARNESS_TEMPLATE.format(marker=INTERACTIVE_MARKER))
        except Exception:
            for p in (user_path, harness_path):
                try:
                    os.unlink(p)
                except OSError:
                    pass
            raise

        popen_kwargs: dict = {
            "args": [sys.executable, "-X", "utf8", "-I", harness_path, user_path],
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "cwd": tmp_dir,
            "env": minimal_child_env(),
            "bufsize": 1,
        }
        preexec = child_preexec(DEFAULT_SESSION_TIMEOUT_SEC)
        if preexec is not None:
            popen_kwargs["preexec_fn"] = preexec
        proc = subprocess.Popen(**popen_kwargs)
        sess = cls(run_id=run_id, user_path=user_path, harness_path=harness_path, proc=proc)
        sess._start_pumps()
        return sess

    def _start_pumps(self) -> None:
        def stdout_pump() -> None:
            try:
                stream = self.proc.stdout
                if stream is None:
                    return
                while True:
                    chunk = stream.read(1)
                    if not chunk:
                        break
                    with self._lock:
                        self._stdout_feed.append(chunk)
                        self._output_chars += len(chunk)
                        if self._output_chars > MAX_TOTAL_STDIO_CHARS:
                            self._timed_out = True
                            threading.Thread(target=self.abort, daemon=True).start()
                            break
                        self._touch_locked()
            except Exception:
                pass
            finally:
                with self._lock:
                    self._done = True

        def stderr_pump() -> None:
            try:
                stream = self.proc.stderr
                if stream is None:
                    return
                while True:
                    chunk = stream.read(256)
                    if not chunk:
                        break
                    with self._lock:
                        self._stderr_parts.append(chunk)
                        self._stderr_chunks.append(chunk)
                        self._touch_locked()
            except Exception:
                pass

        def watchdog() -> None:
            while True:
                time.sleep(0.2)
                with self._lock:
                    if self._closed or self._done:
                        return
                    if time.monotonic() > self._deadline_monotonic:
                        self._timed_out = True
                        break
            self.abort()

        self._stdout_thread = threading.Thread(target=stdout_pump, daemon=True)
        self._stderr_thread = threading.Thread(target=stderr_pump, daemon=True)
        self._watchdog_thread = threading.Thread(target=watchdog, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()
        self._watchdog_thread.start()

    def _touch_locked(self) -> None:
        now = time.monotonic()
        self._last_activity_monotonic = now
        self._deadline_monotonic = now + DEFAULT_SESSION_TIMEOUT_SEC

    @staticmethod
    def _suffix_prefix_len(text: str, prefix_source: str) -> int:
        max_len = min(len(text), len(prefix_source) - 1)
        for i in range(max_len, 0, -1):
            if text.endswith(prefix_source[:i]):
                return i
        return 0

    def poll(self) -> dict:
        with self._lock:
            if self._closed and not self._done:
                return {"status": "error", "message": "Выполнение остановлено."}

            stdout_chunk = ""
            if self._stdout_feed:
                self._stdout_parse_buffer += "".join(self._stdout_feed)
                self._stdout_feed.clear()
            marker = INTERACTIVE_MARKER

            if not self._waiting_input and self._stdout_parse_buffer:
                idx = self._stdout_parse_buffer.find(marker)
                if idx >= 0:
                    stdout_chunk += self._stdout_parse_buffer[:idx]
                    self._stdout_parse_buffer = self._stdout_parse_buffer[idx + len(marker) :]
                    self._waiting_input = True
                else:
                    keep = self._suffix_prefix_len(self._stdout_parse_buffer, marker)
                    if keep > 0:
                        stdout_chunk += self._stdout_parse_buffer[:-keep]
                        self._stdout_parse_buffer = self._stdout_parse_buffer[-keep:]
                    else:
                        stdout_chunk += self._stdout_parse_buffer
                        self._stdout_parse_buffer = ""

            stderr_chunk = "".join(self._stderr_chunks)
            self._stderr_chunks.clear()

            if self._done:
                if self._stdout_parse_buffer:
                    stdout_chunk += self._stdout_parse_buffer
                    self._stdout_parse_buffer = ""
                try:
                    code = self.proc.poll()
                    if code is None:
                        code = self.proc.wait(timeout=0.5)
                except Exception:
                    code = None
                stderr_full = "".join(self._stderr_parts)
                result: dict = {
                    "status": "done",
                    "stdout_chunk": stdout_chunk,
                    "stderr_chunk": stderr_chunk,
                    "stderr": stderr_full,
                    "exit_code": code,
                    "timed_out": self._timed_out,
                }
                if self._timed_out:
                    result["message"] = "Программа была остановлена по времени."
                if code not in (0, None):
                    result["friendly"] = explain_stderr(stderr_full)
                return result

            if self._waiting_input:
                return {"status": "need_input", "stdout_chunk": stdout_chunk, "stderr_chunk": stderr_chunk}

            return {"status": "running", "stdout_chunk": stdout_chunk, "stderr_chunk": stderr_chunk}

    def send_line(self, line: str) -> dict:
        with self._lock:
            if self._closed or self._done:
                return {"status": "error", "message": "Запуск уже завершён."}
            if not self._waiting_input:
                return {"status": "error", "message": "Программа сейчас не ждёт ввод."}
            try:
                if self.proc.stdin is None:
                    return {"status": "error", "message": "Канал ввода недоступен."}
                self.proc.stdin.write((line or "") + "\n")
                self.proc.stdin.flush()
            except Exception:
                return {"status": "error", "message": "Не удалось передать ввод в программу."}
            self.stdin_lines_sent.append(line or "")
            self._waiting_input = False
            self._touch_locked()
        return self.poll()

    def abort(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
        try:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        except Exception:
            pass
        with self._lock:
            self._done = True
        for p in (self.user_path, self.harness_path):
            try:
                os.unlink(p)
            except OSError:
                pass

    def close(self) -> None:
        self.abort()

    def stdin_for_check(self) -> str:
        if not self.stdin_lines_sent:
            return ""
        return "\n".join(self.stdin_lines_sent) + "\n"

    def is_finished(self) -> bool:
        with self._lock:
            if self._done or self._closed:
                return True
        return self.proc.poll() is not None

    def is_expired(self, now_monotonic: float | None = None) -> bool:
        now = now_monotonic if now_monotonic is not None else time.monotonic()
        with self._lock:
            return now > self._deadline_monotonic
