"""GeoIP ユーティリティ"""

from __future__ import annotations

from contextlib import closing

import httpx


def get_country(ip_addr: str, db_path: str | None = None) -> str | None:
    """指定 IP から国コード (ISO-3166) を取得する。

    1. ローカルの GeoIP2 データベースを参照。
    2. 取得できなければ ``ipapi.co`` の外部 API を利用。

    どちらも失敗した場合は ``None`` を返す。
    """
    db_path = db_path or "/usr/share/GeoIP/GeoLite2-Country.mmdb"

    # GeoIP2 データベースの利用を試みる
    try:  # pragma: no cover - 環境によっては DB が存在しない
        import geoip2.database

        with closing(geoip2.database.Reader(db_path)) as reader:
            geo_resp = reader.country(ip_addr)
            code = geo_resp.country.iso_code
            if code:
                return code.upper()
    except Exception:
        # DB が使えない場合は外部 API にフォールバック
        pass

    # 外部 API へのフォールバック
    try:
        resp = httpx.get(f"https://ipapi.co/{ip_addr}/country/", timeout=5)
        if resp.status_code == 200:
            code = resp.text.strip().upper()
            return code or None
    except httpx.HTTPError:
        pass
    return None
