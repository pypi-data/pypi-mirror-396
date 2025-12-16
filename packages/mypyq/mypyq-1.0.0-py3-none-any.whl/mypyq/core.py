import requests
from time import time
from time import sleep

class MyQAPI:
    """MyQ API client for controlling garage doors."""
    
    def __init__(self, account_id=None, refresh_token=None, handle=None):
        """
        Initialize the MyQ API client.
        
        Args:
            account_id: MyQ account ID
            refresh_token: MyQ refresh token
            handle: Optional existing handle dict to restore session state
        """
        if (not account_id or not refresh_token) and (not handle):
            raise ValueError("Both account_id and refresh_token are required.")
        
        if handle:
            self._state = handle
        else:
            self._state = {
                'accountId': account_id,
                'refreshToken': refresh_token
            }
        
        self._update_token()
    
    def _update_token(self):
        """Update the access token if expired."""
        if self._state.get('expirationTime') and self._state['expirationTime'] > time():
            return  # still valid
        
        try:
            body = {
                "client_id": "IOS_CGI_MYQ",
                "grant_type": "refresh_token",
                "refresh_token": self._state['refreshToken'],
            }
            
            response = requests.post(
                "https://partner-identity.myq-cloud.com/connect/token",
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()
            
            self._state['authorizationToken'] = data.get("access_token")
            self._state['refreshToken'] = data.get("refresh_token")
            self._state['tokenType'] = data.get("token_type")
            expires_in = data.get("expires_in")
            self._state['expirationTime'] = time() + expires_in - 10 if expires_in else None
            
        except Exception as e:
            raise ConnectionError("Failed to connect to the myQ API: " + str(e)) from e
    
    def devices(self, raw=False):
        """
        Get all garage door devices.
        
        Args:
            raw: If True, return raw device data. If False, return GarageDoor objects.
        
        Returns:
            List of GarageDoor objects or raw device dicts
        """
        self._update_token()
        
        try:
            headers = {
                "Authorization": f"{self._state['tokenType']} {self._state['authorizationToken']}"
            }
            response = requests.get(
                f"https://devices.myq-cloud.com/api/v6.0/Accounts/{self._state['accountId']}/Devices",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            devices = [
                device for device in data.get("items", [])
                if device.get("device_family") == "garagedoor"
            ]
            
            if raw:
                return devices
            
            return [GarageDoor(self, device.get('serial_number'), name=device.get('name', None)) for device in devices]
            
        except Exception as e:
            raise ConnectionError("Failed to get garage devices: " + str(e)) from e
    
    def open(self, device_id):
        """Open a garage door."""
        
        self._update_token()
        try:
            headers = {"Authorization": f"{self._state['tokenType']} {self._state['authorizationToken']}"}
            
            response = requests.put(
                f"https://account-devices-gdo.myq-cloud.com/api/v6.0/Accounts/{self._state['accountId']}/door_openers/{device_id}/open",
                headers=headers
            )

            response.raise_for_status()
            return self.status(device_id)
        
        except Exception as e:
            raise ConnectionError("Failed to open garage door: " + str(e)) from e
    
    def close(self, device_id):
        """Close a garage door."""
        self._update_token()
        try:
            headers = {"Authorization": f"{self._state['tokenType']} {self._state['authorizationToken']}"}
            
            response = requests.put(
                f"https://account-devices-gdo.myq-cloud.com/api/v6.0/Accounts/{self._state['accountId']}/door_openers/{device_id}/close",
                headers=headers
            )

            response.raise_for_status()
            return self.status(device_id)
        
        except Exception as e:
            raise ConnectionError("Failed to close garage door: " + str(e)) from e
    
    def status(self, device_id):
        """Get status of a garage door."""
        self._update_token()
        try:
            headers = {"Authorization": f"{self._state['tokenType']} {self._state['authorizationToken']}"}
            
            response = requests.get(
                f"https://devices.myq-cloud.com/api/v6.0/Accounts/{self._state['accountId']}/Devices/{device_id}",
                headers=headers
            )

            response.raise_for_status()
            return response.json().get("state", {})
        
        except Exception as e:
            raise ConnectionError("Failed to get garage door status: " + str(e)) from e
    
    def get_handle(self):
        """Get the current session state for persistence."""
        return self._state.copy()

class GarageDoor(MyQAPI):
    """Represents a MyQ garage door device."""
    
    def __init__(self, parent_api, device_id, name=None):
        """
        Initialize a GarageDoor instance.
        
        Args:
            parent_api: Parent MyQAPI instance
            device_id: Device ID (serial number)
        """
        # Copy parent state instead of calling super().__init__
        self._state = parent_api._state
        self.device_id = device_id
        self.prev_status = self.status()
        self.name = name
    
    def open(self):
        """Open this garage door."""
        return super().open(self.device_id)
    
    def close(self):
        """Close this garage door."""
        return super().close(self.device_id)
    
    def status(self, device_id=None):
        """Get the status of this garage door.

        Accepts an optional `device_id` because `MyQAPI` calls
        `self.status(device_id)` after open/close operations. If a
        `device_id` is provided use it, otherwise use this instance's
        `device_id`.
        """
        return super().status(device_id or self.device_id)
    
    def subscribe(self, callback):
        """Subscribe to status updates."""
        while True:
            status = self.status()

            if status != self.prev_status:
                self.prev_status = status
                callback(status)
            sleep(10) # Replicate polling interval from myQ app
    
    def __repr__(self):
        return f"GarageDoor(device_id='{self.device_id}', name='{self.name}')"