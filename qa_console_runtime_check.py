import json
import time

from code_runner.interactive_session import InteractiveSession


def run_case(code, inputs=None, timeout_sec=8.0):
    inputs = inputs or []
    s = InteractiveSession.start(code)
    deadline = time.monotonic() + timeout_sec
    in_idx = 0
    events = []
    done = None
    try:
        while time.monotonic() < deadline:
            phase = s.poll()
            events.append(
                {
                    "status": phase.get("status"),
                    "stdout": phase.get("stdout_chunk", ""),
                    "stderr": phase.get("stderr_chunk", ""),
                }
            )
            st = phase.get("status")
            if st == "need_input":
                if in_idx >= len(inputs):
                    done = {"ok": False, "error": "missing_input", "events": events}
                    break
                phase = s.send_line(inputs[in_idx])
                in_idx += 1
                events.append(
                    {
                        "status": phase.get("status"),
                        "stdout": phase.get("stdout_chunk", ""),
                        "stderr": phase.get("stderr_chunk", ""),
                    }
                )
                if phase.get("status") == "done":
                    done = {"ok": phase.get("exit_code") == 0, "phase": phase, "events": events}
                    break
            elif st == "done":
                done = {"ok": phase.get("exit_code") == 0, "phase": phase, "events": events}
                break
            elif st == "error":
                done = {"ok": False, "error": phase.get("message"), "events": events}
                break
            else:
                time.sleep(0.01)
        if done is None:
            done = {"ok": False, "error": "timeout", "events": events}
    finally:
        s.close()
    return done


def main():
    report = {}

    report["multi_input"] = run_case(
        'print("Анна")\n'
        'n = input("ВВЕДИ: ")\n'
        'print(n)\n'
        'h = input("ВВЕДИ: ")\n'
        'print(h)\n',
        ["хай", "привет"],
    )

    report["input_in_loop"] = run_case(
        "for i in range(3):\n"
        "    x = input('Число: ')\n"
        "    print('ok', i, x)\n",
        ["1", "2", "3"],
    )

    report["while_input_break"] = run_case(
        "count = 0\n"
        "while True:\n"
        "    x = input('> ')\n"
        "    print(x)\n"
        "    count += 1\n"
        "    if count == 4:\n"
        "        break\n",
        ["a", "b", "c", "d"],
    )

    report["stderr_traceback"] = run_case(
        "print('start')\n"
        "x = 1 / 0\n",
        [],
    )

    # Fast repeated restarts should not crash lifecycle.
    restart_ok = True
    for i in range(12):
        s = InteractiveSession.start(f"print('run', {i})")
        time.sleep(0.01)
        p = s.poll()
        if p.get("status") not in ("running", "done"):
            restart_ok = False
        s.close()
        if s.proc.poll() is None:
            restart_ok = False
    report["rapid_restart"] = {"ok": restart_ok}

    # Simple memory/lifecycle smoke: no deadlock during many short sessions.
    batch_ok = True
    for i in range(35):
        r = run_case("print('x')", [])
        if not r.get("ok"):
            batch_ok = False
            break
    report["many_sessions"] = {"ok": batch_ok}

    report["all_ok"] = all(v.get("ok", False) for v in report.values() if isinstance(v, dict))

    with open("qa_console_runtime_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
