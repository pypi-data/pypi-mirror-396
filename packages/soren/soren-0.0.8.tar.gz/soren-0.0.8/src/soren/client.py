"""
API client for communicating with the Soren backend service
"""
import os
import requests
from typing import Optional, Dict, Any


class SorenClient:
    """Client for interacting with the Soren backend API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Soren API client
        
        Args:
            api_key: API key for authentication (defaults to env var SOREN_API_KEY)
            base_url: Base URL for the Soren API (defaults to env var SOREN_API_URL or production URL)
        """
        self.api_key = api_key or os.getenv("SOREN_API_KEY")
        self.base_url = base_url or os.getenv("SOREN_API_URL", "https://api.soren-ai.com")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def login(self, api_key: str) -> Dict[str, Any]:
        """
        Authenticate with the Soren backend and validate API key.

        Validates if the API key is valid by checking if the user exists.
        If the user exists, return the API key and user info.
        If the user does not exist, return an error.
        
        Args:
            api_key: User API key
            
        Returns:
            Response containing API key (as access_token) and user info
        """
        response = self.session.post(
            f"{self.base_url}/auth/validate-api-key",
            json={"api_key": api_key}
        )
        print(f"response: {response.json()}")
        response.raise_for_status()
        return response.json()
    
    def create_run(self, yaml_config: dict, **kwargs) -> Dict[str, Any]:
        """
        Create a new evaluation run
        
        Args:
            yaml_config: Parsed YAML configuration dictionary from user's machine
            **kwargs: Additional run parameters
            
        Returns:
            Response containing run ID and details
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")
        
        yaml_config_dict = dict(yaml_config.items())

        print(f"yaml_config_dict: {yaml_config_dict}")
        # Create the run --> store in backend and create in frontend
        response = self.session.post(
            f"{self.base_url}/runs",
            json={
                "yaml_config": yaml_config_dict, 
                }
        )
        print(f"Response (in Client.py file): {response.json()}")
        response.raise_for_status()
        return response.json()

    def update_run(self, run_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of a run

        Args:
            run_id: Run ID
            status: New status
        """
        response = self.session.patch(
            f"{self.base_url}/runs/{run_id}",
            json={
                "status": status,
                }
            )
        response.raise_for_status()
        return response.json()

    def upload_output(self, run_id: str, output_content: str) -> Dict[str, Any]:
        """
        Upload the output content to the backend.

        Args:
            run_id: Run ID
            output_content: The output file content as a string

        Returns:
            Response from server
        """
        response = self.session.patch(
            f"{self.base_url}/runs/{run_id}/output",
            json={"output": output_content}
        )
        response.raise_for_status()
        return response.json()

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get details for a specific run
        
        Args:
            run_id: Run ID
            
        Returns:
            Run details
        """
        if not self.api_key:
            raise ValueError("API key required. Run 'soren login' first.")
        
        response = self.session.get(f"{self.base_url}/runs/{run_id}")
        response.raise_for_status()
        return response.json()
