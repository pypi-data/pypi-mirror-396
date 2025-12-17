import asyncio
import json
from pathlib import Path
import pandas as pd
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


# 取得資料檔案路徑（從套件目錄讀取）
DATA_FILE = Path(__file__).parent / "data.csv"


def load_case_data():
    """載入 CSV 檔案"""
    try:
        df = pd.read_csv(DATA_FILE)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到資料檔案: {DATA_FILE}")
    except Exception as e:
        raise Exception(f"讀取資料檔案時發生錯誤: {e}")


def search_case_by_id(case_id: str):
    """根據 case_id 查詢案件資訊"""
    df = load_case_data()

    # 搜尋符合的案件
    result = df[df['case_id'] == case_id]

    if result.empty:
        return None

    # 將結果轉換為字典並處理 NaN 值
    case_info = result.iloc[0].to_dict()

    # 將 NaN 轉換為 None（JSON null）
    for key, value in case_info.items():
        if pd.isna(value):
            case_info[key] = None

    return case_info


# 建立 MCP server
server = Server("case-search")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="search_case",
            description="根據案件編號(case_id)查詢案件資訊。輸入案件編號，回傳該案件的完整資訊，包括納稅人名稱、稅籍編號、稅目、申報類型、申報日期、申報金額、核定金額、案件狀態、承辦人、管轄機關及最後更新時間。",
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "案件編號，例如：2023-0001, 2024-0002, 2025-0001",
                    }
                },
                "required": ["case_id"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """執行工具"""
    if name == "search_case":
        case_id = arguments.get("case_id")

        if not case_id:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": "請提供案件編號(case_id)"}, ensure_ascii=False, indent=2)
                )
            ]

        try:
            case_info = search_case_by_id(case_id)

            if case_info is None:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"找不到案件編號 {case_id} 的資料"},
                            ensure_ascii=False,
                            indent=2
                        )
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(case_info, ensure_ascii=False, indent=2)
                )
            ]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"error": f"查詢時發生錯誤: {str(e)}"},
                        ensure_ascii=False,
                        indent=2
                    )
                )
            ]

    return [
        TextContent(
            type="text",
            text=json.dumps({"error": f"未知的工具: {name}"}, ensure_ascii=False, indent=2)
        )
    ]


async def run_server():
    """啟動 MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main() -> None:
    """主程式進入點"""
    asyncio.run(run_server())

