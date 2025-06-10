#!/usr/bin/env python3
"""
MCP-only messaging server (no UI, for Claude Desktop integration)
"""

from fastmcp import FastMCP
import httpx
import asyncio
from viewer import MessageViewer
import threading
from typing import Optional
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import time
import sys
import os

# Global variables
mcp = FastMCP("Messaging")
viewer = MessageViewer()
partner_url: Optional[str] = None

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    from_user: str = "Partner"

# Create webhook app
webhook_app = FastAPI()

# MCP Tools
@mcp.tool()
def set_partner_url(url: str) -> str:
    """Set the partner's Ngrok URL for sending messages"""
    global partner_url
    
    # Clean up the URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    if url.endswith('/'):
        url = url[:-1]
    
    partner_url = url
    
    # Log to file since we can't show UI
    with open('messaging.log', 'a') as f:
        f.write(f"Partner URL set to: {url}\n")
    
    return f"Partner URL set to: {url}"


@mcp.tool()
async def send_message(message: str) -> str:
    """Send a message to your partner via their Ngrok URL"""
    global partner_url
    
    if not partner_url:
        return "Error: Partner URL not set. Use set_partner_url first."
    
    try:
        # For Ngrok URLs, don't add port (they handle routing)
        webhook_url = partner_url
        if 'localhost' in webhook_url:
            # For localhost, explicitly add port 8001
            if ':8001' not in webhook_url:
                webhook_url += ':8001'
        
        webhook_url += '/receive_message'
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                json={
                    "message": message,
                    "from_user": "Partner"
                }
            )
            
            if response.status_code == 200:
                # Log to file
                with open('messaging.log', 'a') as f:
                    f.write(f"You: {message}\n")
                return f"Message sent successfully: {message}"
            else:
                return f"Failed to send message. Status: {response.status_code}"
                
    except httpx.TimeoutException:
        return "Error: Request timed out. Check if partner's server is running."
    except httpx.ConnectError:
        return "Error: Could not connect to partner. Check the URL and network."
    except Exception as e:
        return f"Error sending message: {str(e)}"


@mcp.tool()
def start_ui() -> str:
    """Start the Tkinter message viewer UI"""
    try:
        # Start UI in a separate process to avoid blocking MCP
        import subprocess
        subprocess.Popen([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'ui_launcher.py')
        ], 
        cwd=os.path.dirname(__file__))
        return "Message viewer UI started in separate window"
    except Exception as e:
        return f"Error starting UI: {e}"


@mcp.tool()
def get_messages() -> str:
    """Get recent messages from the message log"""
    try:
        if os.path.exists('messaging.log'):
            with open('messaging.log', 'r') as f:
                lines = f.readlines()
                recent = lines[-10:] if len(lines) > 10 else lines
                return "Recent messages:\n" + "".join(recent)
        else:
            return "No messages found"
    except Exception as e:
        return f"Error reading messages: {e}"


# Webhook endpoints (for receiving messages)
@webhook_app.get("/")
async def root():
    return {"message": "Claude Messaging Webhook Server", "status": "ok"}


@webhook_app.post("/receive_message")
async def receive_message_webhook(request: MessageRequest):
    """HTTP webhook endpoint called by partner to deliver messages"""
    try:
        message = request.message
        from_user = request.from_user
        
        if not message:
            return {"status": "error", "message": "No message provided"}
        
        # Log to file
        with open('messaging.log', 'a') as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {from_user}: {message}\n")
        
        return {"status": "success", "message": "Message received"}
        
    except Exception as e:
        return {"status": "error", "message": f"Error processing message: {str(e)}"}


# Webhook server functions
async def run_webhook_server():
    """Run the webhook FastAPI server"""
    config = uvicorn.Config(webhook_app, host="0.0.0.0", port=8001, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


def start_webhook_server():
    """Start the webhook server in a separate thread"""
    asyncio.run(run_webhook_server())


# Start webhook server when MCP starts
webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
webhook_thread.start()

# Log startup
with open('messaging.log', 'a') as f:
    f.write(f"=== MCP Messaging Server Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

if __name__ == "__main__":
    mcp.run()