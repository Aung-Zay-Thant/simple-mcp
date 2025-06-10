import tkinter as tk
from tkinter import scrolledtext
import threading
from datetime import datetime
import json
from typing import List, Dict


class MessageViewer:
    def __init__(self):
        self.root = None
        self.text_widget = None
        self.messages: List[Dict] = []
        self.running = False
        
    def start(self):
        """Start the Tkinter UI in a separate thread"""
        if not self.running:
            self.running = True
            ui_thread = threading.Thread(target=self._run_ui, daemon=True)
            ui_thread.start()
    
    def _run_ui(self):
        """Run the Tkinter UI - should be called on the main thread"""
        self.running = True
        self.root = tk.Tk()
        self.root.title("Claude Messaging Viewer")
        self.root.geometry("600x400")
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        title_label = tk.Label(main_frame, text="Claude Messaging Viewer", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Scrolled text widget for messages
        self.text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        self.text_widget.tag_configure("own_message", foreground="blue")
        self.text_widget.tag_configure("partner_message", foreground="green")
        self.text_widget.tag_configure("timestamp", foreground="gray", font=("Arial", 8))
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready to receive messages...", 
                                   font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=(10, 0))
        
        # Restore any existing messages
        if self.messages:
            self._restore_messages()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start the UI loop
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window close event"""
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def add_message(self, from_user: str, message: str):
        """Add a message to the UI and message history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Store message
        msg_data = {
            "from_user": from_user,
            "message": message,
            "timestamp": timestamp
        }
        self.messages.append(msg_data)
        
        # Update UI if it's running
        if self.root and self.text_widget:
            self._update_ui(from_user, message, timestamp)
        
        # Save to file
        self._save_messages()
    
    def _update_ui(self, from_user: str, message: str, timestamp: str):
        """Update the UI with a new message - thread-safe"""
        def update():
            self.text_widget.config(state=tk.NORMAL)
            
            # Add timestamp
            self.text_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Add sender and message with appropriate styling
            if from_user.lower() == "you":
                self.text_widget.insert(tk.END, f"You: {message}\n", "own_message")
            else:
                self.text_widget.insert(tk.END, f"{from_user}: {message}\n", "partner_message")
            
            self.text_widget.config(state=tk.DISABLED)
            
            # Auto-scroll to bottom
            self.text_widget.see(tk.END)
            
            # Update status
            self.status_label.config(text=f"Last message: {timestamp}")
        
        # Schedule the update on the main thread
        if self.root:
            self.root.after(0, update)
    
    def _save_messages(self):
        """Save messages to a JSON file"""
        try:
            with open("inbox.json", "w") as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            print(f"Error saving messages: {e}")
    
    def load_messages(self):
        """Load messages from JSON file"""
        try:
            with open("inbox.json", "r") as f:
                self.messages = json.load(f)
                # Restore messages to UI if it's running
                if self.root and self.text_widget:
                    self._restore_messages()
        except FileNotFoundError:
            self.messages = []
        except Exception as e:
            print(f"Error loading messages: {e}")
            self.messages = []
    
    def _restore_messages(self):
        """Restore messages to the UI"""
        def restore():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            
            for msg in self.messages:
                from_user = msg["from_user"]
                message = msg["message"]
                timestamp = msg["timestamp"]
                
                self.text_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
                
                if from_user.lower() == "you":
                    self.text_widget.insert(tk.END, f"You: {message}\n", "own_message")
                else:
                    self.text_widget.insert(tk.END, f"{from_user}: {message}\n", "partner_message")
            
            self.text_widget.config(state=tk.DISABLED)
            self.text_widget.see(tk.END)
        
        if self.root:
            self.root.after(0, restore)
    
    def stop(self):
        """Stop the UI"""
        if self.root:
            self.root.quit()
            self.root.destroy()
        self.running = False