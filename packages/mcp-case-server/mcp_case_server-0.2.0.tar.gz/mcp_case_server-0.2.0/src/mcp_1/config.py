import os
import importlib.resources as ir

def resolve_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    # fallback: 內建 demo sqlite（唯讀）
    # sqlite URI 方式：mode=ro + uri=true
    # 注意：需確保 package data 有正確被打包與安裝
    try:
        demo_db = ir.files("mcp_1.data").joinpath("demo_cases.db")
        # 當使用 importlib.resources 時，返回的可能是 MultiplexedPath，轉為 string 路徑
        return f"sqlite+pysqlite:///{str(demo_db)}?mode=ro&uri=true"
    except Exception:
        # 開發環境 fallback (如果未安裝 package)
        return "sqlite+pysqlite:///src/mcp_1/data/demo_cases.db?mode=ro&uri=true"
