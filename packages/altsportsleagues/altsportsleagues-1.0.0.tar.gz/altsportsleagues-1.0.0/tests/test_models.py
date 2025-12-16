"""
Unit tests for AltSportsLeagues data models
"""

import pytest
from datetime import datetime
from altsportsleagues.models import (
    League, Event, Sport, Odds, LeagueQuestionnaire,
    ComplianceReport, SportBucket
)


class TestLeagueModel:
    """Test suite for League model"""

    def test_league_initialization(self):
        """Test League is properly initialized"""
        league = League(
            league_id="test_123",
            league_name="Test League",
            sport_bucket="team",
            contact_email="test@example.com",
            compliance_score=80
        )

        assert league.league_id == "test_123"
        assert league.league_name == "Test League"
        assert league.sport_bucket == "team"
        assert league.contact_email == "test@example.com"
        assert league.compliance_score == 80

    def test_league_is_compliant(self):
        """Test compliance check method"""
        compliant_league = League(
            league_id="1",
            league_name="Compliant League",
            sport_bucket="team",
            contact_email="test@example.com",
            compliance_score=75
        )
        assert compliant_league.is_compliant() is True

        non_compliant_league = League(
            league_id="2",
            league_name="Non-compliant League",
            sport_bucket="team",
            contact_email="test@example.com",
            compliance_score=50
        )
        assert non_compliant_league.is_compliant() is False

    def test_league_onboarding_progress(self):
        """Test onboarding status messages"""
        league = League(
            league_id="1",
            league_name="Test",
            sport_bucket="team",
            contact_email="test@example.com",
            onboarding_status="pending"
        )
        assert "awaiting review" in league.get_onboarding_progress()

        league.onboarding_status = "approved"
        assert "Approved" in league.get_onboarding_progress()


class TestEventModel:
    """Test suite for Event model"""

    def test_event_initialization(self):
        """Test Event is properly initialized"""
        event = Event(
            event_id="evt_123",
            league_id="nba",
            home_team="Lakers",
            away_team="Celtics",
            start_time="2024-01-15T19:00:00Z",
            venue="Crypto.com Arena"
        )

        assert event.event_id == "evt_123"
        assert event.league_id == "nba"
        assert event.home_team == "Lakers"
        assert event.away_team == "Celtics"
        assert event.venue == "Crypto.com Arena"

    def test_event_get_winner(self):
        """Test winner determination"""
        # Home team wins
        event = Event(
            event_id="1",
            league_id="nba",
            home_team="Lakers",
            away_team="Celtics",
            start_time="2024-01-15T19:00:00Z",
            status="completed",
            home_score=110,
            away_score=105
        )
        assert event.get_winner() == "Lakers"

        # Away team wins
        event.home_score = 95
        event.away_score = 100
        assert event.get_winner() == "Celtics"

        # Draw
        event.home_score = 100
        event.away_score = 100
        assert event.get_winner() == "draw"

        # Event not completed
        event.status = "scheduled"
        assert event.get_winner() is None


class TestSportModel:
    """Test suite for Sport model"""

    def test_sport_initialization(self):
        """Test Sport is properly initialized"""
        sport = Sport(
            sport_id="basketball",
            name="Basketball",
            bucket=SportBucket.TEAM,
            popularity_score=95
        )

        assert sport.sport_id == "basketball"
        assert sport.name == "Basketball"
        assert sport.bucket == SportBucket.TEAM
        assert sport.popularity_score == 95


class TestLeagueQuestionnaire:
    """Test suite for LeagueQuestionnaire model"""

    def test_questionnaire_initialization(self):
        """Test LeagueQuestionnaire is properly initialized"""
        questionnaire = LeagueQuestionnaire(
            league_name="Test League",
            contact_email="test@example.com",
            sport_bucket=SportBucket.TEAM,
            has_official_rules=True,
            interested_in_betting=True
        )

        assert questionnaire.league_name == "Test League"
        assert questionnaire.has_official_rules is True
        assert questionnaire.interested_in_betting is True

    def test_questionnaire_to_dict(self):
        """Test conversion to dictionary"""
        questionnaire = LeagueQuestionnaire(
            league_name="Test League",
            contact_email="test@example.com",
            sport_bucket=SportBucket.TEAM
        )

        data = questionnaire.to_dict()
        assert isinstance(data, dict)
        assert data["league_name"] == "Test League"
        assert data["contact_email"] == "test@example.com"
        assert data["sport_bucket"] == "team"

    def test_compliance_score_calculation(self):
        """Test compliance score calculation"""
        # Minimal questionnaire
        minimal = LeagueQuestionnaire(
            league_name="Minimal",
            contact_email="test@example.com",
            sport_bucket=SportBucket.TEAM
        )
        assert minimal.calculate_compliance_score() < 30

        # Complete questionnaire
        complete = LeagueQuestionnaire(
            league_name="Complete",
            contact_email="test@example.com",
            sport_bucket=SportBucket.TEAM,
            description="A great league",
            website="https://example.com",
            location="New York",
            founded_year=2020,
            has_official_rules=True,
            has_player_contracts=True,
            has_liability_insurance=True,
            has_drug_testing_program=True,
            has_integrity_officer=True,
            interested_in_betting=True,
            preferred_betting_model="fixed_odds"
        )
        score = complete.calculate_compliance_score()
        assert score == 100


class TestOddsModel:
    """Test suite for Odds model"""

    def test_odds_initialization(self):
        """Test Odds is properly initialized"""
        odds = Odds(
            odds_id="odds_123",
            event_id="evt_123",
            bookmaker="DraftKings",
            market="moneyline",
            selections=[
                {"name": "Lakers", "odds": 1.75},
                {"name": "Celtics", "odds": 2.10}
            ]
        )

        assert odds.odds_id == "odds_123"
        assert odds.bookmaker == "DraftKings"
        assert odds.market == "moneyline"
        assert len(odds.selections) == 2

    def test_get_best_odds(self):
        """Test retrieving odds for specific selection"""
        odds = Odds(
            odds_id="1",
            event_id="evt_1",
            bookmaker="Test",
            market="moneyline",
            selections=[
                {"name": "Team A", "odds": 1.75},
                {"name": "Team B", "odds": 2.10}
            ]
        )

        assert odds.get_best_odds("Team A") == 1.75
        assert odds.get_best_odds("Team B") == 2.10
        assert odds.get_best_odds("Team C") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
