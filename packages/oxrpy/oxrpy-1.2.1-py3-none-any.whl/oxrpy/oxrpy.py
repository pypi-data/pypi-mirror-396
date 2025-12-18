import requests
import logging
import time
from typing import Optional

class OxfordAPIError(Exception):
    """Base exception for Oxford API errors."""
    pass

class OxfordAPI:
    def __init__(self, server_id: str, server_key: str, timeout: int = 10, rate_limit: float = 0.2):
        if not server_id or not server_key:
            raise ValueError("server_id and server_key are required")
        self.base_url = "https://api.oxfd.re/v1"
        self.headers = {
            "server-id": server_id,
            "server-key": server_key
        }
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.logger = logging.getLogger(__name__)

    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Internal method to make API requests with error handling and rate limiting."""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            self.logger.info(f"Successfully called {method} {endpoint}")
            return response.json()
        except requests.Timeout:
            self.logger.error(f"Request to {endpoint} timed out")
            raise OxfordAPIError(f"Request to {endpoint} timed out")
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error for {endpoint}: {e}")
            raise OxfordAPIError(f"HTTP error: {e}")
        except requests.RequestException as e:
            self.logger.error(f"Request error for {endpoint}: {e}")
            raise OxfordAPIError(f"Request error: {e}")

    @property
    def servers(self):
        """Access server-related endpoints."""
        return Servers(self)

    @property
    def logs(self):
        """Access log-related endpoints."""
        return Logs(self)

    @property
    def commands(self):
        """Access command execution endpoints."""
        return Commands(self)

    def get_server(self):
        """Returns general information about the private server."""
        return self._make_request("GET", "/server")

    def get_players(self):
        """Returns a list of players currently in the server."""
        return self._make_request("GET", "/server/players")

    def get_queue(self):
        """Returns the current reserved server queue."""
        return self._make_request("GET", "/server/queue")

    def get_bans(self):
        """Returns active bans for the server."""
        return self._make_request("GET", "/server/bans")

    def get_killlogs(self):
        """Returns recent kill logs (maximum 100 entries)."""
        return self._make_request("GET", "/server/killlogs")

    def get_commandlogs(self):
        """Returns recent command execution logs."""
        return self._make_request("GET", "/server/commandlogs")

    def get_modcalls(self):
        """Returns recent moderator call requests."""
        return self._make_request("GET", "/server/modcalls")

    def get_vehicles(self):
        """Returns vehicles currently spawned in the server."""
        return self._make_request("GET", "/server/vehicles")

    def get_robberies(self):
        """
        Returns the current status of all robbery locations.
        Each entry contains:
            - Name (str): The name of the robbery location.
            - Alarm (bool): Whether the alarm is active.
            - Available (bool): Whether the location is available for robbery.
        """
        return self._make_request("GET", "/server/robberies")

    def get_radiocalls(self):
        """
        Returns recent radio calls.
        Each entry contains:
            - Timestamp (int): Unix timestamp of the call.
            - UserId (int): The user ID of the caller.
            - Username (str): The username of the caller.
            - Location (str): The location of the call.
            - Description (str): The description of the call.
            - Channel (str): The radio channel.
            - Callsign (str): The callsign of the caller.
        """
        return self._make_request("GET", "/server/radiocalls")

    def execute_command(self, command: str):
        """Executes a permitted command on the server."""
        if not command:
            raise ValueError("Command cannot be empty")
        data = {"command": command}
        return self._make_request("POST", "/server/command", data)

class Servers:
    """Manager for server-related endpoints."""
    
    def __init__(self, api: 'OxfordAPI'):
        self.api = api

    def get_server(self):
        """Returns general information about the private server."""
        return self.api.get_server()

    def get_players(self):
        """Returns a list of players currently in the server."""
        return self.api.get_players()

    def get_queue(self):
        """Returns the current reserved server queue."""
        return self.api.get_queue()

    def get_bans(self):
        """Returns active bans for the server."""
        return self.api.get_bans()

    def get_vehicles(self):
        """Returns vehicles currently spawned in the server."""
        return self.api.get_vehicles()

class Logs:
    """Manager for log-related endpoints."""
    
    def __init__(self, api: 'OxfordAPI'):
        self.api = api

    def get_killlogs(self):
        """Returns recent kill logs (maximum 100 entries)."""
        return self.api.get_killlogs()

    def get_commandlogs(self):
        """Returns recent command execution logs."""
        return self.api.get_commandlogs()

    def get_modcalls(self):
        """Returns recent moderator call requests."""
        return self.api.get_modcalls()

    def get_robberies(self):
        """
        Returns the current status of all robbery locations.
        Each entry contains:
            - Name (str): The name of the robbery location.
            - Alarm (bool): Whether the alarm is active.
            - Available (bool): Whether the location is available for robbery.
        """
        return self.api.get_robberies()

    def get_radiocalls(self):
        """
        Returns recent radio calls.
        Each entry contains:
            - Timestamp (int): Unix timestamp of the call.
            - UserId (int): The user ID of the caller.
            - Username (str): The username of the caller.
            - Location (str): The location of the call.
            - Description (str): The description of the call.
            - Channel (str): The radio channel.
            - Callsign (str): The callsign of the caller.
        """
        return self.api.get_radiocalls()

class Commands:
    """Manager for command execution endpoints."""
    
    def __init__(self, api: 'OxfordAPI'):
        self.api = api

    def execute_command(self, command: str):
        """Executes a permitted command on the server."""
        return self.api.execute_command(command)