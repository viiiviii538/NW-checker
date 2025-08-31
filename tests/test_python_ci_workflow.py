# tests/test_python_ci_workflow.py
from pathlib import Path
import yaml


def test_hard_workflow_calls_unified_script_in_hard_mode():
    wf = Path(".github/workflows/ci-hard.yml")
    assert wf.exists(), "ci-hard.yml が存在しない"
    data = yaml.safe_load(wf.read_text(encoding="utf-8"))
    jobs = data.get("jobs", {})
    assert "ci-hard" in jobs
    steps = [s for s in jobs["ci-hard"]["steps"] if isinstance(s, dict)]
    run_step = next(s for s in steps if "bash codex_run_tests.sh" in (s.get("run", "")))
    env = run_step.get("env", {})
    assert env.get("SOFT_CL") == "0"


def test_hard_has_fastapi_job_required():
    wf = Path(".github/workflows/ci-hard.yml")
    data = yaml.safe_load(wf.read_text(encoding="utf-8"))
    jobs = data.get("jobs", {})
    assert "fastapi-hard" in jobs
    steps = [s for s in jobs["fastapi-hard"]["steps"] if isinstance(s, dict)]
    assert any("pytest -m fastapi -vv" in (s.get("run", "")) for s in steps)
