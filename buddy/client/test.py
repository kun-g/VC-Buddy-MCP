import asyncio
from fastmcp import Client

client = Client("../server/main.py")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("ask_for_feedback", {"summary": name})
        for line in result:
            print(line.text)

asyncio.run(call_tool("Ford"))