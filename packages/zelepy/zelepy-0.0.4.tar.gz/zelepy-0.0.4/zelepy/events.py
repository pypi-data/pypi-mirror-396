import socket
import json
import threading
import base64
from typing import Callable, Dict, List, Optional, Any, Tuple
from pathlib import Path


class ZelesisClient:
    """
    Client for interacting with Zelesis Neo via UDP.
    
    Listens for broadcast events and can send commands to control the application.
    
    Example:
        >>> client = ZelesisClient()
        >>> client.subscribe("detection", lambda event: print(event))
        >>> client.start()
        >>> client.move_mouse(100, 50)
        >>> client.click_mouse()
    """
    
    DEFAULT_RECEIVE_PORT = 26512
    DEFAULT_SEND_PORT = 26513
    DEFAULT_TIMEOUT = 2.0
    DEFAULT_BUFFER_SIZE = 65535
    
    def __init__(
        self,
        receive_port: int = DEFAULT_RECEIVE_PORT,
        send_port: int = DEFAULT_SEND_PORT,
        target_ip: str = "127.0.0.1",
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the Zelesis client.
        
        Args:
            receive_port: Port to listen for broadcast events (default: 26512)
            send_port: Port to send commands to (default: 26513)
            target_ip: IP address of the Zelesis Neo instance (default: 127.0.0.1)
            timeout: Timeout for command responses in seconds (default: 2.0)
        """
        self.receive_port = receive_port
        self.send_port = send_port
        self.target_ip = target_ip
        self.timeout = timeout
        
        self._running = False
        self._listener_sock: Optional[socket.socket] = None
        self._command_sock: Optional[socket.socket] = None
        self._listener_thread: Optional[threading.Thread] = None
        
        # Event subscriptions: event_name -> list of callbacks
        self._subscriptions: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        
        # General event callbacks
        self._event_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def subscribe(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_name: Name of the event to subscribe to (e.g., "detection", "triggerbot")
            callback: Function to call when the event is received
        """
        if event_name not in self._subscriptions:
            self._subscriptions[event_name] = []
        self._subscriptions[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Optional[Callable] = None) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_name: Name of the event to unsubscribe from
            callback: Specific callback to remove. If None, removes all callbacks for the event.
        """
        if event_name not in self._subscriptions:
            return
        
        if callback is None:
            self._subscriptions[event_name].clear()
        else:
            self._subscriptions[event_name] = [
                cb for cb in self._subscriptions[event_name] if cb != callback
            ]
        
    
    def add_event_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a general event listener (receives all events). It is prefered to use subscribe() for specific events.
        
        Args:
            callback: Function to call for any event
        """
        self._event_callbacks.append(callback)
    
    def remove_event_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Remove a general event listener.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._event_callbacks:
            self._event_callbacks.remove(callback)
    
    def start(self) -> None:
        """
        Start listening for events in a background thread.
        """
        if self._running:
            return
        
        self._running = True
        
        # Create broadcast listener socket
        self._listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._listener_sock.bind(("", self.receive_port))
        
        # Create command socket
        self._command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._command_sock.settimeout(self.timeout)
        
        # Start listener thread
        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()
        
    
    def stop(self) -> None:
        """
        Stop listening for events and close sockets.
        """
        if not self._running:
            return
        
        self._running = False
        
        # Close sockets
        if self._listener_sock:
            try:
                self._listener_sock.close()
            except Exception as e:
                pass
            self._listener_sock = None
        
        if self._command_sock:
            try:
                self._command_sock.close()
            except Exception as e:
                pass
            self._command_sock = None
        
        # Wait for thread to finish
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1.0)
        
    
    def _listen_loop(self) -> None:
        if not self._listener_sock:
            return
        
        while self._running:
            try:
                data, addr = self._listener_sock.recvfrom(self.DEFAULT_BUFFER_SIZE)
                try:
                    event = json.loads(data.decode('utf-8'))
                    self._dispatch_event(event)
                except json.JSONDecodeError as e:
                    pass
                except UnicodeDecodeError as e:
                    pass
            except OSError:
                # Socket closed or interrupted
                if self._running:
                    pass
                break
            except Exception as e:
                pass
    
    def _dispatch_event(self, event: Dict[str, Any]) -> None:
        event_type = event.get("event")
        
        # Dispatch to specific subscribers
        if event_type and event_type in self._subscriptions:
            for callback in self._subscriptions[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    pass
        
        # Dispatch to general listeners
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                pass
    
    def send_command(
        self,
        command_data: Dict[str, Any],
        wait_response: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Send a command to Zelesis Neo.
        
        Args:
            command_data: Dictionary containing command data
            wait_response: Whether to wait for a response (default: False)
        
        Returns:
            Response dictionary if wait_response is True, None otherwise
        """
        if not self._command_sock:
            return None
        
        try:
            msg = json.dumps(command_data).encode('utf-8')
            self._command_sock.sendto(msg, (self.target_ip, self.send_port))
            
            if wait_response:
                try:
                    data, addr = self._command_sock.recvfrom(self.DEFAULT_BUFFER_SIZE)
                    response = json.loads(data.decode('utf-8'))
                    return response
                except socket.timeout:
                    return None
                except json.JSONDecodeError as e:
                    return None
        except Exception as e:
            return None
        
        return None
    
    def move_mouse(self, x: int, y: int) -> None:
        """
        Move the mouse by x, y pixels relative to its current position.
        
        Args:
            x: Horizontal movement in pixels
            y: Vertical movement in pixels
        """
        self.send_command({"command": "moveMouse", "x": x, "y": y})
    
    def click_mouse(self) -> None:
        """Trigger a left mouse click."""
        self.send_command({"command": "clickMouse"})
    
    def request_detection(self, image_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Request AI detection.
        
        If image_path is provided, detects objects in that image.
        Otherwise, detects objects on the current screen (ignoring pause state).
        
        Args:
            image_path: Optional path to an image file to analyze
        
        Returns:
            Detection results dictionary, or None if request failed
        """
        cmd: Dict[str, Any] = {"command": "requestDetection"}
        
        if image_path:
            try:
                image_path_obj = Path(image_path)
                if not image_path_obj.exists():
                    return None
                
                with open(image_path_obj, "rb") as f:
                    img_bytes = f.read()
                    b64 = base64.b64encode(img_bytes).decode('utf-8')
                    cmd["image_data"] = b64
            except Exception as e:
                return None
        
        return self.send_command(cmd, wait_response=True)
    
    def request_detection_raw(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Request detection on raw image bytes.
        
        Args:
            image_bytes: Raw image data as bytes
        
        Returns:
            Detection results dictionary, or None if request failed
        """
        try:
            b64 = base64.b64encode(image_bytes).decode('utf-8')
            cmd = {"command": "requestDetection", "image_data": b64}
            return self.send_command(cmd, wait_response=True)
        except Exception as e:
            return None
    
    def set_target_ip(self, ip: str) -> None:
        """
        Set the target IP address for commands.
        
        Args:
            ip: IP address of the Zelesis Neo instance
        """
        self.target_ip = ip
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

