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
from unittest.mock import patch, Mock
from app.plantworks_tools import (
    plant_database_search, weather_lookup, marketplace_search,
    native_plant_finder, soil_analyzer, hardiness_zone_lookup,
    PlantSearchInput, WeatherInput, MarketplaceSearchInput,
    NativePlantInput, SoilAnalysisInput, HardinessZoneInput
)


class TestPlantDatabaseSearch:
    """Unit tests for plant database search tool."""
    
    def test_plant_search_basic_query(self):
        """Test basic plant search functionality."""
        input_data = PlantSearchInput(query="monstera", limit=5)
        result = plant_database_search(input_data)
        
        assert "query" in result
        assert "results" in result
        assert "total_found" in result
        assert result["query"] == "monstera"
        assert isinstance(result["results"], list)
        assert result["total_found"] >= 0
    
    def test_plant_search_with_limit(self):
        """Test plant search respects limit parameter."""
        input_data = PlantSearchInput(query="plant", limit=2)
        result = plant_database_search(input_data)
        
        assert len(result["results"]) <= 2
    
    def test_plant_search_empty_query(self):
        """Test plant search with empty query."""
        input_data = PlantSearchInput(query="", limit=5)
        result = plant_database_search(input_data)
        
        assert "results" in result
        assert isinstance(result["results"], list)
    
    def test_plant_search_scientific_name(self):
        """Test search by scientific name."""
        input_data = PlantSearchInput(query="Monstera deliciosa", limit=5)
        result = plant_database_search(input_data)
        
        # Should find monstera in mock data
        assert result["total_found"] > 0
        found_monstera = any("monstera" in plant.get("scientific_name", "").lower() 
                           for plant in result["results"])
        assert found_monstera
    
    @patch('app.plantworks_tools.make_api_request')
    def test_plant_search_with_api_key(self, mock_api):
        """Test plant search with external API integration."""
        # Mock Trefle API response
        mock_api.return_value = {
            "data": [
                {
                    "scientific_name": "Monstera deliciosa",
                    "common_name": "Swiss Cheese Plant",
                    "family": "Araceae"
                }
            ]
        }
        
        with patch.dict('os.environ', {'TREFLE_API_KEY': 'test_key'}):
            input_data = PlantSearchInput(query="monstera", limit=5)
            result = plant_database_search(input_data)
            
            assert "Trefle.io" in result["sources"]
            mock_api.assert_called_once()


class TestWeatherLookup:
    """Unit tests for weather lookup tool."""
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_weather_lookup_basic(self, mock_coords):
        """Test basic weather lookup functionality."""
        mock_coords.return_value = (37.7749, -122.4194)  # San Francisco
        
        input_data = WeatherInput(location="San Francisco, CA", days=3)
        result = weather_lookup(input_data)
        
        assert "location" in result
        assert "current" in result
        assert "forecast" in result
        assert "growing_conditions" in result
        assert result["location"] == "San Francisco, CA"
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_weather_lookup_invalid_location(self, mock_coords):
        """Test weather lookup with invalid location."""
        mock_coords.return_value = None
        
        input_data = WeatherInput(location="Invalid Location", days=3)
        result = weather_lookup(input_data)
        
        assert "error" in result
    
    @patch('app.plantworks_tools.get_coordinates')
    @patch('app.plantworks_tools.make_api_request')
    def test_weather_lookup_with_api(self, mock_api, mock_coords):
        """Test weather lookup with OpenWeather API."""
        mock_coords.return_value = (37.7749, -122.4194)
        mock_api.return_value = {
            "main": {"temp": 22, "humidity": 65, "pressure": 1013},
            "weather": [{"description": "partly cloudy"}],
            "wind": {"speed": 5.2}
        }
        
        with patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'test_key'}):
            input_data = WeatherInput(location="San Francisco, CA", days=3)
            result = weather_lookup(input_data)
            
            assert result["current"]["temperature"] == 22
            assert result["current"]["humidity"] == 65
            mock_api.assert_called()
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_weather_growing_conditions(self, mock_coords):
        """Test weather growing conditions analysis."""
        mock_coords.return_value = (37.7749, -122.4194)
        
        input_data = WeatherInput(location="San Francisco, CA", days=3)
        result = weather_lookup(input_data)
        
        conditions = result["growing_conditions"]
        assert "watering_recommendation" in conditions
        assert "outdoor_suitable" in conditions
        assert "frost_warning" in conditions
        assert "heat_stress_warning" in conditions


class TestMarketplaceSearch:
    """Unit tests for marketplace search tool."""
    
    def test_marketplace_search_snake_plant(self):
        """Test marketplace search for snake plant."""
        input_data = MarketplaceSearchInput(
            plant_name="snake plant",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        assert "plant_name" in result
        assert "products" in result
        assert "total_found" in result
        assert result["plant_name"] == "snake plant"
        assert len(result["products"]) > 0
    
    def test_marketplace_search_monstera(self):
        """Test marketplace search for monstera."""
        input_data = MarketplaceSearchInput(
            plant_name="monstera",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        assert result["total_found"] > 0
        # Should find The Sill in results
        sellers = [p["seller"] for p in result["products"]]
        assert "The Sill" in sellers
    
    def test_marketplace_search_with_price_filter(self):
        """Test marketplace search with price filtering."""
        input_data = MarketplaceSearchInput(
            plant_name="monstera",
            location="nationwide",
            max_price=30.0
        )
        result = marketplace_search(input_data)
        
        # All results should be under $30
        for product in result["products"]:
            assert product["price"] <= 30.0
    
    def test_marketplace_search_unknown_plant(self):
        """Test marketplace search for unknown plant."""
        input_data = MarketplaceSearchInput(
            plant_name="unknown_plant_xyz",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        assert result["total_found"] == 0
        assert len(result["products"]) == 0
    
    def test_marketplace_affiliate_links(self):
        """Test that affiliate links are properly generated."""
        input_data = MarketplaceSearchInput(
            plant_name="snake plant",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        for product in result["products"]:
            assert "affiliate_url" in product
            if "thesill.com" in product["url"]:
                assert "ref=plantworks" in product["affiliate_url"]


class TestNativePlantFinder:
    """Unit tests for native plant finder tool."""
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_native_plant_finder_basic(self, mock_coords):
        """Test basic native plant finder functionality."""
        mock_coords.return_value = (37.7749, -122.4194)
        
        input_data = NativePlantInput(
            location="San Francisco, CA",
            plant_type="all"
        )
        result = native_plant_finder(input_data)
        
        assert "location" in result
        assert "native_plants" in result
        assert "ecological_benefits" in result
        assert "planting_seasons" in result
        assert len(result["native_plants"]) > 0
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_native_plant_finder_trees_only(self, mock_coords):
        """Test native plant finder for trees only."""
        mock_coords.return_value = (37.7749, -122.4194)
        
        input_data = NativePlantInput(
            location="San Francisco, CA",
            plant_type="trees"
        )
        result = native_plant_finder(input_data)
        
        # Should only return trees
        for plant in result["native_plants"]:
            assert plant["type"] == "tree"
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_native_plant_finder_invalid_location(self, mock_coords):
        """Test native plant finder with invalid location."""
        mock_coords.return_value = None
        
        input_data = NativePlantInput(
            location="Invalid Location",
            plant_type="all"
        )
        result = native_plant_finder(input_data)
        
        assert "error" in result


class TestSoilAnalyzer:
    """Unit tests for soil analyzer tool."""
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_soil_analyzer_basic(self, mock_coords):
        """Test basic soil analyzer functionality."""
        mock_coords.return_value = (37.7749, -122.4194)
        
        input_data = SoilAnalysisInput(location="San Francisco, CA")
        result = soil_analyzer(input_data)
        
        assert "location" in result
        assert "soil_type" in result
        assert "ph_level" in result
        assert "nutrients" in result
        assert "recommendations" in result
        assert "amendments" in result
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_soil_analyzer_with_sample_data(self, mock_coords):
        """Test soil analyzer with user-provided sample data."""
        mock_coords.return_value = (37.7749, -122.4194)
        
        sample_data = {
            "ph": 6.5,
            "nitrogen": "high",
            "phosphorus": "low"
        }
        
        input_data = SoilAnalysisInput(
            location="San Francisco, CA",
            soil_sample_data=sample_data
        )
        result = soil_analyzer(input_data)
        
        assert "user_test_results" in result
        assert result["user_test_results"] == sample_data
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_soil_analyzer_ph_recommendations(self, mock_coords):
        """Test soil analyzer pH-based recommendations."""
        mock_coords.return_value = (37.7749, -122.4194)
        
        input_data = SoilAnalysisInput(location="San Francisco, CA")
        result = soil_analyzer(input_data)
        
        ph_level = result["ph_level"]
        recommendations = result["recommendations"]
        
        if ph_level < 6.0:
            assert any("acidic" in rec.lower() for rec in recommendations)
        elif ph_level > 7.5:
            assert any("alkaline" in rec.lower() for rec in recommendations)


class TestHardinessZoneLookup:
    """Unit tests for hardiness zone lookup tool."""
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_hardiness_zone_lookup_basic(self, mock_coords):
        """Test basic hardiness zone lookup."""
        mock_coords.return_value = (37.7749, -122.4194)  # San Francisco
        
        input_data = HardinessZoneInput(location="San Francisco, CA")
        result = hardiness_zone_lookup(input_data)
        
        assert "location" in result
        assert "hardiness_zone" in result
        assert "temperature_range" in result
        assert "frost_dates" in result
        assert "growing_season" in result
        assert "climate_description" in result
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_hardiness_zone_northern_location(self, mock_coords):
        """Test hardiness zone for northern location."""
        mock_coords.return_value = (47.6062, -122.3321)  # Seattle
        
        input_data = HardinessZoneInput(location="Seattle, WA")
        result = hardiness_zone_lookup(input_data)
        
        # Seattle should be in a colder zone
        zone = result["hardiness_zone"]
        assert any(char in zone for char in ["3", "4", "5", "6"])
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_hardiness_zone_southern_location(self, mock_coords):
        """Test hardiness zone for southern location."""
        mock_coords.return_value = (25.7617, -80.1918)  # Miami
        
        input_data = HardinessZoneInput(location="Miami, FL")
        result = hardiness_zone_lookup(input_data)
        
        # Miami should be in a warmer zone
        zone = result["hardiness_zone"]
        assert any(char in zone for char in ["9", "10", "11", "12"])
    
    @patch('app.plantworks_tools.get_coordinates')
    def test_hardiness_zone_invalid_location(self, mock_coords):
        """Test hardiness zone lookup with invalid location."""
        mock_coords.return_value = None
        
        input_data = HardinessZoneInput(location="Invalid Location")
        result = hardiness_zone_lookup(input_data)
        
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

