#!/usr/bin/env python3
"""FastMCP Server runner for Vibe Coding Buddy."""
from fastmcp import FastMCP
import subprocess
import json

mcp = FastMCP(
    name="Vibe Coding Buddy",
    instructions="This is a test server for Vibe Coding Buddy.",
)

@mcp.tool()
def ask_for_feedback(
    summary: str,
) -> str:
    print("ask_for_feedback", summary)
    # 启动 ui/answer_box.py,获取 stdout
    process = subprocess.Popen(["python", "buddy/ui/answer_box.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    process.stdin.write(json.dumps({"summary": summary}, ensure_ascii=False))
    process.stdin.flush()
    stdout, _ = process.communicate()
    return stdout

if __name__ == "__main__":
    mcp.run(transport="stdio")