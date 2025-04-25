# MCP Server Demo

A simple demonstration project for the Model Control Protocol (MCP) server implementation.
MCP client implementation will be provided in the future.

## Overview

This project demonstrates a simple MCP server built with FastMCP that provides several tools and resources for AI assistants to use:

- **News Article Fetching**: Query and retrieve news articles from WorldNewsAPI
- **Simple Calculation**: Basic addition functionality 
- **Weather Information**: Simple weather data retrieval
- **Dynamic Greeting**: Personalized greeting resource

## Setup

### Prerequisites

- Python 3.x
- Required Python packages (used for testing):
  - `mcp-server`
  - `worldnewsapi`

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   uv add mcp-server
   ```
   ```
   uv add worldnewsapi
   ```
   ```
   pip install mcp-server worldnewsapi
   ```

## Usage

### Running the Server

Run the server with Python: from MCP related configuration and restart the client, like claude desktop or cursor ide mcp.