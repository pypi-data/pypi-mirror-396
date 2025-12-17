from __future__ import annotations
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from .store import CaseStore

mcp = FastMCP("Case MCP")
store = CaseStore()

@mcp.tool()
def get_case(case_id: str) -> Dict[str, Any]:
    """
    以案件編號查詢案件資料。
    - 若未設定 DATABASE_URL，會用套件內建 demo SQLite（唯讀）
    - 若有設定 DATABASE_URL，改連使用者資料庫
    """
    case_id = (case_id or "").strip()
    if not case_id:
        return {"found": False, "reason": "case_id is required"}

    try:
        data = store.get_case(case_id)
        if not data:
            return {"found": False, "case_id": case_id, "reason": "not found"}

        return {"found": True, "case": data}
    except Exception as e:
        return {"found": False, "case_id": case_id, "error": str(e)}

def main():
    # stdio：讓 MCP client 以子程序 stdin/stdout 跟你通訊
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
