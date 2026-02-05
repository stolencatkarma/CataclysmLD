"""Network and connection management for the client."""

import json
import threading
import time
from typing import Any, Optional, Callable
from src.mastermind._mm_client import MastermindClientTCP
from src.command import Command


class NetworkManager:
    """Handles all network communication with the server."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6317):
        self.host = host
        self.port = port
        self.client = MastermindClientTCP(timeout_connect=5.0, timeout_receive=1.0)
        self.connected = False
        self.running = True
        
        # Message handling
        self.receive_thread = None
        self.receive_lock = threading.Lock()
        self.message_queue = []
        self.message_callback: Optional[Callable] = None
        
    def connect(self) -> bool:
        """Connect to the game server."""
        try:
            self.client.connect(self.host, self.port)
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the game server."""
        if self.connected:
            self.running = False
            self.client.disconnect()
            self.connected = False
            print("Disconnected from server")
    
    def send_command(self, command: str, args: Any = None, ident: str = ""):
        """Send a command to the server."""
        if not self.connected:
            return
        try:
            cmd = Command(ident, command, args)
            message = json.dumps(cmd)
            self.client.send(message)
        except Exception as e:
            print(f"Failed to send command: {e}")
    
    def _receive_loop(self):
        """Background thread to receive messages from server."""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.client.receive(blocking=False)
                if data:
                    buffer += data
                    # Try to parse complete JSON objects from the buffer
                    while True:
                        try:
                            obj, idx = json.JSONDecoder().raw_decode(buffer)
                            with self.receive_lock:
                                self.message_queue.append(obj)
                            buffer = buffer[idx:].lstrip()
                        except Exception:
                            break
                time.sleep(0.01)
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
    
    def process_messages(self) -> list:
        """Get all pending messages from the queue."""
        messages = []
        with self.receive_lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        return messages
