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
import httpx
from unittest.mock import patch
from tests.adk_simulation import run_server, InvocationContext, SessionState
from app.agent import plantworks_main_agent
from tests.conftest import TestConfig


class TestAgentIntegration:
    """Integration tests for agent interactions and workflows."""
    
    @pytest.mark.asyncio
    async def test_plant_identification_workflow(self, mock_invocation_context):
        """Test complete plant identification workflow."""
        # Test query that should trigger The Botanist
        mock_invocation_context.session.state["user_query"] = "What is Monstera deliciosa and how do I identify it?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert len(response) > 100  # Should be detailed response
        # Should contain botanical information
        assert any(keyword in response.lower() for keyword in ["plant", "botanical", "identify", "species"])
    
    @pytest.mark.asyncio
    async def test_plant_care_workflow(self, mock_invocation_context):
        """Test complete plant care workflow."""
        # Test query that should trigger The Gardener
        mock_invocation_context.session.state["user_query"] = "How do I care for a snake plant in my apartment?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert len(response) > 100
        # Should contain care information
        assert any(keyword in response.lower() for keyword in ["care", "water", "light", "gardener"])
    
    @pytest.mark.asyncio
    async def test_marketplace_workflow(self, mock_invocation_context):
        """Test complete marketplace workflow."""
        # Test query that should trigger The Merchant
        mock_invocation_context.session.state["user_query"] = "Where can I buy a fiddle leaf fig for under $50?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert len(response) > 100
        # Should contain marketplace information
        assert any(keyword in response.lower() for keyword in ["buy", "price", "seller", "merchant"])
    
    @pytest.mark.asyncio
    async def test_native_plants_workflow(self, mock_invocation_context):
        """Test complete native plants workflow."""
        # Test query that should trigger The Ecologist
        mock_invocation_context.session.state["user_query"] = "What native plants should I grow in California?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert len(response) > 100
        # Should contain native plant information
        assert any(keyword in response.lower() for keyword in ["native", "local", "ecologist", "environment"])
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, mock_invocation_context):
        """Test coordination between multiple agents."""
        # Complex query that might involve multiple agents
        mock_invocation_context.session.state["user_query"] = "I want to buy a Monstera deliciosa, how do I care for it, and are there native alternatives in Texas?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert len(response) > 200  # Should be comprehensive response
        # Should address multiple aspects
        response_lower = response.lower()
        assert "plant" in response_lower
        # Should provide helpful information even if not perfectly coordinated


class TestServerIntegration:
    """Integration tests for the ADK server."""
    
    @pytest.mark.asyncio
    async def test_server_startup_and_health(self):
        """Test server can start up and respond to health checks."""
        # This test would require actually starting the server
        # For now, we'll test the server components
        
        # Test that the main agent is properly configured
        assert plantworks_main_agent is not None
        assert plantworks_main_agent.name == "plantworks_main_agent"
        assert len(plantworks_main_agent.sub_agents) == 4
        assert len(plantworks_main_agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_agent_response_format(self, mock_invocation_context):
        """Test that agent responses follow expected format."""
        mock_invocation_context.session.state["user_query"] = "Test query"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        
        event_received = False
        async for event in response_generator:
            if event.get("type") == "agent_response":
                event_received = True
                assert "content" in event
                assert "agent" in event
                assert "model" in event
                assert isinstance(event["content"], str)
                assert len(event["content"]) > 0
                break
        
        assert event_received, "No agent response event received"


class TestToolIntegration:
    """Integration tests for tool usage within agents."""
    
    @pytest.mark.asyncio
    async def test_plant_search_tool_integration(self, mock_external_apis):
        """Test plant search tool integration with agents."""
        from app.plantworks_tools import plant_database_search, PlantSearchInput
        
        # Test tool directly
        input_data = PlantSearchInput(query="monstera", limit=3)
        result = plant_database_search(input_data)
        
        assert "results" in result
        assert "total_found" in result
        assert result["total_found"] >= 0
        assert isinstance(result["results"], list)
    
    @pytest.mark.asyncio
    async def test_weather_tool_integration(self, mock_external_apis):
        """Test weather tool integration with agents."""
        from app.plantworks_tools import weather_lookup, WeatherInput
        
        # Test tool directly
        input_data = WeatherInput(location="San Francisco, CA", days=3)
        result = weather_lookup(input_data)
        
        assert "location" in result
        assert "current" in result
        assert "forecast" in result
        assert "growing_conditions" in result
    
    @pytest.mark.asyncio
    async def test_marketplace_tool_integration(self):
        """Test marketplace tool integration with agents."""
        from app.plantworks_tools import marketplace_search, MarketplaceSearchInput
        
        # Test tool directly
        input_data = MarketplaceSearchInput(
            plant_name="snake plant",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        assert "products" in result
        assert "total_found" in result
        assert isinstance(result["products"], list)
        
        # Check affiliate links are generated
        for product in result["products"]:
            assert "affiliate_url" in product


class TestErrorHandling:
    """Integration tests for error handling across the system."""
    
    @pytest.mark.asyncio
    async def test_invalid_location_handling(self, mock_invocation_context):
        """Test handling of invalid location queries."""
        mock_invocation_context.session.state["user_query"] = "What's the weather in InvalidLocationXYZ123?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should handle gracefully, not crash
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self, mock_invocation_context):
        """Test handling of empty queries."""
        mock_invocation_context.session.state["user_query"] = ""
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should provide helpful response even for empty query
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_unknown_plant_handling(self, mock_invocation_context):
        """Test handling of unknown plant queries."""
        mock_invocation_context.session.state["user_query"] = "Tell me about the XYZ123 plant that doesn't exist"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should handle gracefully
        assert len(response) > 0


class TestBusinessLogic:
    """Integration tests for business logic and revenue features."""
    
    @pytest.mark.asyncio
    async def test_affiliate_link_generation(self):
        """Test that affiliate links are properly generated for revenue."""
        from app.plantworks_tools import marketplace_search, MarketplaceSearchInput
        
        input_data = MarketplaceSearchInput(
            plant_name="snake plant",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        # Check that affiliate links are generated
        for product in result["products"]:
            assert "affiliate_url" in product
            
            # Check specific affiliate parameters
            if "thesill.com" in product["url"]:
                assert "ref=plantworks" in product["affiliate_url"]
                assert "utm_source=plantworks" in product["affiliate_url"]
            elif "planterina.com" in product["url"]:
                assert "ref=plantworks" in product["affiliate_url"]
    
    @pytest.mark.asyncio
    async def test_price_filtering(self):
        """Test price filtering functionality."""
        from app.plantworks_tools import marketplace_search, MarketplaceSearchInput
        
        input_data = MarketplaceSearchInput(
            plant_name="monstera",
            location="nationwide",
            max_price=30.0
        )
        result = marketplace_search(input_data)
        
        # All results should be under the price limit
        for product in result["products"]:
            assert product["price"] <= 30.0
    
    @pytest.mark.asyncio
    async def test_seller_information_completeness(self):
        """Test that seller information is complete for business decisions."""
        from app.plantworks_tools import marketplace_search, MarketplaceSearchInput
        
        input_data = MarketplaceSearchInput(
            plant_name="snake plant",
            location="nationwide"
        )
        result = marketplace_search(input_data)
        
        # Check that all required business information is present
        for product in result["products"]:
            assert "seller" in product
            assert "price" in product
            assert "rating" in product
            assert "reviews" in product
            assert "availability" in product
            assert "url" in product
            assert "affiliate_url" in product


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
