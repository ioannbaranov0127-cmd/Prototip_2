"""
Параметры запуска дочернего Python на Linux-хостинге (Railway, VPS и т.д.).
Не меняет учебную логику — только окружение subprocess.
"""
from __future__ import annotations

import os
import sys
import tempfile


def runner_temp_dir() -> str:
    explicit = os.environ.get("CODE_RUNNER_TMP", "").strip()
    if explicit:
        os.makedirs(explicit, exist_ok=True)
        return explicit
    return tempfile.gettempdir()


def minimal_child_env() -> dict[str, str]:
    """Минимальное окружение: UTF-8 и PATH, без лишних секретов из .env хоста."""
    env: dict[str, str] = {
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    for key in ("PATH", "HOME", "SystemRoot"):
        val = os.environ.get(key)
        if val:
            env[key] = val
    tmp = runner_temp_dir()
    env["TMPDIR"] = tmp
    env["TEMP"] = tmp
    env["TMP"] = tmp
    return env


def child_preexec(timeout_sec: float):
    """Лимиты CPU/RAM/файлов для дочернего процесса (только Unix)."""
    if sys.platform == "win32":
        return None

    limit_sec = max(3, int(timeout_sec) + 2)
    mem_mb = int(os.environ.get("CODE_RUNNER_MEM_MB", "256"))

    def _preexec() -> None:
        try:
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (limit_sec, limit_sec))
            resource.setrlimit(
                resource.RLIMIT_AS,
                (mem_mb * 1024 * 1024, mem_mb * 1024 * 1024),
            )
            resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        except Exception:
            pass

    return _preexec
