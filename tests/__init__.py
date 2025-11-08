"""
PrayerOffline Test Suite

Test organization:
- unit: Individual component tests (isolation)
- integration: Component interaction tests
- fixtures: Reusable test data and mock objects

Run tests:
  pytest tests/                           # All tests
  pytest tests/ -v                        # Verbose output
  pytest tests/ -m unit                   # Unit tests only
  pytest tests/ -m integration            # Integration tests only
  pytest tests/ --cov=prayer_offline      # With coverage
  pytest tests/ -k test_prayer            # Specific pattern
"""

import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

__all__ = ["TEST_DATA_DIR"]