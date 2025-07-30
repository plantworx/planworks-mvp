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
from unittest.mock import patch, Mock
from app.plantworks_agents import (
    learn_agent, grow_agent, local_environment_agent, marketplace_agent,
    plantworks_main_agent
)
from tests.adk_simulation import InvocationContext, SessionState


class TestLearnAgent:
    """Unit tests for The Botanist (learn_agent)."""
    
    @pytest.mark.asyncio
    async def test_learn_agent_initialization(self):
        """Test learn agent is properly initialized."""
        assert learn_agent.name == "learn_agent"
        assert learn_agent.description.startswith("The Botanist")
        assert len(learn_agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_learn_agent_plant_identification(self, mock_invocation_context):
        """Test learn agent handles plant identification queries."""
        mock_invocation_context.session.state["user_query"] = "What is Monstera deliciosa?"
        
        response_generator = learn_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "botanist" in response.lower() or "plant" in response.lower()
    
    @pytest.mark.asyncio
    async def test_learn_agent_botanical_query(self, mock_invocation_context):
        """Test learn agent handles botanical knowledge queries."""
        mock_invocation_context.session.state["user_query"] = "Tell me about the Araceae family"
        
        response_generator = learn_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert len(response) > 50  # Should provide detailed response


class TestGrowAgent:
    """Unit tests for The Gardener (grow_agent)."""
    
    @pytest.mark.asyncio
    async def test_grow_agent_initialization(self):
        """Test grow agent is properly initialized."""
        assert grow_agent.name == "grow_agent"
        assert grow_agent.description.startswith("The Gardener")
        assert len(grow_agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_grow_agent_care_advice(self, mock_invocation_context):
        """Test grow agent handles plant care queries."""
        mock_invocation_context.session.state["user_query"] = "How do I care for a snake plant?"
        
        response_generator = grow_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "care" in response.lower() or "gardener" in response.lower()
        assert "water" in response.lower() or "light" in response.lower()
    
    @pytest.mark.asyncio
    async def test_grow_agent_watering_query(self, mock_invocation_context):
        """Test grow agent handles watering-specific queries."""
        mock_invocation_context.session.state["user_query"] = "How often should I water my monstera?"
        
        response_generator = grow_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "water" in response.lower()


class TestLocalEnvironmentAgent:
    """Unit tests for The Ecologist (local_environment_agent)."""
    
    @pytest.mark.asyncio
    async def test_local_environment_agent_initialization(self):
        """Test local environment agent is properly initialized."""
        assert local_environment_agent.name == "local_environment_agent"
        assert local_environment_agent.description.startswith("The Ecologist")
        assert len(local_environment_agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_local_environment_agent_native_plants(self, mock_invocation_context):
        """Test local environment agent handles native plant queries."""
        mock_invocation_context.session.state["user_query"] = "What native plants grow in California?"
        
        response_generator = local_environment_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "native" in response.lower() or "ecologist" in response.lower()
        assert "local" in response.lower() or "environment" in response.lower()
    
    @pytest.mark.asyncio
    async def test_local_environment_agent_climate_query(self, mock_invocation_context):
        """Test local environment agent handles climate queries."""
        mock_invocation_context.session.state["user_query"] = "What's the hardiness zone for Seattle?"
        
        response_generator = local_environment_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "zone" in response.lower() or "climate" in response.lower()


class TestMarketplaceAgent:
    """Unit tests for The Merchant (marketplace_agent)."""
    
    @pytest.mark.asyncio
    async def test_marketplace_agent_initialization(self):
        """Test marketplace agent is properly initialized."""
        assert marketplace_agent.name == "marketplace_agent"
        assert marketplace_agent.description.startswith("The Merchant")
        assert len(marketplace_agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_marketplace_agent_shopping_query(self, mock_invocation_context):
        """Test marketplace agent handles shopping queries."""
        mock_invocation_context.session.state["user_query"] = "Where can I buy a fiddle leaf fig?"
        
        response_generator = marketplace_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "buy" in response.lower() or "merchant" in response.lower() or "shop" in response.lower()
    
    @pytest.mark.asyncio
    async def test_marketplace_agent_price_query(self, mock_invocation_context):
        """Test marketplace agent handles price comparison queries."""
        mock_invocation_context.session.state["user_query"] = "Compare prices for snake plants"
        
        response_generator = marketplace_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "price" in response.lower() or "seller" in response.lower()


class TestMainAgent:
    """Unit tests for the main Plantworks agent."""
    
    @pytest.mark.asyncio
    async def test_main_agent_initialization(self):
        """Test main agent is properly initialized."""
        assert plantworks_main_agent.name == "plantworks_main_agent"
        assert len(plantworks_main_agent.sub_agents) == 4
        assert len(plantworks_main_agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_main_agent_sub_agents(self):
        """Test main agent has all required sub-agents."""
        sub_agent_names = [agent.name for agent in plantworks_main_agent.sub_agents]
        
        assert "learn_agent" in sub_agent_names
        assert "grow_agent" in sub_agent_names
        assert "local_environment_agent" in sub_agent_names
        assert "marketplace_agent" in sub_agent_names
    
    @pytest.mark.asyncio
    async def test_main_agent_general_query(self, mock_invocation_context):
        """Test main agent handles general plant queries."""
        mock_invocation_context.session.state["user_query"] = "I need help with plants"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        assert "plantworks" in response.lower() or "plant" in response.lower()
    
    @pytest.mark.asyncio
    async def test_main_agent_identification_routing(self, mock_invocation_context):
        """Test main agent routes identification queries correctly."""
        mock_invocation_context.session.state["user_query"] = "Identify this plant for me"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should route to botanist
        assert "botanist" in response.lower() or "identify" in response.lower()
    
    @pytest.mark.asyncio
    async def test_main_agent_care_routing(self, mock_invocation_context):
        """Test main agent routes care queries correctly."""
        mock_invocation_context.session.state["user_query"] = "How do I care for my plants?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should route to gardener
        assert "gardener" in response.lower() or "care" in response.lower()
    
    @pytest.mark.asyncio
    async def test_main_agent_shopping_routing(self, mock_invocation_context):
        """Test main agent routes shopping queries correctly."""
        mock_invocation_context.session.state["user_query"] = "Where can I buy plants?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should route to merchant
        assert "merchant" in response.lower() or "buy" in response.lower() or "shop" in response.lower()
    
    @pytest.mark.asyncio
    async def test_main_agent_native_plant_routing(self, mock_invocation_context):
        """Test main agent routes native plant queries correctly."""
        mock_invocation_context.session.state["user_query"] = "What native plants should I grow?"
        
        response_generator = plantworks_main_agent._run_async_impl(mock_invocation_context)
        response = None
        async for event in response_generator:
            if event.get("type") == "agent_response":
                response = event.get("content")
                break
        
        assert response is not None
        # Should route to ecologist
        assert "ecologist" in response.lower() or "native" in response.lower()


class TestAgentConfiguration:
    """Test agent configuration and setup."""
    
    def test_all_agents_have_required_attributes(self):
        """Test all agents have required attributes."""
        agents = [learn_agent, grow_agent, local_environment_agent, marketplace_agent, plantworks_main_agent]
        
        for agent in agents:
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'description')
            assert hasattr(agent, 'instruction')
            assert hasattr(agent, 'model')
            assert hasattr(agent, 'tools')
            
            assert agent.name is not None
            assert agent.description is not None
            assert agent.instruction is not None
            assert agent.model is not None
            assert isinstance(agent.tools, list)
    
    def test_agent_models_configured(self):
        """Test all agents have proper model configuration."""
        agents = [learn_agent, grow_agent, local_environment_agent, marketplace_agent, plantworks_main_agent]
        
        for agent in agents:
            assert agent.model == "gemini-2.0-flash-exp"
    
    def test_agent_tools_not_empty(self):
        """Test all agents have tools configured."""
        agents = [learn_agent, grow_agent, local_environment_agent, marketplace_agent]
        
        for agent in agents:
            assert len(agent.tools) > 0
    
    def test_main_agent_has_sub_agents(self):
        """Test main agent has all sub-agents configured."""
        assert len(plantworks_main_agent.sub_agents) == 4
        
        sub_agent_names = [agent.name for agent in plantworks_main_agent.sub_agents]
        expected_names = ["learn_agent", "grow_agent", "local_environment_agent", "marketplace_agent"]
        
        for expected_name in expected_names:
            assert expected_name in sub_agent_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
