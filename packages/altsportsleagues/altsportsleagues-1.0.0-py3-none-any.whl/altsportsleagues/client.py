"""
Main client for interacting with AltSportsLeagues API
"""

import requests
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin
import json

from .models import League, Event, Sport, Odds, LeagueQuestionnaire
from .exceptions import AltSportsLeaguesError, AuthenticationError, ValidationError


class AltSportsLeagues:
    """
    Main client for the AltSportsLeagues API.

    Provides methods for:
    - Creating and managing sports leagues
    - Batch uploading events
    - Accessing historical sports data
    - Retrieving sports types and classifications
    - Getting betting odds and market data

    Args:
        api_key: Your AltSportsLeagues API key
        base_url: API base URL (default: https://api.altsportsleagues.ai)
        timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.altsportsleagues.ai",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'altsportsleagues-python/{__import__("altsportsleagues").__version__}'
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the API"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e)
        except requests.exceptions.RequestException as e:
            raise AltSportsLeaguesError(f"Request failed: {e}")

    def _handle_http_error(self, error: requests.exceptions.HTTPError) -> None:
        """Handle HTTP errors and raise appropriate exceptions"""
        response = error.response
        try:
            data = response.json()
            message = data.get('message', str(error))
        except:
            message = str(error)

        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 422:
            raise ValidationError(message)
        else:
            raise AltSportsLeaguesError(message)

    # League Management
    def create_league(self, league_data: Dict[str, Any]) -> League:
        """
        Create a new sports league.

        Args:
            league_data: League information including name, sport type, contact details

        Returns:
            League: Created league object

        Example:
            >>> league = client.create_league({
            ...     "league_name": "My Basketball League",
            ...     "sport_bucket": "team",
            ...     "contact_email": "admin@myleague.com"
            ... })
        """
        response = self._request('POST', '/v1/leagues', json=league_data)
        return League(**response['data'])

    def get_leagues(self, sport_type: Optional[str] = None) -> List[League]:
        """
        Get all available leagues, optionally filtered by sport type.

        Args:
            sport_type: Filter by sport type (e.g., 'basketball', 'football')

        Returns:
            List[League]: List of leagues

        Example:
            >>> nba_leagues = client.get_leagues(sport_type="basketball")
        """
        params = {}
        if sport_type:
            params['sport_type'] = sport_type

        response = self._request('GET', '/v1/leagues', params=params)
        return [League(**league) for league in response['data']]

    def get_league(self, league_id: str) -> League:
        """
        Get detailed information about a specific league.

        Args:
            league_id: League identifier

        Returns:
            League: League details
        """
        response = self._request('GET', f'/v1/leagues/{league_id}')
        return League(**response['data'])

    # Event Management
    def create_events_batch(self, events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple events in batch.

        Args:
            events_data: List of event data dictionaries

        Returns:
            Dict: Batch creation results

        Example:
            >>> events = [
            ...     {"league_id": "nba", "home_team": "Lakers", "away_team": "Celtics", "start_time": "2024-01-15T19:00:00Z"},
            ...     {"league_id": "nba", "home_team": "Warriors", "away_team": "Heat", "start_time": "2024-01-16T19:00:00Z"}
            ... ]
            >>> result = client.create_events_batch(events)
        """
        response = self._request('POST', '/v1/events/batch', json={'events': events_data})
        return response

    def create_events_from_csv(self, csv_file_path: str, league_id: str) -> Dict[str, Any]:
        """
        Create events from a CSV file.

        Args:
            csv_file_path: Path to CSV file
            league_id: League identifier for all events

        Returns:
            Dict: Batch creation results
        """
        import csv

        events = []
        with open(csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['league_id'] = league_id
                events.append(row)

        return self.create_events_batch(events)

    def get_events(
        self,
        league_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get events with optional filtering.

        Args:
            league_id: Filter by league
            start_date: Filter events after this date (ISO format)
            end_date: Filter events before this date (ISO format)
            limit: Maximum number of events to return

        Returns:
            List[Event]: List of events
        """
        params = {'limit': limit}
        if league_id:
            params['league_id'] = league_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        response = self._request('GET', '/v1/events', params=params)
        return [Event(**event) for event in response['data']]

    def get_historical_events(
        self,
        league_id: str,
        season: Optional[str] = None,
        limit: int = 1000
    ) -> List[Event]:
        """
        Get historical events for a league.

        Args:
            league_id: League identifier
            season: Filter by season (e.g., "2023-2024")
            limit: Maximum events to return

        Returns:
            List[Event]: Historical events
        """
        params = {'limit': limit}
        if season:
            params['season'] = season

        response = self._request('GET', f'/v1/leagues/{league_id}/history', params=params)
        return [Event(**event) for event in response['data']]

    # Sports Data
    def get_sports(self) -> List[Sport]:
        """
        Get all available sports types and classifications.

        Returns:
            List[Sport]: Available sports
        """
        response = self._request('GET', '/v1/sports')
        return [Sport(**sport) for sport in response['data']]

    def get_sport_buckets(self) -> List[str]:
        """
        Get available sport bucket classifications.

        Returns:
            List[str]: Sport bucket names (e.g., ['combat', 'large_field', 'team', 'racing'])
        """
        response = self._request('GET', '/v1/sports/buckets')
        return response['data']

    # Odds and Markets (for Sportsbooks)
    def get_odds(self, event_id: str) -> List[Odds]:
        """
        Get betting odds for an event.

        Args:
            event_id: Event identifier

        Returns:
            List[Odds]: Available betting odds
        """
        response = self._request('GET', f'/v1/events/{event_id}/odds')
        return [Odds(**odds) for odds in response['data']]

    def get_markets(self, league_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available betting markets.

        Args:
            league_id: Optional league filter

        Returns:
            List[Dict]: Available markets
        """
        params = {}
        if league_id:
            params['league_id'] = league_id

        response = self._request('GET', '/v1/markets', params=params)
        return response['data']

    # League Onboarding (for League Owners)
    def submit_league_questionnaire(self, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a league questionnaire for compliance review and sportsbook onboarding.

        Args:
            questionnaire: League questionnaire data

        Returns:
            Dict: Submission results including compliance score and recommendations
        """
        response = self._request('POST', '/v1/questionnaire', json=questionnaire)
        return response

    def get_compliance_status(self, league_id: str) -> Dict[str, Any]:
        """
        Get league compliance status and sportsbook onboarding progress.

        Args:
            league_id: League identifier

        Returns:
            Dict: Compliance status and recommendations
        """
        response = self._request('GET', f'/v1/leagues/{league_id}/compliance')
        return response

    def get_sportsbook_matches(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Get recommended sportsbook matches for a league.

        Args:
            league_id: League identifier

        Returns:
            List[Dict]: Recommended sportsbooks with compatibility scores
        """
        response = self._request('GET', f'/v1/leagues/{league_id}/matches')
        return response['data']

    # Utility methods
    def ping(self) -> Dict[str, Any]:
        """Test API connectivity"""
        return self._request('GET', '/health')

    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and capabilities"""
        return self._request('GET', '/v1/info')
