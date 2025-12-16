"""
Pytest Configuration

Shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "test_session_prefix": "test_session_",
        "timeout_simple": 1.0,
        "timeout_complex": 5.0,
        "timeout_export": 3.0
    }


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests"""
    import logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise in tests
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

