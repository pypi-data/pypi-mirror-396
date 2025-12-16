"""
AltSportsLeagues Python SDK

A comprehensive SDK for interacting with the AltSportsLeagues platform,
enabling league owners to get compliant and onboarded with sportsbooks,
and sportsbooks to discover new betting opportunities.

Example:
    >>> from altsportsleagues import AltSportsLeagues
    >>> client = AltSportsLeagues(api_key="your_api_key")
    >>> leagues = client.get_leagues()
    >>> events = client.get_events(league_id="nba")
"""

__version__ = "1.0.0"
__author__ = "AltSportsLeagues.ai"
__description__ = "Python SDK for AltSportsLeagues platform"

from .client import AltSportsLeagues
from .models import League, Event, Sport, Odds
from .exceptions import AltSportsLeaguesError, AuthenticationError, ValidationError

__all__ = [
    "AltSportsLeagues",
    "League",
    "Event",
    "Sport",
    "Odds",
    "AltSportsLeaguesError",
    "AuthenticationError",
    "ValidationError",
]
