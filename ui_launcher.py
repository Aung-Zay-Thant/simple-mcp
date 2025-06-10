#!/usr/bin/env python3
"""
Standalone UI launcher for the messaging system
"""

import time
import threading
from viewer import MessageViewer
import os


def monitor_log_file(viewer):
    """Monitor the messaging.log file for new messages and update UI"""
    last_size = 0
    
    while True:
        try:
            if os.path.exists('messaging.log'):
                current_size = os.path.getsize('messaging.log')
                
                if current_size > last_size:
                    with open('messaging.log', 'r') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                        
                        for line in new_lines:
                            line = line.strip()
                            if line and not line.startswith('==='):
                                # Parse log format: [timestamp] user: message
                                if ': ' in line:
                                    try:
                                        # Extract timestamp, user, and message
                                        if line.startswith('['):
                                            # Format: [timestamp] user: message
                                            parts = line.split('] ', 1)
                                            if len(parts) == 2:
                                                timestamp_part = parts[0] + ']'
                                                rest = parts[1]
                                                if ': ' in rest:
                                                    user, message = rest.split(': ', 1)
                                                    viewer.add_message(user, message)
                                        else:
                                            # Simple format: user: message
                                            user, message = line.split(': ', 1)
                                            viewer.add_message(user, message)
                                    except Exception as e:
                                        # If parsing fails, show the raw line
                                        viewer.add_message("System", line)
                    
                    last_size = current_size
            
            time.sleep(1)  # Check every second
            
        except Exception as e:
            print(f"Error monitoring log: {e}")
            time.sleep(5)


def main():
    """Main function to start the UI"""
    print("Starting Claude Messaging UI...")
    
    # Create viewer
    viewer = MessageViewer()
    viewer.load_messages()
    
    # Start log monitor thread
    monitor_thread = threading.Thread(target=monitor_log_file, args=(viewer,), daemon=True)
    monitor_thread.start()
    
    # Add welcome message
    viewer.add_message("System", "🚀 Claude Messaging UI Started!")
    viewer.add_message("System", "💡 This UI shows messages from your MCP server")
    viewer.add_message("System", "📱 Use Claude Desktop to send/receive messages")
    
    # Start UI on main thread
    viewer._run_ui()


if __name__ == "__main__":
    main()