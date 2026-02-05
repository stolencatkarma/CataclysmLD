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
            # print(f"[NET] Sending: cmd={command}, ident={ident}, args={args}")
            self.client.send(message)
        except Exception as e:
            print(f"Failed to send command: {e}")
    
    def _receive_loop(self):
        """Background thread to receive messages from server."""
        buffer = ""
        print("[NET] Receive loop started")
        max_buffer_size = 1024 * 1024  # 1MB max
        
        while self.running and self.connected:
            try:
                data = self.client.receive(blocking=False)
                if data:
                    # print(f"[NET] Received raw data: {len(data)} bytes")
                    buffer += data
                    
                    # Safety: if buffer gets too large without valid JSON, clear it
                    if len(buffer) > max_buffer_size:
                        print(f"[NET] WARNING: Buffer exceeded {max_buffer_size} bytes, clearing. Content starts with: {buffer[:100]}")
                        buffer = ""
                        continue
                    
                    # Try to parse complete JSON objects from the buffer
                    while len(buffer) > 0:
                        # Skip leading whitespace and non-JSON characters
                        buffer = buffer.lstrip()
                        if not buffer:
                            break
                            
                        # If buffer doesn't start with JSON character, skip until we find one
                        if buffer[0] not in '{["-0123456789tfn':
                            # Find next JSON start
                            brace_pos = buffer.find('{')
                            bracket_pos = buffer.find('[')
                            
                            next_json = len(buffer)  # Default: skip all
                            if brace_pos >= 0:
                                next_json = min(next_json, brace_pos)
                            if bracket_pos >= 0:
                                next_json = min(next_json, bracket_pos)
                            
                            skipped = buffer[:next_json]
                            buffer = buffer[next_json:]
                            if skipped.strip():  # Only log if there's actual content
                                print(f"[NET] Skipped non-JSON: {skipped[:50]}...")
                            continue
                        
                        # Try to parse JSON
                        try:
                            obj, idx = json.JSONDecoder().raw_decode(buffer)
                            # print(f"[NET] Received: {obj}")
                            with self.receive_lock:
                                self.message_queue.append(obj)
                            buffer = buffer[idx:]
                        except json.JSONDecodeError as e:
                            # Incomplete JSON, wait for more data
                            # sample = buffer[:100].replace('\n', '\\n')
                            # print(f"[NET] Incomplete JSON at pos {e.pos}, waiting for more data. Sample: {sample}...")
                            break
                        except Exception as e:
                            print(f"[NET] Error parsing JSON: {e}")
                            import traceback
                            traceback.print_exc()
                            break
                time.sleep(0.01)
            except Exception as e:
                if self.running:
                    print(f"[NET] Receive loop exception: {e}")
                    import traceback
                    traceback.print_exc()
                break
        print("[NET] Receive loop ended")
    
    def process_messages(self) -> list:
        """Get all pending messages from the queue."""
        messages = []
        with self.receive_lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        return messages
