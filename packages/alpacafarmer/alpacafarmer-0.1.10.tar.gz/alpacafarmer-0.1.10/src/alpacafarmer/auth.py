"""Authentication handling for Alpaca API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class Environment(str, Enum):
    """Alpaca API environment."""

    PAPER = "paper"
    LIVE = "live"


# Base URLs for different environments and APIs
BASE_URLS = {
    Environment.PAPER: {
        "trading": "https://paper-api.alpaca.markets",
        "data": "https://data.alpaca.markets",
        "broker": "https://broker-api.sandbox.alpaca.markets",
    },
    Environment.LIVE: {
        "trading": "https://api.alpaca.markets",
        "data": "https://data.alpaca.markets",
        "broker": "https://broker-api.alpaca.markets",
    },
}


@dataclass
class AlpacaAuth:
    """Handles API key authentication and header generation.
    
    Supports both API key/secret authentication and OAuth token authentication.
    Falls back to environment variables if credentials are not provided directly.
    
    Environment variables:
        - ALPACA_API_KEY: API key for authentication
        - ALPACA_SECRET_KEY: Secret key for authentication
        - ALPACA_OAUTH_TOKEN: OAuth token (alternative to API key/secret)
    
    Examples:
        >>> # Direct credentials
        >>> auth = AlpacaAuth(api_key="your-key", secret_key="your-secret")
        >>> 
        >>> # From environment variables
        >>> auth = AlpacaAuth()
        >>> 
        >>> # OAuth token
        >>> auth = AlpacaAuth(oauth_token="your-oauth-token")
    """

    api_key: str | None = None
    secret_key: str | None = None
    oauth_token: str | None = None
    environment: Environment = Environment.PAPER

    def __post_init__(self) -> None:
        """Initialize auth from environment variables if not provided."""
        if self.oauth_token is None:
            self.api_key = self.api_key or os.environ.get("ALPACA_API_KEY")
            self.secret_key = self.secret_key or os.environ.get("ALPACA_SECRET_KEY")
        else:
            self.oauth_token = self.oauth_token or os.environ.get("ALPACA_OAUTH_TOKEN")

    def get_headers(self) -> dict[str, str]:
        """Generate authentication headers for API requests.
        
        Returns:
            Dictionary of HTTP headers for authentication.
            
        Raises:
            ValueError: If no valid authentication credentials are available.
        """
        if self.oauth_token:
            return {
                "Authorization": f"Bearer {self.oauth_token}",
            }
        
        if self.api_key and self.secret_key:
            return {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key,
            }
        
        raise ValueError(
            "No valid authentication credentials. Provide api_key/secret_key "
            "or oauth_token, or set ALPACA_API_KEY/ALPACA_SECRET_KEY environment variables."
        )

    def get_base_url(self, api_type: str = "trading") -> str:
        """Get the base URL for the specified API type and environment.
        
        Args:
            api_type: Type of API - "trading", "data", or "broker"
            
        Returns:
            The base URL for the API.
            
        Note:
            For broker API:
            - PAPER environment uses sandbox: https://broker-api.sandbox.alpaca.markets
            - LIVE environment uses production: https://broker-api.alpaca.markets
        """
        return BASE_URLS[self.environment][api_type]

    @property
    def is_paper(self) -> bool:
        """Check if using paper trading environment."""
        return self.environment == Environment.PAPER

    @property
    def is_live(self) -> bool:
        """Check if using live trading environment."""
        return self.environment == Environment.LIVE