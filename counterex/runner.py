"""Timeout-controlled execution of TRUSTED code. This is not a security sandbox."""

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import time


@dataclass(frozen=True)
class Execution:
    status: str
    value: int | None = None
    stdout: str = ""
    stderr: str = ""
    returncode: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def run_python(candidate: Path, case: dict, *, trusted: bool = False,
               timeout: float = 2.0, output_limit: int = 65536) -> Execution:
    if not trusted:
        raise ValueError("Execution requires trusted=True. Review code first; this runner is not a sandbox.")
    if not math.isfinite(timeout) or timeout <= 0 or output_limit <= 0:
        raise ValueError("Timeout and output limit must be positive and finite")
    candidate = Path(candidate).resolve(strict=True)
    if not candidate.is_file():
        raise ValueError("Candidate must be a Python file")
    payload = json.dumps(case).encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="counterex-") as directory:
        root = Path(directory)
        # Files avoid pipe deadlocks and keep captured output out of parent RAM.
        with (root / "input").open("w+b") as stdin, (root / "out").open("w+b") as stdout, (root / "err").open("w+b") as stderr:
            stdin.write(payload)
            stdin.seek(0)
            started = time.monotonic()
            process = subprocess.Popen([sys.executable, "-I", str(candidate)],
                                       stdin=stdin, stdout=stdout, stderr=stderr, cwd=root)
            status = None
            try:
                while process.poll() is None:
                    if (root / "out").stat().st_size + (root / "err").stat().st_size > output_limit:
                        status = "output_limit"
                        break
                    if time.monotonic() - started > timeout:
                        status = "timeout"
                        break
                    time.sleep(0.01)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
            stdout.seek(0)
            stderr.seek(0)
            out = stdout.read(output_limit).decode("utf-8", errors="replace")
            err = stderr.read(output_limit).decode("utf-8", errors="replace")
            if status is None and (root / "out").stat().st_size + (root / "err").stat().st_size > output_limit:
                status = "output_limit"
            if status:
                return Execution(status, stdout=out, stderr=err, returncode=process.returncode)
            if process.returncode != 0:
                return Execution("runtime_error", stdout=out, stderr=err, returncode=process.returncode)
            try:
                value = json.loads(out)
                if type(value) is not int:
                    raise ValueError("Expected a JSON integer")
            except (ValueError, json.JSONDecodeError):
                return Execution("invalid_output", stdout=out, stderr=err, returncode=0)
            return Execution("ok", value, out, err, 0)
