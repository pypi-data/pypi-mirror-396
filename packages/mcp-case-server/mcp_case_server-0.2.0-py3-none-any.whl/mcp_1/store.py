from __future__ import annotations
from typing import Any, Dict, Optional
import json

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import resolve_database_url

def _engine() -> Engine:
    # pool_pre_ping：避免連線閒置後斷線
    return create_engine(resolve_database_url(), pool_pre_ping=True, future=True)

class CaseStore:
    def __init__(self, engine: Engine | None = None):
        self.engine = engine or _engine()

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        # 兼容兩種 schema：
        # A) demo：cases(case_id, payload TEXT)
        # B) 正式：你也可以改成 cases(case_id, customer, ..., payload JSONB)
        sql = text("SELECT case_id, payload FROM cases WHERE case_id = :case_id")

        with self.engine.connect() as conn:
            # 使用 mappings() 獲取類似 dict 的結果
            result = conn.execute(sql, {"case_id": case_id}).mappings().first()
            if not result:
                return None

            payload_raw = result.get("payload") or "{}"
            try:
                payload = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
            except Exception:
                payload = {"raw_payload": payload_raw}

            return {"case_id": result["case_id"], "payload": payload}
