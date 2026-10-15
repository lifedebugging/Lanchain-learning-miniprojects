import asyncio
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

app = Server("janus-engine")

#the Discovery 
@app.list_tools()
async def list_my_tools():
    return [
        Tool(
            name = "get_datetime",
            description="Returns current date and time with accuracy",
            inputSchema={"types" : "object", "properties": {}},
            )
        ]

# the Logic (The Switchboard)
@app.call_tool()
async def execute_tool(name, args):
    if name == "get_datetime":
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return [TextContent(type="text", 
                            text = f"The time is {current_datetime}"
                           )]
    else:
    # Architect Tip: Always handle the "unknown tool" case
        raise ValueError(f"Tool not found : {name}")

#the Transport (The Pipes)
async def main():
    #1. (The stdio pipes)
    async with stdio_server() as (read, write):
        # 2. Start the brain (The server)
        await app.run(read, 
                      write, 
                      app.create_initialization_options(), # These are the handshake settings
                      )

if __name__ == "__main__":
    asyncio.run(main())

