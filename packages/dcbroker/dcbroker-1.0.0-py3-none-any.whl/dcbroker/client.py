import requests
from typing import Optional
import time

class DCBrokerClient:
    """Client library for DC-broker message broker system"""
    
    def __init__(self, base_url: str = "https://friendio.live"):
        self.base_url = base_url
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.session_key: Optional[str] = None
        self.session_created_at: float = 0
        self.session_timeout = 900  # 15 minutes
    
    def login(self, username: str, password: str) -> bool:
        try:
            resp = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password},
                timeout=5
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.username = username
                self.password = password
                self.session_key = data.get("session_key")
                self.session_created_at = time.time()
                print(f"✓ Logged in as {username}")
                return True
            elif resp.status_code == 404:
                print("✗ Account not found")
            elif resp.status_code == 403:
                print("✗ Invalid password")
            else:
                print(f"✗ Login failed: {resp.text}")
            return False
        except requests.exceptions.ConnectionError:
            print("✗ Connection error: Server is not running")
            return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    def _is_session_valid(self) -> bool:
        if not self.session_key:
            return False
        elapsed = time.time() - self.session_created_at
        return elapsed < self.session_timeout
    
    def _reauthenticate(self) -> bool:
        if not self.username or not self.password:
            print("✗ Cannot re-authenticate: credentials not stored")
            return False
        print("Session expired. Re-authenticating...")
        return self.login(self.username, self.password)
    
    def _ensure_authenticated(self) -> bool:
        if not self.session_key:
            print("✗ Not authenticated. Call login() first")
            return False
        if not self._is_session_valid():
            return self._reauthenticate()
        return True
    
    def create_endpoint(self, endpoint_name: str, message: str = "") -> bool:
        if not self._ensure_authenticated():
            return False
        
        try:
            resp = requests.post(
                f"{self.base_url}/add_account_endpoint",
                json={
                    "session_key": self.session_key,
                    "endpoint": endpoint_name,
                    "message": message
                },
                timeout=5
            )
            
            if resp.status_code == 201:
                print(f"✓ Endpoint '{endpoint_name}' created/updated")
                return True
            else:
                print(f"✗ Failed to create endpoint: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ Error creating endpoint: {e}")
            return False
    
    def update_endpoint(self, endpoint_name: str, message: str) -> bool:
        return self.create_endpoint(endpoint_name, message)
    
    def list_endpoints(self) -> Optional[list]:
        if not self._ensure_authenticated():
            return None
        
        try:
            resp = requests.get(
                f"{self.base_url}/account/{self.username}/endpoints",
                params={"session_key": self.session_key},
                timeout=5
            )
            
            if resp.status_code == 200:
                data = resp.json()
                endpoints = data.get("endpoints", [])
                print(f"✓ Found {len(endpoints)} endpoints")
                return endpoints
            else:
                print(f"✗ Failed to list endpoints: {resp.text}")
                return None
        except Exception as e:
            print(f"✗ Error listing endpoints: {e}")
            return None
    
    def get_endpoint_message(self, endpoint_name: str) -> Optional[str]:
        if not self._ensure_authenticated():
            return None
        
        try:
            resp = requests.get(
                f"{self.base_url}/account/{self.username}/endpoint/{endpoint_name}",
                params={"session_key": self.session_key},
                timeout=5
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return data.get("message")
            elif resp.status_code == 401:
                print("✗ Session expired or invalid")
                return None
            else:
                print(f"✗ Failed to get endpoint: {resp.text}")
                return None
        except Exception as e:
            print(f"✗ Error getting endpoint: {e}")
            return None
    
    def get_all_endpoints(self) -> Optional[list]:
        if not self._ensure_authenticated():
            return None
        
        try:
            resp = requests.get(
                f"{self.base_url}/account/{self.username}/all_endpoints",
                params={"session_key": self.session_key},
                timeout=5
            )
            
            if resp.status_code == 200:
                data = resp.json()
                endpoints = data.get("endpoints", [])
                print(f"✓ Retrieved {len(endpoints)} endpoints with messages")
                return endpoints
            elif resp.status_code == 401:
                print("✗ Session expired or invalid")
                return None
            else:
                print(f"✗ Failed to get all endpoints: {resp.text}")
                return None
        except Exception as e:
            print(f"✗ Error getting all endpoints: {e}")
            return None
    
    def logout(self):
        """Clear session and logout"""
        self.session_key = None
        self.session_created_at = 0
        print(f"✓ Logged out from {self.username}")
        self.username = None
        self.password = None


if __name__ == "__main__":
    client = DCBrokerClient(base_url="https://friendio.live")

    if client.login("testuser", "password123"):
        client.create_endpoint("status", "Server is running")
        
        endpoints = client.list_endpoints()
        if endpoints:
            print(f"Endpoints: {endpoints}")
        
        msg = client.get_endpoint_message("status")
        if msg:
            print(f"Message: {msg}")
        
        client.logout()