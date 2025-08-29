from pathlib import Path


def test_python_ci_has_fastapi_job():
    """python-ci workflow should include FastAPI test job"""
    workflow = Path(".github/workflows/python-ci.yml").read_text(encoding="utf-8")
    assert "python-tests:" in workflow
    assert 'pytest -m "not fastapi" -vv' in workflow
    assert "python-fastapi-tests:" in workflow
    assert "pytest -m fastapi -vv" in workflow
