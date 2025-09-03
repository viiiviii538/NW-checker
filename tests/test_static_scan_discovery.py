import sys
import time
import types

import pytest

# 外部依存ライブラリが存在しない場合に限りスタブを登録
try:  # pragma: no cover - 実環境では本物が入るため
    import nmap  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    sys.modules.setdefault("nmap", types.SimpleNamespace(PortScanner=lambda: None))

try:  # pragma: no cover - 実環境では本物が入るため
    import scapy.all  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    scapy_stub = types.SimpleNamespace(
        all=types.SimpleNamespace(
            IP=None,
            UDP=None,
            Raw=None,
            sr1=lambda *a, **k: None,
            ARP=None,
            send=lambda *a, **k: None,
            Ether=None,
            BOOTP=None,
            DHCP=None,
            srp=lambda *a, **k: ([], []),
            DNS=None,
            DNSQR=None,
        )
    )
    sys.modules.setdefault("scapy", scapy_stub)
    sys.modules.setdefault("scapy.all", scapy_stub.all)

from src import static_scan

pytestmark = pytest.mark.nmap


def test_load_scanners_discovers_modules():
    scanners = static_scan._load_scanners()
    names = {name for name, _ in scanners}
    # Ensure common scan modules are discovered
    assert {"ports", "os_banner"}.issubset(names)


def test_run_all_executes_scanners_concurrently(monkeypatch):
    """Scans should run in parallel to reduce total execution time."""

    def make_slow(name):
        def slow_scan():
            time.sleep(1)
            return {"category": name, "score": 1, "details": {}}

        return slow_scan

    monkeypatch.setattr(
        static_scan,
        "_load_scanners",
        lambda: [("slow1", make_slow("slow1")), ("slow2", make_slow("slow2"))],
    )

    start = time.perf_counter()
    result = static_scan.run_all()
    elapsed = time.perf_counter() - start

    # Would take ~2s sequentially; concurrent run should be significantly faster
    assert elapsed < 1.8
    assert result["risk_score"] == 2
    categories = [item["category"] for item in result["findings"]]
    assert {"slow1", "slow2"} == set(categories)


def test_load_scanners_skips_private_and_non_scan_modules(tmp_path, monkeypatch):
    """プライベート or scan関数未定義モジュールを無視することを確認"""

    # ダミーモジュールを一時ディレクトリに作成
    (tmp_path / "good.py").write_text(
        "def scan():\n    return {'category': 'good', 'score': 1, 'details': {}}\n"
    )
    (tmp_path / "no_scan.py").write_text("value = 1\n")
    (tmp_path / "_hidden.py").write_text(
        "def scan():\n    return {'category': '_hidden', 'score': 1, 'details': {}}\n"
    )

    # scans パッケージの探索パスを差し替え
    monkeypatch.setattr(static_scan.scans, "__path__", [str(tmp_path)])

    scanners = static_scan._load_scanners()
    names = [name for name, _ in scanners]
    assert names == ["good"]

    # run_all でも同様に good モジュールのみが実行されることを確認
    result = static_scan.run_all()
    assert result["findings"] == [{"category": "good", "score": 1, "details": {}}]
    assert result["risk_score"] == 1
