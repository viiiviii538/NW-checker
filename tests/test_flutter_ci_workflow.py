from pathlib import Path


def test_flutter_workflow_runs_flutter_test():
    """flutter-ci workflow should run flutter tests"""
    # Explicit encoding avoids UnicodeDecodeError on Windows CI where the
    # default encoding may not be UTF-8
    workflow = Path('.github/workflows/flutter-ci.yml').read_text(encoding='utf-8')
    assert 'flutter test' in workflow
    assert 'flutter-actions/setup-flutter@v2' in workflow
