"""
Data models for AltSportsLeagues API
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class SportBucket(str, Enum):
    """Sport classification buckets"""
    COMBAT = "combat"
    LARGE_FIELD = "large_field"
    TEAM = "team"
    RACING = "racing"
    OTHER = "other"


class Sport:
    """Sports type definition"""

    def __init__(self, sport_id: str, name: str, bucket: SportBucket, **kwargs):
        self.sport_id = sport_id
        self.name = name
        self.bucket = bucket
        self.description = kwargs.get('description', '')
        self.popularity_score = kwargs.get('popularity_score', 0)
        self.betting_volume = kwargs.get('betting_volume', 0)

    def __repr__(self):
        return f"Sport(id='{self.sport_id}', name='{self.name}', bucket='{self.bucket}')"


class League:
    """Sports league information"""

    def __init__(
        self,
        league_id: str,
        league_name: str,
        sport_bucket: SportBucket,
        contact_email: str,
        **kwargs
    ):
        self.league_id = league_id
        self.league_name = league_name
        self.sport_bucket = sport_bucket
        self.contact_email = contact_email

        # Optional fields
        self.description = kwargs.get('description', '')
        self.website = kwargs.get('website', '')
        self.location = kwargs.get('location', '')
        self.founded_year = kwargs.get('founded_year')
        self.compliance_score = kwargs.get('compliance_score', 0)
        self.onboarding_status = kwargs.get('onboarding_status', 'pending')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')

    def __repr__(self):
        return f"League(id='{self.league_id}', name='{self.league_name}')"

    def is_compliant(self) -> bool:
        """Check if league meets basic compliance standards"""
        return self.compliance_score >= 70

    def get_onboarding_progress(self) -> str:
        """Get human-readable onboarding status"""
        status_map = {
            'pending': 'Application submitted, awaiting review',
            'under_review': 'Compliance review in progress',
            'approved': 'Approved for sportsbook onboarding',
            'onboarded': 'Successfully onboarded with sportsbooks',
            'rejected': 'Application requires revisions'
        }
        return status_map.get(self.onboarding_status, self.onboarding_status)


class Event:
    """Sports event information"""

    def __init__(
        self,
        event_id: str,
        league_id: str,
        home_team: str,
        away_team: str,
        start_time: str,
        **kwargs
    ):
        self.event_id = event_id
        self.league_id = league_id
        self.home_team = home_team
        self.away_team = away_team
        self.start_time = start_time

        # Optional fields
        self.venue = kwargs.get('venue', '')
        self.status = kwargs.get('status', 'scheduled')  # scheduled, in_progress, completed, cancelled
        self.home_score = kwargs.get('home_score')
        self.away_score = kwargs.get('away_score')
        self.season = kwargs.get('season', '')
        self.round = kwargs.get('round', '')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')

    def __repr__(self):
        return f"Event(id='{self.event_id}', {self.home_team} vs {self.away_team})"

    def is_upcoming(self) -> bool:
        """Check if event is in the future"""
        if isinstance(self.start_time, str):
            event_time = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        else:
            event_time = self.start_time
        return event_time > datetime.now(event_time.tzinfo)

    def get_winner(self) -> Optional[str]:
        """Get the winning team if event is completed"""
        if self.status != 'completed':
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        else:
            return 'draw'  # or None for tie


class Odds:
    """Betting odds for an event"""

    def __init__(
        self,
        odds_id: str,
        event_id: str,
        bookmaker: str,
        market: str,
        **kwargs
    ):
        self.odds_id = odds_id
        self.event_id = event_id
        self.bookmaker = bookmaker
        self.market = market

        # Market-specific data
        self.selections = kwargs.get('selections', [])  # List of betting options
        self.last_updated = kwargs.get('last_updated')
        self.is_live = kwargs.get('is_live', False)

    def __repr__(self):
        return f"Odds(event='{self.event_id}', bookmaker='{self.bookmaker}', market='{self.market}')"

    def get_best_odds(self, selection: str) -> Optional[float]:
        """Get the best odds for a specific selection"""
        for sel in self.selections:
            if sel.get('name') == selection:
                return sel.get('odds')
        return None


class LeagueQuestionnaire:
    """
    League questionnaire for compliance assessment and sportsbook onboarding.

    This is used by league owners to submit their league information for review
    and to get matched with appropriate sportsbooks.
    """

    def __init__(
        self,
        league_name: str,
        contact_email: str,
        sport_bucket: SportBucket,
        **kwargs
    ):
        self.league_name = league_name
        self.contact_email = contact_email
        self.sport_bucket = sport_bucket

        # Basic information
        self.description = kwargs.get('description', '')
        self.website = kwargs.get('website', '')
        self.location = kwargs.get('location', '')
        self.founded_year = kwargs.get('founded_year')
        self.number_of_teams = kwargs.get('number_of_teams')
        self.average_attendance = kwargs.get('average_attendance')
        self.annual_budget = kwargs.get('annual_budget')

        # Compliance information
        self.has_official_rules = kwargs.get('has_official_rules', False)
        self.has_player_contracts = kwargs.get('has_player_contracts', False)
        self.has_liability_insurance = kwargs.get('has_liability_insurance', False)
        self.has_drug_testing_program = kwargs.get('has_drug_testing_program', False)
        self.has_integrity_officer = kwargs.get('has_integrity_officer', False)

        # Betting interest
        self.interested_in_betting = kwargs.get('interested_in_betting', False)
        self.preferred_betting_model = kwargs.get('preferred_betting_model', '')  # 'pool', 'fixed_odds', 'both'
        self.expected_betting_volume = kwargs.get('expected_betting_volume', '')

        # Additional info
        self.additional_notes = kwargs.get('additional_notes', '')

    def __repr__(self):
        return f"LeagueQuestionnaire(name='{self.league_name}', sport='{self.sport_bucket}')"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API submission"""
        return {
            'league_name': self.league_name,
            'contact_email': self.contact_email,
            'sport_bucket': self.sport_bucket.value,
            'description': self.description,
            'website': self.website,
            'location': self.location,
            'founded_year': self.founded_year,
            'number_of_teams': self.number_of_teams,
            'average_attendance': self.average_attendance,
            'annual_budget': self.annual_budget,
            'has_official_rules': self.has_official_rules,
            'has_player_contracts': self.has_player_contracts,
            'has_liability_insurance': self.has_liability_insurance,
            'has_drug_testing_program': self.has_drug_testing_program,
            'has_integrity_officer': self.has_integrity_officer,
            'interested_in_betting': self.interested_in_betting,
            'preferred_betting_model': self.preferred_betting_model,
            'expected_betting_volume': self.expected_betting_volume,
            'additional_notes': self.additional_notes,
        }

    def calculate_compliance_score(self) -> int:
        """Calculate basic compliance score based on provided information"""
        score = 0
        max_score = 100

        # Basic information (20 points)
        if self.description:
            score += 5
        if self.website:
            score += 5
        if self.location:
            score += 5
        if self.founded_year:
            score += 5

        # Compliance requirements (60 points)
        compliance_items = [
            self.has_official_rules,
            self.has_player_contracts,
            self.has_liability_insurance,
            self.has_drug_testing_program,
            self.has_integrity_officer,
        ]
        score += sum(compliance_items) * 12

        # Betting readiness (20 points)
        if self.interested_in_betting:
            score += 10
            if self.preferred_betting_model:
                score += 10

        return min(score, max_score)


class ComplianceReport:
    """Compliance assessment report for leagues"""

    def __init__(self, league_id: str, **kwargs):
        self.league_id = league_id
        self.overall_score = kwargs.get('overall_score', 0)
        self.compliance_level = kwargs.get('compliance_level', 'unknown')  # bronze, silver, gold, platinum
        self.strengths = kwargs.get('strengths', [])
        self.gaps = kwargs.get('gaps', [])
        self.recommendations = kwargs.get('recommendations', [])
        self.matched_sportsbooks = kwargs.get('matched_sportsbooks', [])
        self.generated_at = kwargs.get('generated_at', datetime.now())

    def __repr__(self):
        return f"ComplianceReport(league='{self.league_id}', score={self.overall_score}, level='{self.compliance_level}')"

    def get_required_actions(self) -> List[str]:
        """Get list of required actions to improve compliance"""
        return self.gaps + self.recommendations
