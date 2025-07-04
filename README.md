# Claude Messaging MCP Server

A real-time messaging system that integrates with Claude Desktop using the Model Context Protocol (MCP). This allows two users to send and receive messages instantly through Ngrok-exposed endpoints with a live Tkinter UI.

## 🚀 Features

- **Real-time messaging** between two users
- **Instant UI updates** using Tkinter (no polling)
- **MCP integration** with Claude Desktop
- **Ngrok support** for exposing local servers
- **Message persistence** with file logging
- **Color-coded messages** (your messages vs partner's)
- **Webhook endpoints** for message delivery
- **Background server management** with threading
- **Cross-platform compatibility** (macOS, Linux, Windows)

## 📋 Prerequisites

- **Python 3.11+** (required)
- **UV** (Python package manager)
- **Ngrok** (for exposing local server)
- **Claude Desktop** (for MCP integration)

## 🛠️ Installation & Setup

### 1. Initialize Project with UV

First, set up the project using UV:

```bash
# Create a new directory for the project
mkdir claude-messaging-mcp
cd claude-messaging-mcp

# Initialize UV project
uv init

# Add the required dependencies
uv add fastmcp>=2.7.1
uv add "mcp[cli]>=1.9.3"
uv add httpx>=0.25.0
uv add fastapi>=0.104.0
uv add "uvicorn[standard]>=0.24.0"

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# or .venv\Scripts\activate  # On Windows
```

### 2. Install and Setup Ngrok

```bash
# Install ngrok (choose your platform)
# macOS:
brew install ngrok

# Linux:
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Windows:
# Download from https://ngrok.com/download and add to PATH

# Setup ngrok authentication
# 1. Create account at https://ngrok.com/
# 2. Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
# 3. Run:
ngrok authtoken YOUR_AUTH_TOKEN_HERE
```

### 3. Clone or Create Project Files

Either clone this repository or create the following files in your project directory:

- `server_mcp.py` - Main MCP server with webhook endpoints
- `viewer.py` - Tkinter UI for message viewing
- `ui_launcher.py` - Standalone UI launcher
- `mcp_wrapper.py` - Wrapper for proper path resolution
- `pyproject.toml` - Project dependencies

## 🏃‍♂️ How to Run

### Step 1: Start the MCP Server

```bash
# Make sure you're in the project directory and virtual environment is activated
source .venv/bin/activate  # If not already activated

# Start the MCP server
python server_mcp.py
```

This will start:
- **MCP Server** (for Claude Desktop integration)
- **Webhook Server** on port 8001 (for receiving messages)
- **Background logging** to `messaging.log`

### Step 2: Expose Server with Ngrok

In a **new terminal**, expose port 8001:

```bash
ngrok http 8001
```

You'll see output like:
```
Session Status                online
Account                       Your Account (Plan: Free)
Version                       3.1.0
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8001
```

**Important:** Note the HTTPS URL (e.g., `https://abc123.ngrok.io`) - you'll need this!

### Step 3: Start UI (Optional)

To view messages in a GUI:

```bash
# In another terminal
python ui_launcher.py
```

## 🔧 Configure Claude Desktop

### Finding Claude Desktop Configuration

The configuration file location depends on your OS:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Adding MCP Server Configuration

Edit the Claude Desktop configuration file and add:

```json
{
  "mcpServers": {
    "messaging": {
      "command": "python",
      "args": ["/full/path/to/your/project/mcp_wrapper.py"],
      "cwd": "/full/path/to/your/project"
    }
  }
}
```

**Example for macOS:**
```json
{
  "mcpServers": {
    "messaging": {
      "command": "python",
      "args": ["/Users/username/claude-messaging-mcp/mcp_wrapper.py"],
      "cwd": "/Users/username/claude-messaging-mcp"
    }
  }
}
```

### Restart Claude Desktop

After editing the configuration, completely restart Claude Desktop for changes to take effect.

## 📱 How to Use

### 1. Set Partner URL

In Claude Desktop, use the MCP tool to set your partner's Ngrok URL:

```
set_partner_url("https://your-partners-ngrok-url.ngrok.io")
```

**Example:**
```
set_partner_url("https://abc123-def456.ngrok.io")
```

### 2. Send Messages

Send messages using:

```
send_message("Hello! This is my first message.")
```

### 3. View Messages

Messages can be viewed in several ways:

- **Tkinter UI:** If you started `ui_launcher.py`
- **File logging:** Check `messaging.log` file
- **Get recent messages:** Use the `get_messages()` tool in Claude Desktop

### 4. Start UI from Claude

You can also start the UI directly from Claude Desktop:

```
start_ui()
```

## 🛠️ MCP Tools Available

### `set_partner_url(url: str)`
Sets your partner's Ngrok URL for sending messages.

**Parameters:**
- `url`: The Ngrok HTTPS URL (with or without https:// prefix)

**Example:**
```
set_partner_url("https://abc123.ngrok.io")
```

### `send_message(message: str)`
Sends a message to your partner via their webhook endpoint.

**Parameters:**
- `message`: The text message to send

**Example:**
```
send_message("Hello from Claude!")
```

### `get_messages()`
Retrieves the last 10 messages from the message log.

**Example:**
```
get_messages()
```

### `start_ui()`
Starts the Tkinter message viewer UI in a separate window.

**Example:**
```
start_ui()
```

## 🎨 UI Features

The Tkinter message viewer provides:

- **Real-time message display** with timestamps
- **Color coding:** Blue for your messages, green for partner's
- **Auto-scrolling** to show latest messages
- **Message persistence** (saved to `inbox.json`)
- **Status updates** showing last message time
- **System notifications** for server status

## 🏗️ Architecture

```
claude-messaging-mcp/
├── server_mcp.py          # Main MCP server with webhook endpoints
├── viewer.py              # Tkinter MessageViewer class
├── ui_launcher.py         # Standalone UI launcher
├── mcp_wrapper.py         # Wrapper for proper path resolution
├── pyproject.toml         # Project dependencies and metadata
├── messaging.log          # Message log file (auto-created)
├── inbox.json            # UI message storage (auto-created)
├── .venv/                # Virtual environment (created by uv)
└── README.md             # This file
```

### Key Components:

1. **FastMCP Server**: Provides MCP tools for Claude Desktop integration
2. **FastAPI Webhook Server** (port 8001): Receives messages from partners
3. **Tkinter UI**: Real-time message display and management
4. **Message Storage**: Dual storage system (log file + JSON)
5. **Background Threading**: Non-blocking server operation

## 🌐 Network Setup

- **MCP Server:** Communication with Claude Desktop via stdin/stdout
- **Webhook Server:** `localhost:8001` (exposed via Ngrok)
- **Partner Communication:** HTTPS via Ngrok tunnels
- **UI Communication:** File-based monitoring of `messaging.log`

## 🐛 Troubleshooting

### Common Issues:

1. **"Partner URL not set" error:**
   - Use `set_partner_url()` first with your partner's Ngrok URL
   - Make sure the URL starts with `https://`

2. **Connection timeout:**
   - Check if partner's server is running
   - Verify Ngrok URL is correct and accessible
   - Test the URL in a web browser

3. **MCP server not appearing in Claude Desktop:**
   - Check the configuration file path and syntax
   - Ensure file paths are absolute, not relative
   - Restart Claude Desktop completely
   - Check Claude Desktop logs for errors

4. **UI not showing:**
   - Make sure you're not running in a headless environment
   - Check if Tkinter is properly installed
   - Try running `python ui_launcher.py` directly

5. **Messages not appearing:**
   - Check if webhook server is running on port 8001
   - Verify Ngrok is forwarding to port 8001
   - Check `messaging.log` for errors

### Debug Commands:

```bash
# Check if servers are running
lsof -i :8001  # Webhook server
ps aux | grep server_mcp  # MCP server process

# Test webhook directly
curl -X POST http://localhost:8001/receive_message \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "from_user": "curl"}'

# Check ngrok status
curl http://localhost:4040/api/tunnels

# View recent logs
tail -f messaging.log
```

### Environment Issues:

```bash
# Verify UV installation
uv --version

# Check Python version
python --version

# Verify dependencies
uv pip list

# Recreate virtual environment if needed
rm -rf .venv
uv venv
source .venv/bin/activate
uv sync
```

## 🔒 Security Notes

- **HTTPS Only:** Always use HTTPS Ngrok URLs for secure communication
- **Local Storage:** Messages are stored locally in `messaging.log` and `inbox.json`
- **No Authentication:** Current version has no authentication (suitable for trusted partners)
- **Firewall:** Ensure your firewall allows connections on port 8001
- **Ngrok Limits:** Free Ngrok accounts have connection limits

## 📊 Testing

### Manual Testing:

```bash
# Test the UI separately
python ui_launcher.py

# Test webhook endpoint
curl -X POST http://localhost:8001/ -v

# Send test message via webhook
curl -X POST http://localhost:8001/receive_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello World", "from_user": "Test"}'
```

### Integration Testing:

1. Start both servers (yours and partner's)
2. Exchange Ngrok URLs
3. Set partner URLs using `set_partner_url()`
4. Send test messages using `send_message()`
5. Verify messages appear in both UIs

## 🙏 Acknowledgments

This project is the result of a collaboration between human creativity and AI assistance:

- **Human Developer** - Vision, requirements, and real-world testing
- **Claude (Anthropic)** - Code implementation, architecture design, and documentation
- **GitHub Copilot** - Code suggestions, autocompletion, and development assistance
- **Claude Code Agent** - Advanced code analysis, refactoring, and architectural guidance

The combination of human insight and multiple AI capabilities demonstrates the power of human-AI collaboration in creating practical, real-world applications.

---

*Built with ❤️ using Human creativity + Claude AI + GitHub Copilot assistance*
