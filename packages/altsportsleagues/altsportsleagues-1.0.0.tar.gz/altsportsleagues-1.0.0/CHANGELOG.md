# Changelog

All notable changes to the AltSportsLeagues Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-12

### Added
- Initial release of AltSportsLeagues Python SDK
- Core client implementation with authentication
- League management functionality
  - Create, list, and retrieve leagues
  - Submit league questionnaires for compliance review
  - Get compliance status and sportsbook matches
- Event management functionality
  - Batch event creation from Python dictionaries
  - CSV import support for bulk event uploads
  - Historical event retrieval by league and season
  - Event filtering by date range and league
- Sports data access
  - Get available sports types and classifications
  - Sport bucket taxonomy (combat, large_field, team, racing, other)
- Betting market data (for sportsbooks)
  - Retrieve odds for specific events
  - Access available betting markets
- Comprehensive data models
  - `League`: League information and compliance status
  - `Event`: Sports event with teams, timing, and results
  - `Sport`: Sport types and classifications
  - `Odds`: Betting odds from various bookmakers
  - `LeagueQuestionnaire`: Compliance assessment form
  - `ComplianceReport`: Detailed compliance evaluation
- Exception handling with custom exceptions
  - `AuthenticationError`: API key authentication failures
  - `ValidationError`: Request validation errors
  - `RateLimitError`: API rate limit exceeded
  - `NotFoundError`: Resource not found
  - `PermissionError`: Insufficient permissions
  - `ServerError`: Internal server errors
  - `NetworkError`: Network connectivity issues
  - `ConfigurationError`: SDK configuration problems
- Comprehensive documentation
  - Quick start guide for league owners and sportsbooks
  - API reference with examples
  - Configuration and error handling guides
- Type hints and docstrings throughout codebase
- Support for Python 3.8+

### Features for League Owners
- Submit league information for compliance review
- Get personalized sportsbook recommendations
- Track onboarding progress and compliance score
- Batch upload events from CSV files
- Calculate compliance scores

### Features for Sportsbooks
- Discover new leagues filtered by sport type
- Access league compliance information
- Retrieve historical event data for analysis
- Get betting odds and market data
- Access comprehensive sports taxonomy

### Developer Experience
- Clean, intuitive API design
- Comprehensive error messages
- Built-in retry logic for rate limits
- Request/response logging support
- Environment variable configuration
- pip installable package
- Modern Python packaging with pyproject.toml

### Documentation
- README with quick start examples
- Installation guide
- API reference documentation
- Integration examples for common use cases
- Error handling guide
- Contributing guidelines

### Security
- API key authentication
- HTTPS-only communication
- Secure credential handling
- No sensitive data in logs

### Known Limitations
- CSV import requires specific column format (to be documented)
- Rate limiting applies per API key tier
- Historical data availability varies by league

## [Unreleased]

### Planned Features
- Async client support with `asyncio`
- WebSocket support for real-time event updates
- Enhanced caching for frequently accessed data
- CLI tool for common operations
- Integration with popular data analysis libraries (pandas, numpy)
- Batch delete operations for events
- Advanced filtering and search capabilities
- GraphQL API support
- Data export utilities (JSON, CSV, Excel)
- League analytics and insights module
- Webhook support for event notifications
- Enhanced compliance scoring algorithms
- Multi-language support for documentation

### Under Consideration
- Integration with popular betting platforms
- Machine learning models for betting predictions
- Enhanced data visualization tools
- Mobile SDK (iOS/Android)
- TypeScript/JavaScript SDK
- Go SDK
- Ruby SDK

---

## Release Process

1. Update version in `pyproject.toml` and `setup.py`
2. Update `__version__` in `altsportsleagues/__init__.py`
3. Document changes in this CHANGELOG
4. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
5. Push tag: `git push origin v1.0.0`
6. Build package: `python -m build`
7. Upload to PyPI: `twine upload dist/*`

## Version Numbering

We use Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

## Support

- **Documentation**: https://docs.altsportsleagues.ai
- **Issues**: https://github.com/altsportsleagues/altsportsleagues-python/issues
- **Email**: support@altsportsleagues.ai
