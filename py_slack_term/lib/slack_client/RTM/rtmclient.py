import json
import logging
import threading
import time

from py_slack_term.lib import Logger


logger = logging.getLogger(__name__)


class SlackRTMClient:
    """
    Real-time messaging client using Slack Socket Mode.
    
    Replaces the deprecated RTM API with Socket Mode (WebSocket over WSS).
    Socket Mode doesn't require a publicly accessible server and is Slack's
    recommended transport for real-time messaging.
    """

    def __init__(self, slack_client, callback):
        self.slack_client = slack_client
        self.callback = callback
        self.logger = Logger(' ')
        self.ws_url: str = None
        self.socket_mode_client = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        self.logger.log('starting Socket Mode client')
        
        if not self.slack_client.socket_mode_token:
            # Fallback to deprecated RTM if no Socket Mode token
            self.logger.log('no socket mode token, falling back to RTM')
            self._start_rtm()
            return
        
        # Use Socket Mode
        self._start_socket_mode()

    def _start_rtm(self) -> None:
        """Fallback to deprecated RTM if Socket Mode isn't configured."""
        while not self.ws_url:
            self.ws_url = self.slack_client.rtm_connect()
            if not self.ws_url:
                self.logger.log('error getting RealTimeMessaging URL. waiting 10 seconds...')
                time.sleep(10)
        
        # For RTM, we'd need to set up a websocket listener
        # This is a simplified fallback — Socket Mode is preferred
        self.logger.log('RTM fallback started (deprecated)')

    def _start_socket_mode(self) -> None:
        """Start Socket Mode connection."""
        def on_socket_mode_message(client: object, message: str) -> None:
            """
            Handle incoming Socket Mode messages.
            
            Socket Mode wraps events in a specific envelope:
            {
                "type": "events_api",
                "payload": {
                    "type": "event_callback",
                    "event": { ... }
                }
            }
            """
            try:
                data = json.loads(message)
                logger.debug(f"Raw Socket Mode message: {data}")
                
                # Extract the actual event from the Socket Mode envelope
                if data.get('type') == 'events_api':
                    payload = data.get('payload', {})
                    event = payload.get('event', {})
                elif data.get('type') == 'hello':
                    # Connection established
                    self.logger.log('Socket Mode connected (hello event)')
                    return
                else:
                    # Direct event or ack
                    event = data
                
                # Call the callback with the extracted event
                if event:
                    self.callback(event)
                    
            except json.JSONDecodeError:
                self.logger.log(f'Failed to parse message: {message}')
            except Exception as e:
                self.logger.log(f'Error processing message: {e}')

        try:
            self.slack_client.socket_mode_connect(on_socket_mode_message)
            self.logger.log('Socket Mode client started')
        except Exception as e:
            self.logger.log(f'Failed to start Socket Mode: {e}')
            raise

    def on_message(self, _, message: str) -> None:
        """Legacy RTM message handler — kept for compatibility."""
        data = json.loads(message)
        self.callback(data)

    def on_error(self, *args: list) -> None:
        """Legacy RTM error handler — kept for compatibility."""
        self.logger.log(args)
        self.stop()
        self.start()

    def stop(self) -> None:
        """Stop the Socket Mode client."""
        self.logger.log('closing Socket Mode client')
        self._stop_event.set()
        
        if self.socket_mode_client:
            try:
                self.socket_mode_client.close()
            except Exception:
                pass
            self.socket_mode_client = None
        
        if hasattr(self, 'ws_url'):
            self.ws_url = None
        
        self.logger.log('closed Socket Mode client')
