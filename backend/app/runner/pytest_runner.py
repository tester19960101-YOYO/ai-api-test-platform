import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PytestRunResult:
    exit_code: int
    stdout: str
    stderr: str
    report_path: Path
    log_path: Path
    results: list[dict]


class PytestRunner:
    project_root = Path(__file__).resolve().parents[3]

    def run(self, generated_project_path: Path, task_id: int) -> PytestRunResult:
        report_dir = self.project_root / "storage" / "reports" / f"execution_{task_id}"
        log_dir = self.project_root / "storage" / "logs" / f"execution_{task_id}"
        report_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)

        report_path = report_dir / "report.html"
        log_path = log_dir / "pytest.log"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "--html",
            str(report_path),
            "--self-contained-html",
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=generated_project_path,
                text=True,
                capture_output=True,
                timeout=300,
                check=False,
            )
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code = 124
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            stderr = f"{stderr}\npytest execution timed out after {exc.timeout} seconds".strip()
        except Exception as exc:
            exit_code = 1
            stdout = ""
            stderr = f"pytest runner failed: {exc}"
        log_path.write_text(
            f"COMMAND: {' '.join(command)}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}",
            encoding="utf-8",
        )
        return PytestRunResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            report_path=report_path,
            log_path=log_path,
            results=self._load_results(generated_project_path / "results" / "results.jsonl"),
        )

    def _load_results(self, result_file: Path) -> list[dict]:
        if not result_file.exists():
            return []
        results = []
        for line_no, line in enumerate(result_file.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as exc:
                results.append(
                    {
                        "status": "failed",
                        "error_message": f"invalid execution result JSON at line {line_no}: {exc}",
                        "assertion_result": {"items": [], "passed": False},
                    }
                )
        return results
