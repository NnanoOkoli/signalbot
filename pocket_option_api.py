import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import websocket
import threading
import hashlib
import hmac

class PocketOptionAPI:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.pocketoption.com"
        self.ws_url = "wss://api.pocketoption.com/echo/websocket"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json'
        })
        
        self.access_token = None
        self.user_id = None
        self.account_balance = 0.0
        self.is_authenticated = False
        
        # WebSocket connection
        self.ws = None
        self.ws_connected = False
        self.ws_thread = None
        
    def authenticate(self, email: str = None, password: str = None) -> bool:
        """Authenticate with Pocket Option API"""
        try:
            email = email or self.config.POCKET_OPTION_EMAIL
            password = password or self.config.POCKET_OPTION_PASSWORD
            
            if not email or not password:
                self.logger.error("Email and password are required for authentication")
                return False
            
            # Login endpoint
            login_data = {
                "email": email,
                "password": password,
                "remember": True
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.access_token = data.get('data', {}).get('access_token')
                    self.user_id = data.get('data', {}).get('user_id')
                    
                    if self.access_token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.access_token}'
                        })
                        self.is_authenticated = True
                        self.logger.info("Successfully authenticated with Pocket Option")
                        
                        # Get account information
                        self._get_account_info()
                        return True
                    else:
                        self.logger.error("No access token received")
                        return False
                else:
                    self.logger.error(f"Authentication failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.logger.error(f"Authentication request failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _get_account_info(self):
        """Get account information and balance"""
        try:
            if not self.is_authenticated:
                return
            
            response = self.session.get(f"{self.base_url}/api/user/profile")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user_data = data.get('data', {})
                    self.account_balance = float(user_data.get('balance', 0))
                    self.logger.info(f"Account balance: ${self.account_balance}")
                    
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
    
    def get_market_data(self, asset: str, timeframe: str = "5m", count: int = 100) -> Optional[Dict]:
        """Get market data for a specific asset"""
        try:
            if not self.is_authenticated:
                self.logger.error("Not authenticated")
                return None
            
            # Convert timeframe to seconds
            timeframe_map = {
                "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
                "1h": 3600, "4h": 14400, "1d": 86400
            }
            
            seconds = timeframe_map.get(timeframe, 300)
            
            # Get candles endpoint
            params = {
                "asset": asset,
                "timeframe": seconds,
                "count": count
            }
            
            response = self.session.get(f"{self.base_url}/api/chart/candles", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return self._process_market_data(data.get('data', []))
                else:
                    self.logger.error(f"Failed to get market data: {data.get('message')}")
                    return None
            else:
                self.logger.error(f"Market data request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return None
    
    def _process_market_data(self, raw_data: List) -> Dict:
        """Process raw market data into OHLCV format"""
        try:
            processed_data = {
                'timestamp': [],
                'open': [],
                'high': [],
                'low': [],
                'close': [],
                'volume': []
            }
            
            for candle in raw_data:
                processed_data['timestamp'].append(candle.get('time', 0))
                processed_data['open'].append(float(candle.get('open', 0)))
                processed_data['high'].append(float(candle.get('high', 0)))
                processed_data['low'].append(float(candle.get('low', 0)))
                processed_data['close'].append(float(candle.get('close', 0)))
                processed_data['volume'].append(float(candle.get('volume', 0)))
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing market data: {str(e)}")
            return {}
    
    def get_available_assets(self) -> List[str]:
        """Get list of available trading assets"""
        try:
            if not self.is_authenticated:
                return []
            
            response = self.session.get(f"{self.base_url}/api/assets")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    assets = data.get('data', [])
                    return [asset.get('name') for asset in assets if asset.get('active')]
                else:
                    self.logger.error(f"Failed to get assets: {data.get('message')}")
                    return []
            else:
                self.logger.error(f"Assets request failed with status {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting assets: {str(e)}")
            return []
    
    def place_trade(self, asset: str, direction: str, amount: float, 
                   expiry_time: int = None) -> Optional[Dict]:
        """Place a binary option trade"""
        try:
            if not self.is_authenticated:
                self.logger.error("Not authenticated")
                return None
            
            expiry_time = expiry_time or self.config.EXPIRY_TIME
            
            trade_data = {
                "asset": asset,
                "direction": direction,  # "call" or "put"
                "amount": amount,
                "expiry_time": expiry_time * 60,  # Convert to seconds
                "user_id": self.user_id
            }
            
            response = self.session.post(f"{self.base_url}/api/trade/place", json=trade_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trade_info = data.get('data', {})
                    self.logger.info(f"Trade placed successfully: {trade_info.get('id')}")
                    return trade_info
                else:
                    self.logger.error(f"Trade placement failed: {data.get('message')}")
                    return None
            else:
                self.logger.error(f"Trade request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error placing trade: {str(e)}")
            return None
    
    def get_trade_status(self, trade_id: str) -> Optional[Dict]:
        """Get status of a specific trade"""
        try:
            if not self.is_authenticated:
                return None
            
            response = self.session.get(f"{self.base_url}/api/trade/status/{trade_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', {})
                else:
                    self.logger.error(f"Failed to get trade status: {data.get('message')}")
                    return None
            else:
                self.logger.error(f"Trade status request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting trade status: {str(e)}")
            return None
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get trade history"""
        try:
            if not self.is_authenticated:
                return []
            
            params = {"limit": limit}
            response = self.session.get(f"{self.base_url}/api/trade/history", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', [])
                else:
                    self.logger.error(f"Failed to get trade history: {data.get('message')}")
                    return []
            else:
                self.logger.error(f"Trade history request failed with status {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting trade history: {str(e)}")
            return []
    
    def connect_websocket(self):
        """Connect to WebSocket for real-time data"""
        try:
            if not self.is_authenticated:
                self.logger.error("Cannot connect WebSocket without authentication")
                return
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header={'Authorization': f'Bearer {self.access_token}'},
                on_open=self._on_ws_open,
                on_message=self._on_ws_message,
                on_error=self._on_ws_error,
                on_close=self._on_ws_close
            )
            
            self.ws_thread = threading.Thread(target=self._ws_run)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error connecting WebSocket: {str(e)}")
    
    def _ws_run(self):
        """WebSocket run loop"""
        self.ws.run_forever()
    
    def _on_ws_open(self, ws):
        """WebSocket connection opened"""
        self.ws_connected = True
        self.logger.info("WebSocket connected")
        
        # Subscribe to market data
        self._subscribe_to_market_data()
    
    def _on_ws_message(self, ws, message):
        """WebSocket message received"""
        try:
            data = json.loads(message)
            self._handle_ws_message(data)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {str(e)}")
    
    def _on_ws_error(self, ws, error):
        """WebSocket error occurred"""
        self.logger.error(f"WebSocket error: {str(error)}")
        self.ws_connected = False
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        self.logger.info("WebSocket disconnected")
        self.ws_connected = False
    
    def _subscribe_to_market_data(self):
        """Subscribe to real-time market data"""
        if not self.ws_connected:
            return
        
        # Subscribe to major currency pairs
        assets = self.config.TRADING_ASSETS[:5]  # Limit to 5 assets for performance
        
        for asset in assets:
            subscribe_msg = {
                "action": "subscribe",
                "channel": "candles",
                "asset": asset,
                "timeframe": 300  # 5 minutes
            }
            
            try:
                self.ws.send(json.dumps(subscribe_msg))
                self.logger.info(f"Subscribed to {asset} market data")
            except Exception as e:
                self.logger.error(f"Error subscribing to {asset}: {str(e)}")
    
    def _handle_ws_message(self, data: Dict):
        """Handle incoming WebSocket messages"""
        try:
            if data.get('channel') == 'candles':
                asset = data.get('asset')
                candle_data = data.get('data', {})
                
                # Process real-time candle data
                self._process_realtime_candle(asset, candle_data)
                
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {str(e)}")
    
    def _process_realtime_candle(self, asset: str, candle_data: Dict):
        """Process real-time candle data"""
        # This method can be overridden by the main bot to handle real-time updates
        pass
    
    def disconnect_websocket(self):
        """Disconnect WebSocket connection"""
        if self.ws:
            self.ws.close()
            self.ws_connected = False
            self.logger.info("WebSocket disconnected")
    
    def logout(self):
        """Logout and clear authentication"""
        try:
            if self.is_authenticated:
                response = self.session.post(f"{self.base_url}/api/auth/logout")
                if response.status_code == 200:
                    self.logger.info("Successfully logged out")
                else:
                    self.logger.warning("Logout request failed")
        except Exception as e:
            self.logger.error(f"Error during logout: {str(e)}")
        finally:
            self.access_token = None
            self.user_id = None
            self.account_balance = 0.0
            self.is_authenticated = False
            self.disconnect_websocket()
    
    def get_account_balance(self) -> float:
        """Get current account balance"""
        if self.is_authenticated:
            self._get_account_info()
        return self.account_balance
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        try:
            current_hour = datetime.utcnow().hour
            return self.config.MARKET_OPEN_HOUR <= current_hour <= self.config.MARKET_CLOSE_HOUR
        except Exception as e:
            self.logger.error(f"Error checking market status: {str(e)}")
            return False
