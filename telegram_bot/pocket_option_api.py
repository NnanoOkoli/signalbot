"""
Pocket Option API Wrapper
Handles WebSocket connection, authentication, and trade execution
"""

import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from websocket import create_connection, WebSocketConnectionClosedException
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class PocketOptionAPI:
    """Pocket Option WebSocket API wrapper"""
    
    def __init__(self, email: str, password: str, demo: bool = True):
        self.email = email
        self.password = password
        self.demo = demo
        self.ws = None
        self.connected = False
        self.session_id = None
        self.balance = 0.0
        self.assets = []
        self.trades = []
        
        # Pocket Option endpoints
        self.base_url = "wss://api.pocketoption.com/socket.io/?EIO=3&transport=websocket"
        self.api_url = "https://api.pocketoption.com/api"
        
        # Callbacks
        self.on_balance_update: Optional[Callable] = None
        self.on_trade_result: Optional[Callable] = None
        self.on_connection_status: Optional[Callable] = None
        
        # Connection thread
        self.connection_thread = None
        self.running = False
        
    def connect(self) -> bool:
        """Establish WebSocket connection to Pocket Option"""
        try:
            logger.info("Connecting to Pocket Option WebSocket...")
            self.ws = create_connection(self.base_url)
            self.connected = True
            
            # Start connection thread
            self.running = True
            self.connection_thread = threading.Thread(target=self._connection_loop)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            
            # Authenticate
            if self._authenticate():
                logger.info("Successfully connected and authenticated to Pocket Option")
                return True
            else:
                logger.error("Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close WebSocket connection"""
        self.running = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.connected = False
        logger.info("Disconnected from Pocket Option")
    
    def _authenticate(self) -> bool:
        """Authenticate with Pocket Option"""
        try:
            # Send authentication message
            auth_data = {
                "action": "login",
                "email": self.email,
                "password": self.password,
                "demo": self.demo
            }
            
            auth_message = f"42{json.dumps(auth_data)}"
            self.ws.send(auth_message)
            
            # Wait for response
            response = self.ws.recv()
            logger.debug(f"Auth response: {response}")
            
            if "42" in response and "success" in response:
                # Parse session data
                data = json.loads(response[2:])
                if data.get("success"):
                    self.session_id = data.get("session_id")
                    self.balance = data.get("balance", 0.0)
                    logger.info(f"Authenticated successfully. Balance: ${self.balance}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def _connection_loop(self):
        """Main connection loop for handling messages"""
        while self.running and self.connected:
            try:
                if self.ws:
                    message = self.ws.recv()
                    self._handle_message(message)
            except WebSocketConnectionClosedException:
                logger.warning("WebSocket connection closed, attempting to reconnect...")
                self.connected = False
                if self.running:
                    time.sleep(5)
                    self.connect()
            except Exception as e:
                logger.error(f"Connection loop error: {e}")
                time.sleep(1)
    
    def _handle_message(self, message: str):
        """Handle incoming WebSocket messages"""
        try:
            if message.startswith("42"):
                data = json.loads(message[2:])
                self._process_data(data)
            elif message.startswith("2"):
                # Ping response
                self.ws.send("3")
        except Exception as e:
            logger.error(f"Message handling error: {e}")
    
    def _process_data(self, data: Dict[str, Any]):
        """Process different types of data messages"""
        action = data.get("action")
        
        if action == "balance_update":
            self.balance = data.get("balance", self.balance)
            if self.on_balance_update:
                self.on_balance_update(self.balance)
                
        elif action == "trade_result":
            trade_result = data.get("data", {})
            self.trades.append(trade_result)
            if self.on_trade_result:
                self.on_trade_result(trade_result)
                
        elif action == "assets":
            self.assets = data.get("data", [])
    
    def place_trade(self, asset: str, amount: float, direction: str, 
                    expiry: int, strategy: str = "manual") -> Dict[str, Any]:
        """
        Place a trade on Pocket Option
        
        Args:
            asset: Trading asset (e.g., "EURUSD")
            amount: Trade amount in USD
            direction: "call" or "put"
            expiry: Expiry time in seconds
            strategy: Strategy name for tracking
        
        Returns:
            Dict with trade details and status
        """
        try:
            if not self.connected:
                return {"success": False, "error": "Not connected"}
            
            if amount > self.balance:
                return {"success": False, "error": "Insufficient balance"}
            
            # Prepare trade data
            trade_data = {
                "action": "trade",
                "asset": asset,
                "amount": amount,
                "direction": direction,
                "expiry": expiry,
                "strategy": strategy,
                "timestamp": int(time.time() * 1000)
            }
            
            # Send trade request
            trade_message = f"42{json.dumps(trade_data)}"
            self.ws.send(trade_message)
            
            # Wait for confirmation
            response = self.ws.recv()
            logger.debug(f"Trade response: {response}")
            
            if "42" in response and "success" in response:
                data = json.loads(response[2:])
                if data.get("success"):
                    trade_info = {
                        "success": True,
                        "trade_id": data.get("trade_id"),
                        "asset": asset,
                        "amount": amount,
                        "direction": direction,
                        "expiry": expiry,
                        "entry_price": data.get("entry_price"),
                        "timestamp": trade_data["timestamp"],
                        "strategy": strategy
                    }
                    logger.info(f"Trade placed successfully: {trade_info}")
                    return trade_info
            
            return {"success": False, "error": "Trade placement failed"}
            
        except Exception as e:
            logger.error(f"Trade placement error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_balance(self) -> float:
        """Get current account balance"""
        return self.balance
    
    def get_assets(self) -> list:
        """Get available trading assets"""
        return self.assets
    
    def get_trades(self) -> list:
        """Get recent trades"""
        return self.trades
    
    def is_connected(self) -> bool:
        """Check if connected to Pocket Option"""
        return self.connected
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status"""
        return {
            "connected": self.connected,
            "running": self.running,
            "session_id": self.session_id,
            "balance": self.balance,
            "assets_count": len(self.assets),
            "trades_count": len(self.trades)
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the API
    api = PocketOptionAPI("test@example.com", "password123", demo=True)
    
    if api.connect():
        print("Connected successfully!")
        print(f"Balance: ${api.get_balance()}")
        print(f"Assets: {len(api.get_assets())}")
        
        # Test trade placement
        result = api.place_trade("EURUSD", 10.0, "call", 60, "test")
        print(f"Trade result: {result}")
        
        api.disconnect()
    else:
        print("Connection failed!")
