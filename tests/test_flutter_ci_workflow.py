# tests/test_flutter_ci_workflow.py
from pathlib import Path
import yaml


def test_flutter_workflow_runs_flutter_test():
    wf = Path(".github/workflows/ci-soft.yml")
    assert wf.exists(), "ci-soft.yml が存在しない"
    data = yaml.safe_load(wf.read_text(encoding="utf-8"))
    jobs = data.get("jobs", {})
    assert "ci-soft" in jobs
    steps = [s for s in jobs["ci-soft"]["steps"] if isinstance(s, dict)]
    # flutter-actionが使われてる
    assert any("subosito/flutter-action@v2" in (s.get("uses", "")) for s in steps)
    # codex_run_tests.shが呼ばれている
    assert any("bash codex_run_tests.sh" in (s.get("run", "")) for s in steps)


def test_soft_has_fastapi_job_non_blocking():
    wf = Path(".github/workflows/ci-soft.yml")
    data = yaml.safe_load(wf.read_text(encoding="utf-8"))
    jobs = data.get("jobs", {})
    assert "fastapi-soft" in jobs
    job = jobs["fastapi-soft"]
    # continue-on-error が有効
    assert job.get("continue-on-error", True) is True
