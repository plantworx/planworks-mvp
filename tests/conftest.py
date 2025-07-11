# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import asyncio
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, patch

# Add app to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.adk_simulation import LlmAgent, InvocationContext, SessionState
from app.plantworks_agents import (
    learn_agent, grow_agent, local_environment_agent, marketplace_agent,
    plantworks_main_agent
)
from app.plantworks_tools import (
    PlantSearchInput, WeatherInput, MarketplaceSearchInput,
    plant_database_search, weather_lookup, marketplace_search
)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session_state():
    """Mock session state for testing."""
    return SessionState({
        "user_query": "Test query",
        "session_id": "test_session_123",
        "user_location": "San Francisco, CA"
    })


@pytest.fixture
def mock_invocation_context(mock_session_state):
    """Mock invocation context for agent testing."""
    return InvocationContext(mock_session_state.state)


@pytest.fixture
def sample_plant_data():
    """Sample plant data for testing."""
    return {
        "scientific_name": "Monstera deliciosa",
        "common_name": "Swiss Cheese Plant",
        "family": "Araceae",
        "care_level": "Easy",
        "light_requirements": "Bright, indirect light",
        "water_frequency": "Weekly"
    }


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing."""
    return {
        "location": "San Francisco, CA",
        "current": {
            "temperature": 22,
            "humidity": 65,
            "description": "partly cloudy"
        },
        "forecast": [
            {
                "date": "2025-07-11",
                "temperature": 23,
                "humidity": 60,
                "description": "sunny"
            }
        ]
    }


@pytest.fixture
def sample_marketplace_data():
    """Sample marketplace data for testing."""
    return {
        "plant_name": "snake plant",
        "products": [
            {
                "seller": "The Sill",
                "price": 28.00,
                "size": "4-inch pot",
                "availability": "In Stock",
                "rating": 4.9,
                "reviews": 2100
            },
            {
                "seller": "Planterina", 
                "price": 22.00,
                "size": "4-inch pot",
                "availability": "In Stock",
                "rating": 4.8,
                "reviews": 890
            }
        ]
    }


@pytest.fixture
def mock_api_responses():
    """Mock external API responses."""
    return {
        "trefle_api": {
            "data": [
                {
                    "scientific_name": "Monstera deliciosa",
                    "common_name": "Swiss Cheese Plant",
                    "family": "Araceae",
                    "genus": "Monstera"
                }
            ]
        },
        "openweather_api": {
            "main": {
                "temp": 22,
                "humidity": 65,
                "pressure": 1013
            },
            "weather": [
                {
                    "description": "partly cloudy"
                }
            ],
            "wind": {
                "speed": 5.2
            }
        }
    }


@pytest.fixture
def test_agents():
    """Provide test agents for integration testing."""
    return {
        "learn_agent": learn_agent,
        "grow_agent": grow_agent,
        "local_environment_agent": local_environment_agent,
        "marketplace_agent": marketplace_agent,
        "main_agent": plantworks_main_agent
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "plantworks-test"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_external_apis():
    """Mock external API calls for testing."""
    with patch('requests.get') as mock_get, \
         patch('app.plantworks_tools.get_coordinates') as mock_coords:
        
        # Mock geocoding
        mock_coords.return_value = (37.7749, -122.4194)  # San Francisco coordinates
        
        # Mock API responses
        mock_response = Mock()
        mock_response.json.return_value = {
            "main": {"temp": 22, "humidity": 65},
            "weather": [{"description": "partly cloudy"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        yield {
            "mock_get": mock_get,
            "mock_coords": mock_coords,
            "mock_response": mock_response
        }


class TestConfig:
    """Test configuration constants."""
    
    # Test timeouts
    UNIT_TEST_TIMEOUT = 5
    INTEGRATION_TEST_TIMEOUT = 10
    LOAD_TEST_TIMEOUT = 30
    
    # Load test parameters
    CONCURRENT_USERS = 10
    REQUESTS_PER_USER = 5
    RAMP_UP_TIME = 2
    
    # Test data
    TEST_PLANTS = ["monstera", "snake plant", "fiddle leaf fig", "pothos"]
    TEST_LOCATIONS = ["San Francisco, CA", "New York, NY", "Austin, TX"]
    TEST_QUERIES = [
        "What is Monstera deliciosa?",
        "How do I care for a snake plant?",
        "Where can I buy a fiddle leaf fig?",
        "What native plants grow in California?"
    ]

