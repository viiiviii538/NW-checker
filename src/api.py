from datetime import datetime
from fastapi import FastAPI, HTTPException, Query

from .dynamic_scan import storage

app = FastAPI()


@app.get("/scan/dynamic/history")
def get_dynamic_history(
    from_: str = Query(..., alias="from"),
    to: str = Query(..., alias="to"),
):
    """指定期間の動的スキャン結果を返す。"""
    try:
        datetime.strptime(from_, "%Y-%m-%d")
        datetime.strptime(to, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    return storage.fetch_results(from_, to)
