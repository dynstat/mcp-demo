import asyncio
import sys
import os

print("DEBUG: Imports successful")
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

print("DEBUG: MCP imports successful")


async def main():
    print("DEBUG: Starting main()")
    print("Starting MCP client application...")

    # Set up server parameters for your server.py
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=None,
    )
    print(f"DEBUG: Server params created: {server_params}")

    try:
        async with stdio_client(server_params) as (read, write):
            print("DEBUG: stdio_client context entered")
            async with ClientSession(read, write) as session:
                print("DEBUG: ClientSession context entered")
                # Initialize the connection
                print("DEBUG: Attempting session.initialize()")
                await session.initialize()
                print("DEBUG: session.initialize() successful")

                # List available tools using session
                print("\n=== Available Tools ===")
                print("DEBUG: Attempting session.list_tools()")
                tools_result = await session.list_tools()
                print(f"DEBUG: Got tools result object: {tools_result}")

                if tools_result and tools_result.tools:
                    for tool in tools_result.tools:
                        print(f"- {tool.name}: {tool.description}")
                else:
                    print("No tools found or result object is empty.")

                # List available resource patterns using session
                print("\n=== Available Resources ===")
                print("DEBUG: Attempting session.list_resources()")

                resources_result = await session.list_resources()

                print(f"DEBUG: Got resources result: {resources_result}")

                resources_list = []
                if (
                    hasattr(resources_result, "resources")
                    and resources_result.resources
                ):
                    resources_list = resources_result.resources
                elif isinstance(resources_result, list):
                    resources_list = resources_result

                if resources_list:
                    for resource_info in resources_list:
                        print(f"- {resource_info}")
                else:
                    print("No resources found or result object is empty.")

                # Call the add tool using session
                print("\n=== Running 'add' Tool ===")
                print("DEBUG: Attempting session.call_tool('add')")
                add_result = await session.call_tool("add", {"a": 5, "b": 7})
                print(f"DEBUG: Got add_result: {add_result}")
                print(f"Result of 5 + 7 = {add_result}")

                # Call get_weather using session
                print("\n=== Running 'get_weather' Tool ===")
                print("DEBUG: Attempting session.call_tool('get_weather')")
                weather = await session.call_tool("get_weather", {"city": "London"})
                print(f"DEBUG: Got weather result: {weather}")
                print(f"Weather in London: {weather}")

                # Resolve greeting resource using session
                print("\n=== Resolving 'greeting://Alice' Resource ===")
                print("DEBUG: Attempting session.read_resource('greeting://Alice')")
                content, mime_type = await session.read_resource("greeting://Alice")
                print(f"DEBUG: Got greeting content: {content}, mime: {mime_type}")
                print(f"Greeting: {content} (MIME type: {mime_type})")

    except Exception as e:
        print(f"ERROR in async block: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("DEBUG: Script entry point (__main__)")
    try:
        asyncio.run(main())
        print("DEBUG: asyncio.run(main()) completed.")
    except Exception as e:
        print(f"ERROR during asyncio.run: {e}")
        import traceback

        traceback.print_exc()
