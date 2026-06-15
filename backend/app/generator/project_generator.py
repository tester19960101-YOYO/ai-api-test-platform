from pathlib import Path
import shutil
from typing import Any

import yaml
from jinja2 import Environment as JinjaEnvironment
from jinja2 import FileSystemLoader

from app.core.assertion_engine_v2 import build_swagger_assertions, fuse_assertions, normalize_ai_suggestions, normalize_user_assertions
from app.models.environment import Environment
from app.models.execution_task import ExecutionTask
from app.models.project import Project
from app.models.test_case import TestCase


class PytestProjectGenerator:
    template_dir = Path(__file__).resolve().parent / "templates" / "pytest_project"
    project_root = Path(__file__).resolve().parents[3]

    def __init__(self) -> None:
        self.jinja_env = JinjaEnvironment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=False,
            keep_trailing_newline=True,
        )

    def generate(
        self,
        project: Project,
        environment: Environment,
        task: ExecutionTask,
        test_cases: list[TestCase],
        timeout: int,
    ) -> Path:
        output_dir = self.project_root / "storage" / "generated" / f"project_{project.id}" / f"execution_{task.id}"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        environment_variables = environment.variables or {}
        context_timeout = int(environment_variables.get("timeout_seconds") or timeout)
        retry_count = int(environment_variables.get("retry_count") or 0)
        cases = [self._build_case_data(test_case, context_timeout) for test_case in test_cases]
        context = {
            "project": project,
            "environment": environment,
            "task": task,
            "timeout": context_timeout,
            "auth": self._build_auth_config(environment),
            "retry_count": retry_count,
            "cases": cases,
            "cases_yaml": yaml.safe_dump(cases, allow_unicode=True, sort_keys=False),
        }

        template_map = {
            "config/env.yaml.j2": "config/env.yaml",
            "core/client.py.j2": "core/client.py",
            "core/assertion.py.j2": "core/assertion.py",
            "core/extractor.py.j2": "core/extractor.py",
            "core/variable.py.j2": "core/variable.py",
            "core/logger.py.j2": "core/logger.py",
            "tests/test_api_template.py.j2": "tests/test_api.py",
            "cases/cases.yaml.j2": "cases/cases.yaml",
            "pytest.ini.j2": "pytest.ini",
            "requirements.txt.j2": "requirements.txt",
        }

        for template_name, relative_output in template_map.items():
            output_path = output_dir / relative_output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            content = self.jinja_env.get_template(template_name).render(**context)
            output_path.write_text(content, encoding="utf-8")

        (output_dir / "results").mkdir(exist_ok=True)
        return output_dir

    def _build_case_data(self, test_case: TestCase, timeout: int) -> dict[str, Any]:
        steps = test_case.steps or []
        if not steps:
            steps = [{"name": test_case.name, "request": {}}]

        return {
            "id": test_case.id,
            "name": test_case.name,
            "description": test_case.description,
            "api_endpoint_id": test_case.api_endpoint_id,
            "priority": test_case.priority,
            "variables": test_case.variables or {},
            "steps": [self._normalize_step(step, timeout) for step in steps],
            "assertions": test_case.assertions or [],
            "swagger_assertions": self._build_swagger_assertions(test_case),
            "ai_assertions": self._build_ai_assertions(test_case),
            "user_assertions": normalize_user_assertions(test_case.assertions or []),
            "final_assertions": self._build_final_assertions(test_case),
        }

    def _normalize_step(self, step: Any, timeout: int) -> dict[str, Any]:
        if not isinstance(step, dict):
            return {"name": "request", "request": {"timeout": timeout}}
        request = dict(step.get("request") or {})
        request.setdefault("method", "GET")
        request.setdefault("path", "/")
        request.setdefault("headers", {})
        request.setdefault("query", {})
        request.setdefault("path_params", {})
        request.setdefault("body", {})
        request.setdefault("timeout", timeout)
        return {
            "name": step.get("name") or "request",
            "request": request,
        }

    def _build_auth_config(self, environment: Environment) -> dict[str, Any]:
        variables = environment.variables or {}
        raw_auth_config = variables.get("auth_config_json") or {}
        auth_config = raw_auth_config if isinstance(raw_auth_config, dict) else {}
        return {
            "auth_type": variables.get("auth_type") or auth_config.get("auth_type") or "none",
            "token": variables.get("token") or auth_config.get("token") or "",
            "cookie": variables.get("cookie") or auth_config.get("cookie") or "",
            "auth_config": auth_config,
        }

    def _build_swagger_assertions(self, test_case: TestCase) -> list[dict[str, Any]]:
        if test_case.api_endpoint is None:
            return []
        return build_swagger_assertions(test_case.api_endpoint)

    def _build_ai_assertions(self, test_case: TestCase) -> list[dict[str, Any]]:
        variables = test_case.variables or {}
        return normalize_ai_suggestions(variables.get("ai_assertion_suggestions") or {})

    def _build_final_assertions(self, test_case: TestCase) -> list[dict[str, Any]]:
        fused = fuse_assertions(
            swagger_assertions=self._build_swagger_assertions(test_case),
            ai_assertions=self._build_ai_assertions(test_case),
            user_assertions=normalize_user_assertions(test_case.assertions or []),
        )
        return fused["final_assertions"]
