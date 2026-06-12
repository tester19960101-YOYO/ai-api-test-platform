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
        completed = subprocess.run(
            command,
            cwd=generated_project_path,
            text=True,
            capture_output=True,
            timeout=300,
            check=False,
        )
        log_path.write_text(
            f"COMMAND: {' '.join(command)}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}",
            encoding="utf-8",
        )
        return PytestRunResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            report_path=report_path,
            log_path=log_path,
            results=self._load_results(generated_project_path / "results" / "results.jsonl"),
        )

    def _load_results(self, result_file: Path) -> list[dict]:
        if not result_file.exists():
            return []
        results = []
        for line in result_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                results.append(json.loads(line))
        return results
