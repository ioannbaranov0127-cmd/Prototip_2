"""
Выполнение пользовательского кода вне основного процесса Flask.
"""
from .subprocess_runner import RunResult, run_python


def run_user_code(code: str, stdin: str = "") -> tuple[str, str | None, str | None]:
    """
    Тот же контракт, что раньше в app.py: (stdout-текст, краткая ошибка, подробности).

    stdin — строка, которая попадает в stdin дочернего процесса (для ``input()``).
    """
    result = run_python(code, stdin=stdin)
    return result.to_legacy_tuple()


__all__ = ["RunResult", "run_python", "run_user_code"]

