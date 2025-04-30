import asyncio
import sys
import os

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


async def main():
    print("Starting MCP client application...")

    # Set up server parameters for your server.py
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=None,
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # List available tools using session
                print("\n=== Available Tools ===")
                tools_result = await session.list_tools()

                if tools_result and tools_result.tools:
                    for tool in tools_result.tools:
                        desc_lines = tool.description.strip().split("\n")
                        print(f"- {tool.name}: {desc_lines[0].strip()}...")
                else:
                    print("No tools found.")

                # List available resource patterns using session
                print("\n=== Available Resources ===")
                resources_result = await session.list_resources()

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
                    print("No static resources found.")

                # Call the add tool using session
                print("\n=== Running 'add' Tool ===")
                add_result = await session.call_tool("add", {"a": 5, "b": 7})
                add_output = (
                    add_result.content[0].text
                    if add_result
                    and add_result.content
                    and hasattr(add_result.content[0], "text")
                    else str(add_result)
                )
                print(f"Result of 5 + 7 = {add_output}")

                # Call get_weather using session
                print("\n=== Running 'get_weather' Tool ===")
                weather = await session.call_tool("get_weather", {"city": "London"})
                weather_output = (
                    weather.content[0].text
                    if weather
                    and weather.content
                    and hasattr(weather.content[0], "text")
                    else str(weather)
                )
                print(f"Weather in London: {weather_output}")

                # Read greeting resource using session
                print("\n=== Reading 'greeting://Alice' Resource ===")

                # Unpack into more descriptive names
                resource_meta, resource_data = await session.read_resource(
                    "greeting://Alice"
                )

                # print(f"DEBUG: Got resource meta: {resource_meta}, data: {resource_data}") # Can uncomment for debug

                # Extract text and mime type from resource_data tuple
                greeting_text = "Could not extract greeting text"
                actual_mime_type = "N/A"

                # Check if resource_data is a tuple, long enough, and contains the expected list
                if (
                    isinstance(resource_data, tuple)
                    and len(resource_data) > 1
                    and isinstance(resource_data[1], list)
                    and resource_data[1]
                ):  # Check if the list is not empty

                    first_content_item = resource_data[1][
                        0
                    ]  # Get the first item from the list at index 1

                    if hasattr(first_content_item, "text"):
                        greeting_text = first_content_item.text
                    if hasattr(first_content_item, "mimeType"):
                        actual_mime_type = first_content_item.mimeType

                print(f"Greeting: {greeting_text} (MIME type: {actual_mime_type})")

            print("\nClient finished successfully.")

    except Exception as e:
        print(f"ERROR in async block: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ERROR during asyncio.run: {e}")
        import traceback

        traceback.print_exc()
