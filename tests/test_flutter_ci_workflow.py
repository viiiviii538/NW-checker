from pathlib import Path


def test_flutter_workflow_runs_flutter_test():
    """flutter-ci workflow should run flutter tests"""
    workflow = Path('.github/workflows/flutter-ci.yml').read_text()
    assert 'flutter test' in workflow
    assert 'flutter-actions/setup-flutter@v2' in workflow
