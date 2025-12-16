# AltSportsLeagues Python SDK

[![PyPI version](https://badge.fury.io/py/altsportsleagues.svg)](https://pypi.org/project/altsportsleagues/)
[![Python versions](https://img.shields.io/pypi/pyversions/altsportsleagues.svg)](https://pypi.org/project/altsportsleagues/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for the AltSportsLeagues platform. Enable league owners to get compliant and onboarded with sportsbooks, and help sportsbooks discover new betting opportunities.

## 🚀 Installation

```bash
pip install altsportsleagues
```

## 📖 Quick Start

### For League Owners

```python
from altsportsleagues import AltSportsLeagues

# Initialize client
client = AltSportsLeagues(api_key="your_api_key_here")

# Create a new league
league = client.create_league({
    "league_name": "My Basketball League",
    "sport_bucket": "team",
    "contact_email": "admin@myleague.com",
    "description": "A competitive basketball league for local communities",
    "website": "https://mybasketballleague.com",
    "location": "San Francisco, CA",
    "number_of_teams": 12,
    "has_official_rules": True,
    "interested_in_betting": True
})

print(f"Created league: {league.league_name}")
print(f"Compliance score: {league.compliance_score}")

# Submit for compliance review and sportsbook onboarding
questionnaire = {
    "league_name": "My Basketball League",
    "contact_email": "admin@myleague.com",
    "sport_bucket": "team",
    "has_official_rules": True,
    "has_liability_insurance": True,
    "interested_in_betting": True
}

result = client.submit_league_questionnaire(questionnaire)
print(f"Onboarding status: {result['status']}")

# Check compliance status
status = client.get_compliance_status(league.league_id)
print(f"Compliance level: {status['compliance_level']}")

# Get recommended sportsbook matches
matches = client.get_sportsbook_matches(league.league_id)
for match in matches:
    print(f"Recommended sportsbook: {match['sportsbook_name']} (compatibility: {match['compatibility_score']})")
```

### For Sportsbooks

```python
from altsportsleagues import AltSportsLeagues

# Initialize client
client = AltSportsLeagues(api_key="your_api_key_here")

# Discover new leagues to onboard
leagues = client.get_leagues()
print(f"Found {len(leagues)} leagues")

# Filter by sport type
basketball_leagues = client.get_leagues(sport_type="basketball")
print(f"Found {len(basketball_leagues)} basketball leagues")

# Get detailed league information
for league in basketball_leagues[:5]:  # First 5 leagues
    detail = client.get_league(league.league_id)
    print(f"{detail.league_name} - Compliance: {detail.compliance_score}/100")
    print(f"  Status: {detail.get_onboarding_progress()}")

# Access historical events for analysis
events = client.get_historical_events("nba", season="2023-2024", limit=100)
print(f"Retrieved {len(events)} NBA events from 2023-2024 season")

# Get betting odds for an upcoming event
odds = client.get_odds("event_123")
for odd in odds:
    print(f"{odd.bookmaker}: {odd.market}")
    for selection in odd.selections:
        print(f"  {selection['name']}: {selection['odds']}")
```

### Batch Event Management

```python
# Create events from CSV
result = client.create_events_from_csv("my_events.csv", "my_league_id")
print(f"Created {result['successful']} events, {result['failed']} failed")

# Or create events programmatically
events_data = [
    {
        "league_id": "nba",
        "home_team": "Los Angeles Lakers",
        "away_team": "Boston Celtics",
        "start_time": "2024-01-15T20:00:00Z",
        "venue": "Crypto.com Arena",
        "season": "2023-2024"
    },
    {
        "league_id": "nba",
        "home_team": "Golden State Warriors",
        "away_team": "Miami Heat",
        "start_time": "2024-01-16T19:30:00Z",
        "venue": "Chase Center",
        "season": "2023-2024"
    }
]

result = client.create_events_batch(events_data)
print(f"Batch creation result: {result}")
```

## 📚 API Reference

### Client Initialization

```python
from altsportsleagues import AltSportsLeagues

client = AltSportsLeagues(
    api_key="your_api_key",
    base_url="https://api.altsportsleagues.ai",  # Optional, defaults to production
    timeout=30  # Optional, request timeout in seconds
)
```

### League Management

#### Creating Leagues
```python
league = client.create_league({
    "league_name": "My League",
    "sport_bucket": "team",  # combat, large_field, team, racing, other
    "contact_email": "admin@myleague.com",
    "description": "League description",
    "website": "https://myleague.com",
    "location": "City, State",
    "number_of_teams": 10,
    "interested_in_betting": True
})
```

#### Listing Leagues
```python
# All leagues
all_leagues = client.get_leagues()

# Filter by sport type
basketball_leagues = client.get_leagues(sport_type="basketball")
```

#### Getting League Details
```python
league = client.get_league("league_id")
print(f"Name: {league.league_name}")
print(f"Compliance Score: {league.compliance_score}")
print(f"Onboarding Status: {league.get_onboarding_progress()}")
```

### Event Management

#### Creating Events
```python
# Single event creation
event = client.create_event({
    "league_id": "nba",
    "home_team": "Lakers",
    "away_team": "Celtics",
    "start_time": "2024-01-15T20:00:00Z",
    "venue": "Crypto.com Arena"
})

# Batch creation
events = client.create_events_batch([
    {"league_id": "nba", "home_team": "Lakers", "away_team": "Celtics", "start_time": "2024-01-15T20:00:00Z"},
    {"league_id": "nba", "home_team": "Warriors", "away_team": "Heat", "start_time": "2024-01-16T19:30:00Z"}
])
```

#### Querying Events
```python
# Get upcoming events
upcoming = client.get_events(limit=50)

# Filter by league and date range
nba_events = client.get_events(
    league_id="nba",
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=100
)

# Get historical events
historical = client.get_historical_events("nba", season="2023-2024")
```

### Sports Data

#### Available Sports
```python
sports = client.get_sports()
for sport in sports:
    print(f"{sport.name} ({sport.bucket}) - Popularity: {sport.popularity_score}")

# Get sport classifications
buckets = client.get_sport_buckets()
print(f"Available buckets: {buckets}")
```

### Betting Data (Sportsbooks)

#### Odds and Markets
```python
# Get odds for a specific event
odds = client.get_odds("event_123")
for odd in odds:
    print(f"Bookmaker: {odd.bookmaker}")
    print(f"Market: {odd.market}")
    print(f"Selections: {odd.selections}")

# Get available markets
markets = client.get_markets()
markets_by_league = client.get_markets(league_id="nba")
```

### Compliance & Onboarding (League Owners)

#### Submit Questionnaire
```python
questionnaire = {
    "league_name": "My League",
    "contact_email": "admin@myleague.com",
    "sport_bucket": "team",
    "has_official_rules": True,
    "has_liability_insurance": True,
    "has_player_contracts": True,
    "interested_in_betting": True,
    "preferred_betting_model": "fixed_odds"
}

result = client.submit_league_questionnaire(questionnaire)
```

#### Check Compliance Status
```python
status = client.get_compliance_status("league_id")
print(f"Overall Score: {status['overall_score']}/100")
print(f"Compliance Level: {status['compliance_level']}")
print(f"Strengths: {status['strengths']}")
print(f"Gaps: {status['gaps']}")
```

#### Get Sportsbook Matches
```python
matches = client.get_sportsbook_matches("league_id")
for match in matches:
    print(f"Sportsbook: {match['sportsbook_name']}")
    print(f"Compatibility: {match['compatibility_score']}%")
    print(f"Requirements: {match['requirements']}")
```

## 🔧 Configuration

### Environment Variables

Set your API key as an environment variable:

```bash
export ALTSPORTSLEAGUES_API_KEY="your_api_key_here"
```

### Programmatic Configuration

```python
import os
from altsportsleagues import AltSportsLeagues

api_key = os.getenv("ALTSPORTSLEAGUES_API_KEY")
client = AltSportsLeagues(api_key=api_key)
```

## 🏗️ Architecture Overview

### Platform Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   League Owners │    │ AltSportsLeagues │    │   Sportsbooks   │
│                 │    │     Platform     │    │                 │
│ • Submit leagues│    │                  │    │ • Discover      │
│ • Compliance    │◄──►│ • League analysis│◄──►│   leagues       │
│ • Onboarding    │    │ • Compliance     │    │ • Access odds   │
│ • Matchmaking   │    │   scoring        │    │ • Data feeds    │
└─────────────────┘    │ • Sportsbook      │    └─────────────────┘
                       │   matching       │
                       └──────────────────┘
```

### Data Flow

1. **League Submission**: League owners submit detailed questionnaires
2. **Compliance Analysis**: AI-powered analysis of league readiness
3. **Sportsbook Matching**: Algorithm matches leagues with compatible sportsbooks
4. **Onboarding**: Streamlined process for league-sportsbook integration
5. **Data Provision**: Real-time data feeds for betting markets

## 📊 Data Models

### Core Entities

- **League**: Sports league information and compliance status
- **Event**: Individual sporting events with teams, timing, and results
- **Sport**: Sport classifications and metadata
- **Odds**: Betting odds from various bookmakers
- **ComplianceReport**: Detailed compliance assessment results

### Sport Buckets

- **combat**: Fighting sports (MMA, boxing, wrestling)
- **large_field**: Field sports (football, soccer, baseball)
- **team**: Team sports (basketball, hockey, volleyball)
- **racing**: Racing sports (horse racing, auto racing, cycling)
- **other**: Miscellaneous sports

## 🔒 Security & Compliance

- **API Key Authentication**: Secure API key-based authentication
- **Rate Limiting**: Built-in rate limiting and quota management
- **Data Privacy**: Compliance with sports data privacy regulations
- **Audit Logging**: Comprehensive logging of all API interactions

## 🚦 Error Handling

The SDK provides specific exception types for different error conditions:

```python
from altsportsleagues import (
    AltSportsLeagues,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError
)

try:
    client = AltSportsLeagues(api_key="invalid_key")
    leagues = client.get_leagues()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e}")
```

## 📈 Rate Limits

- **Free Tier**: 1,000 requests per month
- **Developer Tier**: 10,000 requests per month
- **Enterprise Tier**: Unlimited requests

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## 🔗 Links

- **Homepage**: [altsportsleagues.ai](https://altsportsleagues.ai)
- **Documentation**: [docs.altsportsleagues.ai](https://docs.altsportsleagues.ai)
- **API Reference**: [api.altsportsleagues.ai](https://api.altsportsleagues.ai)
- **GitHub**: [github.com/altsportsleagues](https://github.com/altsportsleagues)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by the AltSportsLeagues.ai team**
