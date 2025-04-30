import subprocess
import json
import sys
import threading
import time
import itertools  # To generate unique IDs

# Command to run the server (adjust path as needed)
# On Windows, you might need to specify the python executable explicitly
server_command = [sys.executable, "server.py"]


# --- Function to read server output ---
# Basic version that just prints lines
def read_output(proc):
    try:
        while True:
            # Readline will block until a line is received or the pipe closes
            line = proc.stdout.readline()
            if not line:  # End of output (pipe closed)
                print("Server stdout pipe closed.")
                break
            # In a real client, parse the JSON and handle based on message ID/type
            print(f"Server Response: {line.strip()}")
    except Exception as e:
        print(f"Error reading server output: {e}", file=sys.stderr)
    finally:
        print("Output reading thread finished.")


# --- Function to send requests ---
# Helper to send JSON-RPC messages
request_id_counter = itertools.count()  # Simple way to get unique IDs


def send_request(proc, method, params):
    request_id = next(request_id_counter)
    message = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }
    message_str = json.dumps(message)
    print(f"Client Request (ID: {request_id}): {message_str}")
    try:
        # Write the message followed by a newline, as servers often read line by line
        print(message_str, file=proc.stdin, flush=True)
    except (OSError, BrokenPipeError) as e:
        print(f"Failed to send request (ID: {request_id}): {e}", file=sys.stderr)
        return False
    return True


# --- Main Execution ---
print("Starting server process...")
process = subprocess.Popen(
    server_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,  # Use text mode (auto encodes/decodes)
    encoding="utf-8",  # Be explicit about encoding
    bufsize=1,  # Line-buffered is crucial for stdio communication because:
    # 1. It ensures each complete line is sent immediately without waiting for buffer to fill
    # 2. MCP protocol uses line-delimited JSON messages, so we need line-by-line processing
    # 3. Without line buffering, messages might get stuck in the buffer, causing delays
    # 4. It prevents partial JSON messages from being processed, which would cause parsing errors
    # 5. Enables real-time communication between client and server processes
)

print("Starting output reader thread...")
output_thread = threading.Thread(target=read_output, args=(process,), daemon=True)
# daemon=True allows the main program to exit even if this thread is blocking,
# though we will still explicitly join it later for cleaner shutdown.
output_thread.start()

# Allow server a moment to start up
time.sleep(1)

print("Sending Initialize request...")
initialize_params = {
    "client_info": {"name": "MyCustomClient", "version": "0.1.0"},  # Basic client info
    "protocol_version": "1.0",  # Specify the MCP version
    # Add other capabilities here if needed, consult MCP spec
}
if not send_request(process, "initialize", initialize_params):
    print("Failed to send initialize request, exiting.", file=sys.stderr)
    # Consider cleanup here if needed
    sys.exit(1)

# Wait a moment for the server to potentially process initialize
time.sleep(0.5)

print("Sending tool/run request...")
tool_params = {"tool_name": "add", "arguments": {"a": 5, "b": 7}}
send_request(process, "tool/run", tool_params)

# Wait a moment
time.sleep(0.5)

print("Sending resource/resolve request...")
resource_params = {"resource_uri": "greeting://Alice"}
send_request(process, "resource/resolve", resource_params)

# --- Cleanup ---
print("\n--- Starting Client Cleanup ---")
time.sleep(1)  # Allow time for last responses

# Close server's stdin - signals no more input is coming
print("Client: Closing server stdin...")
try:
    if process.stdin and not process.stdin.closed:
        process.stdin.close()
except OSError as e:
    print(f"Client: Error closing stdin (might be ok): {e}", file=sys.stderr)

# Attempt graceful termination
print("Client: Attempting to terminate server process...")
try:
    process.terminate()
except ProcessLookupError:
    print("Client: Server process already terminated.", file=sys.stderr)
except OSError as e:
    print(f"Client: Error during terminate: {e}", file=sys.stderr)

# Wait for termination with timeout
print("Client: Waiting for server process to exit (max 5 seconds)...")
try:
    exit_code = process.wait(timeout=5)
    print(f"Client: Server process exited with code {exit_code}.")
except subprocess.TimeoutExpired:
    print(
        "Client: Server process did not terminate gracefully, killing...",
        file=sys.stderr,
    )
    process.kill()
    try:
        exit_code = process.wait(timeout=2)
        print(f"Client: Server process killed and exited with code {exit_code}.")
    except subprocess.TimeoutExpired:
        print("Client: Server process failed to exit even after kill.", file=sys.stderr)
except Exception as e:
    print(f"Client: Error during process wait: {e}", file=sys.stderr)

# Wait for the output reading thread
# Since it's a daemon thread, it might have already exited if the process closed stdout
print("Client: Waiting for output thread to finish (max 5 seconds)...")
output_thread.join(timeout=5)
if output_thread.is_alive():
    print("Client: Output thread still alive after timeout.", file=sys.stderr)

# Check for remaining stderr
print("Client: Checking for final server stderr...")
try:
    # Give stderr a moment to flush after process termination
    time.sleep(0.1)
    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"--- Final Server Stderr Output ---", file=sys.stderr)
        print(stderr_output.strip(), file=sys.stderr)
        print(f"----------------------------------", file=sys.stderr)
    else:
        print("Client: No final stderr output detected.")
except Exception as e:
    print(f"Client: Error reading final stderr: {e}", file=sys.stderr)

print("\nClient finished.")
