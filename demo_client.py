import asyncio

from fastmcp import Client

client = Client("http://localhost:8000/mcp", auth="oauth")


async def call_tool(name: str):
    async with client:
        result = await client.call_tool("read_file", {"path": name})
        print(result)


asyncio.run(call_tool("/path/to/file.txt"))
