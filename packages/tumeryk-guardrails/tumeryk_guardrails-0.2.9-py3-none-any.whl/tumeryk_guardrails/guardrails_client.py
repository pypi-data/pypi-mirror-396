# Copyright Tumeryk 2024

import os
import requests
import asyncio
import aiohttp
from requests.exceptions import RequestException

class TumerykGuardrailsClient:
    """API Client for Tumeryk Guardrails"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url
        self.token = None
        self.config_id = None
        self.guard_url = None
        self.session = requests.Session()
        self.manual_model_score = None

    def _auto_login(self):
        """Automatically login if environment variables are available."""
        username = os.getenv("TUMERYK_USERNAME")
        password = os.getenv("TUMERYK_PASSWORD")
        base_url = os.getenv("TUMERYK_BASE_URL")
        
        if not self.base_url:
            if base_url:
                self.set_base_url(base_url)
            else:
                self.set_base_url("https://chat.tmryk.com")
        if username and password:
            try:
                self.login(username, password)
            except RequestException as err:
                print(f"Auto-login failed: {err}")

    def _auto_set_policy(self):
        """Automatically set policy if environment variable is available."""
        policy = os.getenv("TUMERYK_POLICY")
        if policy:
            self.set_policy(policy)

    def _get_headers(self):
        """Helper method to get the headers including authorization."""
        if not self.token:
            self._auto_login()
        return {"Authorization": f"Bearer {self.token}"}

    def login(self, username: str, password: str):
        """Authenticate and store access token."""
        username = username or os.getenv("TUMERYK_USERNAME")
        password = password or os.getenv("TUMERYK_PASSWORD")

        if not self.base_url:
            self.set_base_url(os.getenv("TUMERYK_BASE_URL", "https://chat.tmryk.com"))  

        if not username or not password:
            raise ValueError("Username and password must be provided either as arguments or environment variables.")

        payload = {"grant_type": "password", "username": username, "password": password}
        response = self.session.post(f"{self.base_url}/auth/token", data=payload)
        response.raise_for_status()
        response_data = response.json()

        if "access_token" in response_data:
            self.token = response_data["access_token"]
        else:
            print("Login failed, no access token in response")
        return response_data

    def get_policies(self) -> str:
        """Fetch available policies and return a list."""
        headers = self._get_headers()
        response = self.session.get(f"{self.base_url}/v1/rails/configs", headers=headers)
        response.raise_for_status()
        return [config['id'] for config in response.json()]

    def set_policy(self, config_id: str) -> str:
        """Set the configuration/policy to be used by the user."""
        self.config_id = config_id
        return {"config": f"Policy being used: {config_id}"}

    def set_model_score(self, score: int):
            """Set a default manual model score for all completion calls."""
            self.manual_model_score = score
    def tumeryk_completions(self, messages, stream: bool = False, policy_id: str = None, generation_options: dict = None, manual_model_score: int = None):
            """
            Send user input to the Guard service.
            A specific policy_id can be passed to override the client's default policy.
            """
            headers = self._get_headers()

            # 1. Determine the effective policy to use for this specific call
            effective_policy_id = policy_id
            if effective_policy_id is None:
                # If no override is provided, use the instance's default policy
                if not self.config_id:
                    # If the instance's policy isn't set, try loading from ENV
                    self._auto_set_policy()
                effective_policy_id = self.config_id

            # 2. Add a check to ensure a policy is actually set
            if not effective_policy_id:
                raise ValueError("No policy specified. Pass a 'policy_id' or set the TUMERYK_POLICY environment variable.")

            # 3. Use the effective_policy_id in the payload
            payload = {"config_id": effective_policy_id, "messages": messages, "stream": stream}

            if generation_options:
                payload["generation_options"] = generation_options

            effective_model_score = manual_model_score
            if effective_model_score is None:
                effective_model_score = self.manual_model_score
                
            if effective_model_score is not None:
                payload["manual_model_score"] = effective_model_score

            try:
                response = self.session.post(self.guard_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except RequestException as err:
                print(f"Request failed: {err}")
                return {"error": f"Request failed: {err}"}
            except Exception as err:
                print(f"An unexpected error occurred: {err}")
                return {"error": f"An unexpected error occurred: {err}"}

    async def tumeryk_completions_async(self, messages, stream: bool = False, policy_id: str = None, generation_options: dict = None, manual_model_score: int = None):
        """
        Async version of tumeryk_completions.
        A specific policy_id can be passed to override the client's default policy.
        """
        headers = self._get_headers()

        # 1. Determine the effective policy to use for this specific call
        effective_policy_id = policy_id
        if effective_policy_id is None:
            # If no override is provided, use the instance's default policy
            if not self.config_id:
                # If the instance's policy isn't set, try loading from ENV
                self._auto_set_policy()
            effective_policy_id = self.config_id

        # 2. Add a check to ensure a policy is actually set
        if not effective_policy_id:
            raise ValueError("No policy specified. Pass a 'policy_id' or set the TUMERYK_POLICY environment variable.")

        # 3. Use the effective_policy_id in the payload
        payload = {"config_id": effective_policy_id, "messages": messages, "stream": stream}

        if generation_options:
            payload["generation_options"] = generation_options

        effective_model_score = manual_model_score
        if effective_model_score is None:
            effective_model_score = self.manual_model_score

        if effective_model_score is not None:
            payload["manual_model_score"] = effective_model_score

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.guard_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            print(f"Async request failed: {err}")
            return {"error": f"Async request failed: {err}"}
        except Exception as err:
            print(f"An unexpected async error occurred: {err}")
            return {"error": f"An unexpected async error occurred: {err}"}

    def get_base_url(self):
        """Get the current base URL."""
        return self.base_url

    def set_base_url(self, base_url: str):
        """Set a new base URL."""
        self.base_url = base_url
        self.guard_url = f"{self.base_url}/v1/chat/completions"

    def set_token(self, token: str):
        """Set a new token directly"""
        self.token = token
