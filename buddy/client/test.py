import asyncio
from fastmcp import Client
import os

client = Client("buddy/server/main.py")

async def call_tool(summary: str):
    async with client:
        result = await client.call_tool("ask_for_feedback", {
            "summary": summary,
            "project_directory": os.getcwd()
        })
        for line in result:
            print(line.text)

def main():
    asyncio.run(call_tool("你赶紧看看有啥任务能继续的，然后告诉我"))

if __name__ == "__main__":
    main()