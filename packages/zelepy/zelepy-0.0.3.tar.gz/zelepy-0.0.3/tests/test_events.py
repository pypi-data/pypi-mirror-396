"""
Tests for zelepy.events

Run tests via: 
pytest test_events.py -v

Remember to test while in venv
"""

import pytest
import json
import socket
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from zelepy.events import ZelesisClient


class TestZelesisClientInitialization:
    """Test ZelesisClient initialization."""
    
    def test_default_initialization(self):
        """Test client initialization with default parameters."""
        client = ZelesisClient()
        
        assert client.broadcast_port == ZelesisClient.DEFAULT_BROADCAST_PORT
        assert client.command_port == ZelesisClient.DEFAULT_COMMAND_PORT
        assert client.target_ip == "127.0.0.1"
        assert client.timeout == ZelesisClient.DEFAULT_TIMEOUT
        assert client.is_running is False
        assert client._subscriptions == {}
        assert client._event_callbacks == []
    
    
    def test_custom_timeout_initialization(self):
        """Test client initialization with custom timeout."""
        client = ZelesisClient(timeout=5.0)
        
        assert client.timeout == 5.0
        assert client.is_running is False


class TestEventSubscription:
    """Test event subscription and unsubscription."""
    
    def test_subscribe_single_callback(self):
        """Test subscribing a single callback to an event."""
        client = ZelesisClient()
        callback = Mock()
        
        client.subscribe("detection", callback)
        
        assert "detection" in client._subscriptions
        assert len(client._subscriptions["detection"]) == 1
        assert callback in client._subscriptions["detection"]
    
    def test_subscribe_multiple_callbacks(self):
        """Test subscribing multiple callbacks to the same event."""
        client = ZelesisClient()
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()
        
        client.subscribe("detection", callback1)
        client.subscribe("detection", callback2)
        client.subscribe("triggerbot", callback3)
        
        assert len(client._subscriptions["detection"]) == 2
        assert callback1 in client._subscriptions["detection"]
        assert callback2 in client._subscriptions["detection"]
        assert len(client._subscriptions["triggerbot"]) == 1
        assert callback3 in client._subscriptions["triggerbot"]
    
    def test_unsubscribe_specific_callback(self):
        """Test unsubscribing a specific callback."""
        client = ZelesisClient()
        callback1 = Mock()
        callback2 = Mock()
        
        client.subscribe("detection", callback1)
        client.subscribe("detection", callback2)
        client.unsubscribe("detection", callback1)
        
        assert len(client._subscriptions["detection"]) == 1
        assert callback1 not in client._subscriptions["detection"]
        assert callback2 in client._subscriptions["detection"]
    
    def test_unsubscribe_all_callbacks(self):
        """Test unsubscribing all callbacks for an event."""
        client = ZelesisClient()
        callback1 = Mock()
        callback2 = Mock()
        
        client.subscribe("detection", callback1)
        client.subscribe("detection", callback2)
        client.unsubscribe("detection")
        
        assert len(client._subscriptions["detection"]) == 0
    
    def test_unsubscribe_nonexistent_event(self):
        """Test unsubscribing from an event that doesn't exist."""
        client = ZelesisClient()
        
        # Should not raise an error
        client.unsubscribe("nonexistent")
        assert "nonexistent" not in client._subscriptions


class TestEventListeners:
    """Test general event listeners."""
    
    def test_add_event_listener(self):
        """Test adding a general event listener."""
        client = ZelesisClient()
        callback = Mock()
        
        client.add_event_listener(callback)
        
        assert len(client._event_callbacks) == 1
        assert callback in client._event_callbacks
    
    def test_add_multiple_event_listeners(self):
        """Test adding multiple general event listeners."""
        client = ZelesisClient()
        callback1 = Mock()
        callback2 = Mock()
        
        client.add_event_listener(callback1)
        client.add_event_listener(callback2)
        
        assert len(client._event_callbacks) == 2
        assert callback1 in client._event_callbacks
        assert callback2 in client._event_callbacks
    
    def test_remove_event_listener(self):
        """Test removing a general event listener."""
        client = ZelesisClient()
        callback1 = Mock()
        callback2 = Mock()
        
        client.add_event_listener(callback1)
        client.add_event_listener(callback2)
        client.remove_event_listener(callback1)
        
        assert len(client._event_callbacks) == 1
        assert callback1 not in client._event_callbacks
        assert callback2 in client._event_callbacks
    
    def test_remove_nonexistent_event_listener(self):
        """Test removing an event listener that doesn't exist."""
        client = ZelesisClient()
        callback = Mock()
        
        # Should not raise an error
        client.remove_event_listener(callback)
        assert callback not in client._event_callbacks


class TestClientStartStop:
    """Test client start and stop functionality."""
    
    @patch('socket.socket')
    def test_start_creates_sockets(self, mock_socket_class):
        """Test that start() creates the necessary sockets."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        # Should create two sockets
        assert mock_socket_class.call_count == 2
        assert client.is_running is True
        assert client._listener_thread is not None
        assert client._listener_thread.is_alive()
        
        client.stop()
    
    @patch('socket.socket')
    def test_start_idempotent(self, mock_socket_class):
        """Test that calling start() multiple times doesn't create multiple threads."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        thread1 = client._listener_thread
        
        client.start()  # Call again
        
        thread2 = client._listener_thread
        
        # Should be the same thread
        assert thread1 == thread2
        
        client.stop()
    
    @patch('socket.socket')
    def test_stop_closes_sockets(self, mock_socket_class):
        """Test that stop() closes sockets properly."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        client.stop()
        
        # Should close sockets
        assert mock_socket.close.call_count == 2
        assert client.is_running is False
        assert client._listener_sock is None
        assert client._command_sock is None
    
    @patch('socket.socket')
    def test_stop_idempotent(self, mock_socket_class):
        """Test that calling stop() multiple times doesn't raise errors."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        client.stop()
        client.stop()  # Call again
        
        # Should not raise an error
        assert client.is_running is False


class TestEventDispatching:
    """Test event dispatching to subscribers and listeners."""
    
    def test_dispatch_to_subscribed_callback(self):
        """Test that events are dispatched to subscribed callbacks."""
        client = ZelesisClient()
        callback = Mock()
        
        client.subscribe("detection", callback)
        
        event = {"event": "detection", "data": "test"}
        client._dispatch_event(event)
        
        callback.assert_called_once_with(event)
    
    def test_dispatch_to_multiple_subscribed_callbacks(self):
        """Test that events are dispatched to all subscribed callbacks."""
        client = ZelesisClient()
        callback1 = Mock()
        callback2 = Mock()
        
        client.subscribe("detection", callback1)
        client.subscribe("detection", callback2)
        
        event = {"event": "detection", "data": "test"}
        client._dispatch_event(event)
        
        callback1.assert_called_once_with(event)
        callback2.assert_called_once_with(event)
    
    def test_dispatch_to_general_listeners(self):
        """Test that events are dispatched to general listeners."""
        client = ZelesisClient()
        callback = Mock()
        
        client.add_event_listener(callback)
        
        event = {"event": "detection", "data": "test"}
        client._dispatch_event(event)
        
        callback.assert_called_once_with(event)
    
    def test_dispatch_to_both_subscribers_and_listeners(self):
        """Test that events are dispatched to both subscribers and general listeners."""
        client = ZelesisClient()
        subscriber_callback = Mock()
        listener_callback = Mock()
        
        client.subscribe("detection", subscriber_callback)
        client.add_event_listener(listener_callback)
        
        event = {"event": "detection", "data": "test"}
        client._dispatch_event(event)
        
        subscriber_callback.assert_called_once_with(event)
        listener_callback.assert_called_once_with(event)
    
    def test_dispatch_only_matching_event_type(self):
        """Test that callbacks only receive events matching their subscription."""
        client = ZelesisClient()
        detection_callback = Mock()
        triggerbot_callback = Mock()
        
        client.subscribe("detection", detection_callback)
        client.subscribe("triggerbot", triggerbot_callback)
        
        event = {"event": "detection", "data": "test"}
        client._dispatch_event(event)
        
        detection_callback.assert_called_once_with(event)
        triggerbot_callback.assert_not_called()
    
    def test_dispatch_event_without_event_type(self):
        """Test dispatching an event without an 'event' field."""
        client = ZelesisClient()
        callback = Mock()
        
        client.add_event_listener(callback)
        
        event = {"data": "test"}
        client._dispatch_event(event)
        
        # General listeners should still receive it
        callback.assert_called_once_with(event)
    
    def test_dispatch_handles_callback_exception(self):
        """Test that exceptions in callbacks don't break dispatching."""
        client = ZelesisClient()
        bad_callback = Mock(side_effect=Exception("Test error"))
        good_callback = Mock()
        
        client.subscribe("detection", bad_callback)
        client.subscribe("detection", good_callback)
        
        event = {"event": "detection", "data": "test"}
        
        # Should not raise an exception
        client._dispatch_event(event)
        
        bad_callback.assert_called_once()
        good_callback.assert_called_once()


class TestCommandSending:
    """Test command sending functionality."""
    
    @patch('socket.socket')
    def test_send_command(self, mock_socket_class):
        """Test sending a command."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        command_data = {"command": "test", "value": 123}
        client.send_command(command_data)
        
        # Verify socket.sendto was called
        assert mock_socket.sendto.called
        call_args = mock_socket.sendto.call_args
        sent_data = json.loads(call_args[0][0].decode('utf-8'))
        assert sent_data == command_data
        
        client.stop()
    
    @patch('socket.socket')
    def test_send_command_with_response(self, mock_socket_class):
        """Test sending a command and waiting for response."""
        mock_socket = Mock()
        mock_response = json.dumps({"status": "ok"}).encode('utf-8')
        mock_socket.recvfrom.return_value = (mock_response, ("127.0.0.1", 12345))
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        command_data = {"command": "test"}
        response = client.send_command(command_data, wait_response=True)
        
        assert response is not None
        assert response["status"] == "ok"
        
        client.stop()
    
    @patch('socket.socket')
    def test_send_command_timeout(self, mock_socket_class):
        """Test that command timeout is handled."""
        mock_socket = Mock()
        mock_socket.recvfrom.side_effect = socket.timeout()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        command_data = {"command": "test"}
        response = client.send_command(command_data, wait_response=True)
        
        assert response is None
        
        client.stop()
    
    @patch('socket.socket')
    def test_send_command_when_not_started(self, mock_socket_class):
        """Test sending command when client is not started."""
        client = ZelesisClient()
        
        command_data = {"command": "test"}
        response = client.send_command(command_data)
        
        assert response is None


class TestMouseCommands:
    """Test mouse command methods."""
    
    @patch('socket.socket')
    def test_move_mouse(self, mock_socket_class):
        """Test move_mouse command."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        client.move_mouse(100, 50)
        
        # Verify command was sent
        assert mock_socket.sendto.called
        call_args = mock_socket.sendto.call_args
        sent_data = json.loads(call_args[0][0].decode('utf-8'))
        assert sent_data["command"] == "moveMouse"
        assert sent_data["x"] == 100
        assert sent_data["y"] == 50
        
        client.stop()
    
    @patch('socket.socket')
    def test_click_mouse(self, mock_socket_class):
        """Test click_mouse command."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        client.click_mouse()
        
        # Verify command was sent
        assert mock_socket.sendto.called
        call_args = mock_socket.sendto.call_args
        sent_data = json.loads(call_args[0][0].decode('utf-8'))
        assert sent_data["command"] == "clickMouse"
        
        client.stop()


class TestDetectionRequests:
    """Test detection request methods."""
    
    @patch('socket.socket')
    def test_request_detection_without_image(self, mock_socket_class):
        """Test request_detection without image path."""
        mock_socket = Mock()
        mock_response = json.dumps({"detections": []}).encode('utf-8')
        mock_socket.recvfrom.return_value = (mock_response, ("127.0.0.1", 12345))
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        response = client.request_detection()
        
        assert response is not None
        assert "detections" in response
        
        # Verify command was sent
        call_args = mock_socket.sendto.call_args
        sent_data = json.loads(call_args[0][0].decode('utf-8'))
        assert sent_data["command"] == "requestDetection"
        assert "image_data" not in sent_data
        
        client.stop()
    
    @patch('socket.socket')
    @patch('pathlib.Path')
    def test_request_detection_nonexistent_image(self, mock_path_class, mock_socket_class):
        """Test request_detection with nonexistent image path."""
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path
        
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        response = client.request_detection("nonexistent.png")
        
        assert response is None
        
        client.stop()
    
    @patch('socket.socket')
    def test_request_detection_raw(self, mock_socket_class):
        """Test request_detection_raw with image bytes."""
        mock_socket = Mock()
        mock_response = json.dumps({"detections": []}).encode('utf-8')
        mock_socket.recvfrom.return_value = (mock_response, ("127.0.0.1", 12345))
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        
        image_bytes = b"fake_image_data"
        response = client.request_detection_raw(image_bytes)
        
        assert response is not None
        
        # Verify image data was included
        call_args = mock_socket.sendto.call_args
        sent_data = json.loads(call_args[0][0].decode('utf-8'))
        assert sent_data["command"] == "requestDetection"
        assert "image_data" in sent_data
        
        client.stop()


class TestContextManager:
    """Test context manager functionality."""
    
    @patch('socket.socket')
    def test_context_manager_start_stop(self, mock_socket_class):
        """Test that context manager starts and stops client."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        with ZelesisClient() as client:
            assert client.is_running is True
        
        # After exiting context, should be stopped
        assert client.is_running is False


class TestIsRunningProperty:
    """Test is_running property."""
    
    def test_is_running_false_when_not_started(self):
        """Test is_running is False when client is not started."""
        client = ZelesisClient()
        assert client.is_running is False
    
    @patch('socket.socket')
    def test_is_running_true_when_started(self, mock_socket_class):
        """Test is_running is True when client is started."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        client = ZelesisClient()
        client.start()
        assert client.is_running is True
        
        client.stop()
        assert client.is_running is False



# ============================================================================
# NON-PYTEST INTEGRATION TESTS
# These tests require a running Zelesis Neo instance and test real functionality
# Run these directly: python test_events.py
# ============================================================================

def test_real_event_listening():
    """
    Test real event listening with actual Zelesis instance.
    Listens for events for 10 seconds and prints what it receives.
    """
    print("\n" + "="*60)
    print("TEST: Real Event Listening")
    print("="*60)
    print("Starting client and listening for events for 10 seconds...")
    print("Make sure Zelesis Neo is running!\n")
    
    received_events = []
    
    def on_detection(event):
        print(f"[DETECTION EVENT] {event}")
        received_events.append(event)
    
    def on_triggerbot(event):
        print(f"[TRIGGERBOT EVENT] {event}")
        received_events.append(event)
    
    def on_any_event(event):
        event_type = event.get("event", "unknown")
        print(f"[GENERAL LISTENER] Event type: {event_type}")
    
    client = ZelesisClient()
    client.subscribe("detection", on_detection)
    client.subscribe("triggerbot", on_triggerbot)
    client.add_event_listener(on_any_event)
    
    try:
        client.start()
        print("Client started. Listening for events...\n")
        
        # Listen for 10 seconds
        import time
        time.sleep(10)
        
        print(f"\nReceived {len(received_events)} events total")
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        client.stop()
        print("Client stopped.")


def test_real_mouse_movement():
    """
    Test real mouse movement commands.
    Moves mouse in a square pattern.
    """
    print("\n" + "="*60)
    print("TEST: Real Mouse Movement")
    print("="*60)
    print("Moving mouse in a square pattern...")
    print("Make sure Zelesis Neo is running!\n")
    
    client = ZelesisClient()
    
    try:
        client.start()
        print("Client started.")
        
        import time
        
        # Move in a square: right, down, left, up
        movements = [
            (100, 0, "Right"),
            (0, 100, "Down"),
            (-100, 0, "Left"),
            (0, -100, "Up"),
        ]
        
        for x, y, direction in movements:
            print(f"Moving mouse {direction} ({x}, {y})...")
            client.move_mouse(x, y)
            time.sleep(0.5)
        
        print("\nMouse movement test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        client.stop()
        print("Client stopped.")


def test_real_mouse_clicks():
    """
    Test real mouse click commands.
    Performs 3 clicks with delays.
    """
    print("\n" + "="*60)
    print("TEST: Real Mouse Clicks")
    print("="*60)
    print("Performing mouse clicks...")
    print("Make sure Zelesis Neo is running!\n")
    
    client = ZelesisClient()
    
    try:
        client.start()
        print("Client started.")
        
        import time
        
        for i in range(3):
            print(f"Click {i+1}/3...")
            client.click_mouse()
            time.sleep(1)
        
        print("\nMouse click test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        client.stop()
        print("Client stopped.")


def test_real_detection_request():
    """
    Test real detection request without image (screen capture).
    """
    print("\n" + "="*60)
    print("TEST: Real Detection Request (Screen)")
    print("="*60)
    print("Requesting detection on current screen...")
    print("Make sure Zelesis Neo is running!\n")
    
    client = ZelesisClient()
    
    try:
        client.start()
        print("Client started.")
        
        print("Sending detection request...")
        response = client.request_detection()
        
        if response:
            print("\nDetection response received:")
            print(f"Response keys: {list(response.keys())}")
            if "detections" in response:
                print(f"Number of detections: {len(response['detections'])}")
                for i, detection in enumerate(response['detections'][:3]):  # Show first 3
                    print(f"  Detection {i+1}: {detection}")
            else:
                print(f"Full response: {response}")
        else:
            print("No response received (timeout or error)")
        
        print("\nDetection request test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.stop()
        print("Client stopped.")


def test_real_detection_with_image(image_path=None):
    """
    Test real detection request with an image file.
    
    Args:
        image_path: Path to image file (optional, will prompt if not provided)
    """
    print("\n" + "="*60)
    print("TEST: Real Detection Request (Image File)")
    print("="*60)
    
    if not image_path:
        print("No image path provided. Skipping image detection test.")
        print("Usage: test_real_detection_with_image('path/to/image.png')")
        return
    
    print(f"Requesting detection on image: {image_path}")
    print("Make sure Zelesis Neo is running!\n")
    
    from pathlib import Path
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        return
    
    client = ZelesisClient()
    
    try:
        client.start()
        print("Client started.")
        
        print("Sending detection request with image...")
        response = client.request_detection(image_path)
        
        if response:
            print("\nDetection response received:")
            print(f"Response keys: {list(response.keys())}")
            if "detections" in response:
                print(f"Number of detections: {len(response['detections'])}")
                for i, detection in enumerate(response['detections'][:5]):  # Show first 5
                    print(f"  Detection {i+1}: {detection}")
            else:
                print(f"Full response: {response}")
        else:
            print("No response received (timeout or error)")
        
        print("\nImage detection test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.stop()
        print("Client stopped.")


def test_context_manager_real():
    """
    Test context manager with real client operations.
    """
    print("\n" + "="*60)
    print("TEST: Context Manager (Real)")
    print("="*60)
    print("Testing context manager with real operations...")
    print("Make sure Zelesis Neo is running!\n")
    
    try:
        with ZelesisClient() as client:
            print(f"Client is running: {client.is_running}")
            
            # Test a simple command
            print("Sending mouse move command...")
            client.move_mouse(10, 10)
            
            import time
            time.sleep(0.5)
            
            print("Context manager test completed!")
        
        print(f"After context exit, client is running: {client.is_running}")
        print("Context manager test passed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_subscriptions_real():
    """
    Test multiple event subscriptions with real events.
    Listens for different event types simultaneously.
    """
    print("\n" + "="*60)
    print("TEST: Multiple Subscriptions (Real)")
    print("="*60)
    print("Testing multiple event subscriptions...")
    print("Make sure Zelesis Neo is running!\n")
    
    detection_count = [0]
    triggerbot_count = [0]
    all_events_count = [0]
    
    def on_detection(event):
        detection_count[0] += 1
        print(f"[DETECTION #{detection_count[0]}] Received detection event")
    
    def on_triggerbot(event):
        triggerbot_count[0] += 1
        print(f"[TRIGGERBOT #{triggerbot_count[0]}] Received triggerbot event")
    
    def on_all(event):
        all_events_count[0] += 1
        event_type = event.get("event", "unknown")
        print(f"[ALL EVENTS #{all_events_count[0]}] Event: {event_type}")
    
    client = ZelesisClient()
    client.subscribe("detection", on_detection)
    client.subscribe("triggerbot", on_triggerbot)
    client.add_event_listener(on_all)
    
    try:
        client.start()
        print("Client started. Listening for 15 seconds...\n")
        
        import time
        time.sleep(15)
        
        print(f"\nResults:")
        print(f"  Detection events: {detection_count[0]}")
        print(f"  Triggerbot events: {triggerbot_count[0]}")
        print(f"  Total events (all listeners): {all_events_count[0]}")
        print("Multiple subscriptions test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.stop()
        print("Client stopped.")


def test_unsubscribe_during_runtime():
    """
    Test unsubscribing from events while client is running.
    """
    print("\n" + "="*60)
    print("TEST: Unsubscribe During Runtime")
    print("="*60)
    print("Testing unsubscribe while client is running...")
    print("Make sure Zelesis Neo is running!\n")
    
    detection_count = [0]
    
    def on_detection(event):
        detection_count[0] += 1
        print(f"[DETECTION #{detection_count[0]}] Received event")
    
    client = ZelesisClient()
    client.subscribe("detection", on_detection)
    
    try:
        client.start()
        print("Client started. Listening for 5 seconds...")
        
        import time
        time.sleep(5)
        
        print(f"\nReceived {detection_count[0]} events before unsubscribe")
        print("Unsubscribing from detection events...")
        client.unsubscribe("detection")
        
        print("Listening for 5 more seconds (should receive no more detection events)...")
        detection_count[0] = 0  # Reset counter
        time.sleep(5)
        
        print(f"\nReceived {detection_count[0]} events after unsubscribe")
        print("Unsubscribe test completed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.stop()
        print("Client stopped.")


def run_all_integration_tests():
    """
    Run all integration tests in sequence.
    """
    print("\n" + "="*60)
    print("RUNNING ALL INTEGRATION TESTS")
    print("="*60)
    print("Make sure Zelesis Neo is running before starting!\n")
    
    import time
    
    tests = [
        ("Context Manager", test_context_manager_real),
        ("Mouse Movement", test_real_mouse_movement),
        ("Mouse Clicks", test_real_mouse_clicks),
        ("Detection Request (Screen)", test_real_detection_request),
        ("Multiple Subscriptions", test_multiple_subscriptions_real),
        ("Unsubscribe During Runtime", test_unsubscribe_during_runtime),
        ("Event Listening", test_real_event_listening),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        try:
            test_func()
            print(f"✓ {test_name} completed")
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\nWaiting 2 seconds before next test...")
        time.sleep(2)
    
    print("\n" + "="*60)
    print("ALL INTEGRATION TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    """
    Run integration tests directly.
    
    Usage:
        python test_events.py                          # Run all integration tests
        python test_events.py --test listening         # Run specific test
        python test_events.py --test mouse             # Run mouse tests
        python test_events.py --test detection         # Run detection tests
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        if test_name == "listening":
            test_real_event_listening()
        elif test_name == "mouse":
            test_real_mouse_movement()
            test_real_mouse_clicks()
        elif test_name == "detection":
            test_real_detection_request()
        elif test_name == "context":
            test_context_manager_real()
        elif test_name == "subscriptions":
            test_multiple_subscriptions_real()
        elif test_name == "unsubscribe":
            test_unsubscribe_during_runtime()
        else:
            print("Available tests:")
            print("  --test listening      Test event listening")
            print("  --test mouse          Test mouse commands")
            print("  --test detection      Test detection requests")
            print("  --test context        Test context manager")
            print("  --test subscriptions  Test multiple subscriptions")
            print("  --test unsubscribe    Test unsubscribe during runtime")
    else:
        # Run all integration tests
        run_all_integration_tests()
    
    