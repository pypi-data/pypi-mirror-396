"""
Unit tests for AltSportsLeagues client
"""

import pytest
from unittest.mock import Mock, patch
from altsportsleagues import AltSportsLeagues, AuthenticationError, ValidationError
from altsportsleagues.models import League, Event, Sport


class TestAltSportsLeaguesClient:
    """Test suite for the main client"""

    def test_client_initialization(self):
        """Test client is properly initialized with API key"""
        client = AltSportsLeagues(api_key="test_key_12345")
        assert client.api_key == "test_key_12345"
        assert client.base_url == "https://api.altsportsleagues.ai"
        assert client.timeout == 30
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test_key_12345"

    def test_client_custom_base_url(self):
        """Test client accepts custom base URL"""
        client = AltSportsLeagues(
            api_key="test_key",
            base_url="https://staging.altsportsleagues.ai"
        )
        assert client.base_url == "https://staging.altsportsleagues.ai"

    def test_client_custom_timeout(self):
        """Test client accepts custom timeout"""
        client = AltSportsLeagues(api_key="test_key", timeout=60)
        assert client.timeout == 60

    @patch('requests.Session.request')
    def test_successful_api_request(self, mock_request):
        """Test successful API request returns data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "league_id": "nba",
                    "league_name": "NBA",
                    "sport_bucket": "team",
                    "contact_email": "contact@nba.com"
                }
            ]
        }
        mock_request.return_value = mock_response

        client = AltSportsLeagues(api_key="test_key")
        leagues = client.get_leagues()

        assert len(leagues) == 1
        assert isinstance(leagues[0], League)
        assert leagues[0].league_name == "NBA"

    @patch('requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error is raised for 401 response"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")

        from requests.exceptions import HTTPError
        error = HTTPError()
        error.response = mock_response
        mock_request.side_effect = error

        client = AltSportsLeagues(api_key="invalid_key")

        with pytest.raises(AuthenticationError):
            client.get_leagues()

    @patch('requests.Session.request')
    def test_validation_error(self, mock_request):
        """Test validation error is raised for 422 response"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Invalid request data"}

        from requests.exceptions import HTTPError
        error = HTTPError()
        error.response = mock_response
        mock_request.side_effect = error

        client = AltSportsLeagues(api_key="test_key")

        with pytest.raises(ValidationError):
            client.create_league({})

    @patch('requests.Session.request')
    def test_create_league(self, mock_request):
        """Test creating a new league"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "data": {
                "league_id": "test_123",
                "league_name": "Test League",
                "sport_bucket": "team",
                "contact_email": "test@example.com",
                "compliance_score": 75
            }
        }
        mock_request.return_value = mock_response

        client = AltSportsLeagues(api_key="test_key")
        league = client.create_league({
            "league_name": "Test League",
            "sport_bucket": "team",
            "contact_email": "test@example.com"
        })

        assert isinstance(league, League)
        assert league.league_name == "Test League"
        assert league.compliance_score == 75

    @patch('requests.Session.request')
    def test_batch_create_events(self, mock_request):
        """Test batch creating events"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "successful": 2,
            "failed": 0,
            "errors": []
        }
        mock_request.return_value = mock_response

        client = AltSportsLeagues(api_key="test_key")
        result = client.create_events_batch([
            {
                "league_id": "nba",
                "home_team": "Lakers",
                "away_team": "Celtics",
                "start_time": "2024-01-15T19:00:00Z"
            },
            {
                "league_id": "nba",
                "home_team": "Warriors",
                "away_team": "Heat",
                "start_time": "2024-01-16T19:00:00Z"
            }
        ])

        assert result["successful"] == 2
        assert result["failed"] == 0

    @patch('requests.Session.request')
    def test_get_sports(self, mock_request):
        """Test retrieving available sports"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "sport_id": "basketball",
                    "name": "Basketball",
                    "bucket": "team",
                    "popularity_score": 95
                }
            ]
        }
        mock_request.return_value = mock_response

        client = AltSportsLeagues(api_key="test_key")
        sports = client.get_sports()

        assert len(sports) == 1
        assert isinstance(sports[0], Sport)
        assert sports[0].name == "Basketball"
        assert sports[0].bucket == "team"

    def test_ping(self):
        """Test API connectivity check"""
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_request.return_value = mock_response

            client = AltSportsLeagues(api_key="test_key")
            result = client.ping()

            assert result["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
