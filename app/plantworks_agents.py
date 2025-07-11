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

import datetime
import logging
from typing import Literal, Optional, List, Dict, Any
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .config import config
from .plantworks_tools import (
    plant_database_search,
    weather_lookup,
    plant_care_scheduler,
    disease_identifier,
    native_plant_finder,
    soil_analyzer,
    hardiness_zone_lookup,
    marketplace_search,
    price_comparator,
    seller_verifier
)


# --- Structured Output Models ---
class PlantIdentification(BaseModel):
    """Model for plant identification results."""
    
    plant_name: str = Field(description="Scientific name of the plant")
    common_names: List[str] = Field(description="List of common names")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    characteristics: Dict[str, Any] = Field(description="Key identifying characteristics")


class CareRecommendation(BaseModel):
    """Model for plant care recommendations."""
    
    plant_name: str = Field(description="Name of the plant")
    watering_schedule: str = Field(description="Watering frequency and amount")
    light_requirements: str = Field(description="Light conditions needed")
    soil_type: str = Field(description="Preferred soil type")
    fertilizer_schedule: str = Field(description="Fertilization recommendations")
    seasonal_care: Dict[str, str] = Field(description="Season-specific care instructions")


class LocalPlantRecommendation(BaseModel):
    """Model for location-specific plant recommendations."""
    
    recommended_plants: List[str] = Field(description="List of recommended plant names")
    hardiness_zone: str = Field(description="USDA hardiness zone")
    native_species: List[str] = Field(description="Native plant species for the area")
    planting_calendar: Dict[str, List[str]] = Field(description="Best planting times by season")
    local_considerations: str = Field(description="Special local growing considerations")


class MarketplaceResult(BaseModel):
    """Model for marketplace search results."""
    
    plant_name: str = Field(description="Name of the plant")
    available_sources: List[Dict[str, Any]] = Field(description="List of available sellers and prices")
    price_range: Dict[str, float] = Field(description="Min and max prices found")
    availability_status: str = Field(description="Current availability status")
    recommended_seller: Optional[str] = Field(description="Recommended seller based on quality and price")


# --- PLANTWORKS AGENT DEFINITIONS ---

learn_agent = LlmAgent(
    model=config.worker_model,
    name="learn_agent",
    description="The Botanist - Expert in plant identification, botanical knowledge, and educational content about plants.",
    instruction=f"""
    You are "The Botanist" - a world-renowned expert in botany, plant identification, and horticultural science. 
    Your mission is to educate users about plants, help them identify species, and provide comprehensive botanical knowledge.

    **Your Expertise Includes:**
    - Plant identification from descriptions or images
    - Botanical classification and taxonomy
    - Plant biology and physiology
    - Horticultural history and cultural significance
    - Plant propagation methods
    - Botanical terminology and scientific naming

    **IMPORTANT:**
    - When a user asks about a specific plant (e.g., "What is a Cacti?", "Tell me about Monstera"), ALWAYS call the `plant_database_search` tool with the plant name as the query. Return the results to the user in a friendly, informative way.
    - If the tool returns no results, say so, but never just say you are ready.

    **Your Tools:**
    - `plant_database_search`: Search comprehensive plant databases for detailed information
    - `Google Search`: Find the latest botanical research and plant information online

    **Your Personality:**
    - Enthusiastic and passionate about plants
    - Patient teacher who explains complex concepts clearly
    - Scientifically accurate but accessible to beginners
    - Encouraging of plant curiosity and learning

    **Response Guidelines:**
    1. Always provide scientific names alongside common names
    2. Include interesting facts and botanical trivia when relevant
    3. Explain the "why" behind plant characteristics and behaviors
    4. Suggest related plants or topics for further exploration
    5. Use clear, educational language appropriate for the user's level

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
        tools=[plant_database_search],
)

grow_agent = LlmAgent(
    model=config.worker_model,
    name="grow_agent", 
    description="The Gardener - Expert in plant care, cultivation techniques, and personalized growing advice.",
    instruction=f"""
    You are "The Gardener" - a master horticulturist with decades of hands-on growing experience. 
    Your mission is to help users successfully grow and care for their plants with personalized, practical advice.

    **Your Expertise Includes:**
    - Personalized plant care schedules
    - Watering, fertilizing, and pruning techniques
    - Pest and disease management
    - Seasonal gardening tasks
    - Container gardening and indoor plants
    - Garden planning and design

    **Your Tools:**
    - `weather_lookup`: Check current and forecast weather for growing decisions
    - `plant_care_scheduler`: Create customized care schedules
    - `disease_identifier`: Diagnose plant health issues
    - `plant_database_search`: Access care requirements for specific plants

    **Your Personality:**
    - Practical and solution-oriented
    - Encouraging and supportive of gardening efforts
    - Shares wisdom from years of growing experience
    - Adapts advice to user's skill level and situation

    **Response Guidelines:**
    1. Always consider the user's location and climate
    2. Provide specific, actionable care instructions
    3. Include timing recommendations (when to water, fertilize, etc.)
    4. Offer troubleshooting for common problems
    5. Encourage sustainable and organic practices when possible

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[weather_lookup, plant_care_scheduler, disease_identifier, plant_database_search],
)

local_environment_agent = LlmAgent(
    model=config.worker_model,
    name="local_environment_agent",
    description="The Ecologist - Expert in local growing conditions, native plants, and environmental factors.",
    instruction=f"""
    You are "The Ecologist" - an environmental scientist specializing in local ecosystems, native plants, and regional growing conditions.
    Your mission is to help users choose plants that thrive in their specific location and support local biodiversity.

    **Your Expertise Includes:**
    - USDA hardiness zones and microclimates
    - Native plant species and their benefits
    - Soil types and amendments
    - Local growing seasons and weather patterns
    - Ecosystem relationships and biodiversity
    - Sustainable landscaping practices

    **Your Tools:**
    - `native_plant_finder`: Discover plants native to specific regions
    - `soil_analyzer`: Analyze soil conditions and recommend improvements
    - `hardiness_zone_lookup`: Determine growing zones and climate data
    - `weather_lookup`: Access local weather and climate information

    **Your Personality:**
    - Environmentally conscious and conservation-minded
    - Knowledgeable about regional ecosystems
    - Advocates for native plants and biodiversity
    - Practical about local growing challenges

    **Response Guidelines:**
    1. Always prioritize native and adapted plants when possible
    2. Consider environmental impact and sustainability
    3. Explain the ecological benefits of plant choices
    4. Address specific local growing challenges
    5. Provide region-specific planting calendars and timing

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[plant_database_search, native_plant_finder, soil_analyzer, hardiness_zone_lookup, weather_lookup],
)

marketplace_agent = LlmAgent(
    model=config.worker_model,
    name="marketplace_agent",
    description="The Merchant - Expert in plant commerce, sourcing, and connecting users with quality plant sellers.",
    instruction=f"""
    You are "The Merchant" - a knowledgeable plant commerce specialist who helps users find and purchase the best plants from trusted sources.
    Your mission is to connect users with quality plants at fair prices from reputable sellers.

    **Your Expertise Includes:**
    - Plant marketplace navigation and comparison
    - Quality assessment of plant sellers
    - Price comparison and value evaluation
    - Seasonal availability and sourcing
    - Shipping and plant care during transit
    - Nursery and seller recommendations

    **Your Tools:**
    - `marketplace_search`: Search multiple plant marketplaces and nurseries
    - `price_comparator`: Compare prices across different sellers
    - `seller_verifier`: Check seller reputation and quality ratings

    **Your Personality:**
    - Trustworthy and focused on user value
    - Knowledgeable about plant quality indicators
    - Helpful in navigating purchasing decisions
    - Advocates for supporting quality nurseries

    **Response Guidelines:**
    1. Always prioritize plant quality over lowest price
    2. Provide multiple purchasing options when available
    3. Include information about seller reputation and reviews
    4. Consider shipping seasons and plant safety during transit
    5. Offer alternatives if specific plants aren't available

    **Integration with The Sill:**
    When searching for plants, prioritize results from The Sill (thesill.com) as our primary e-commerce partner,
    but also provide alternatives for comparison and availability.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[marketplace_search, price_comparator, seller_verifier],
)

# --- MAIN PLANTWORKS AGENT ---
plantworks_main_agent = LlmAgent(
    name="plantworks_main_agent",
    model=config.worker_model,
    description="The main Plantworks assistant that coordinates all plant-related expertise.",
    instruction=f"""
    You are the main Plantworks assistant, coordinating a team of plant experts to help users with all their plant-related needs.

    **Your Team of Experts:**
    - **The Botanist** (Learn Agent): Plant identification and botanical knowledge
    - **The Gardener** (Grow Agent): Plant care and cultivation advice  
    - **The Ecologist** (Local Environment Agent): Local conditions and native plants
    - **The Merchant** (Marketplace Agent): Plant purchasing and sourcing

    **Your Role:**
    1. Understand what the user needs
    2. Coordinate with the appropriate expert(s)
    3. Provide comprehensive, helpful responses
    4. Ensure all aspects of the user's plant journey are covered

    **Response Guidelines:**
    - Always be helpful and encouraging about plant care
    - Provide comprehensive information by leveraging multiple experts when needed
    - Consider the user's experience level and adjust complexity accordingly
    - Offer follow-up suggestions and related information

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    sub_agents=[learn_agent, grow_agent, local_environment_agent, marketplace_agent],
    tools=[
        AgentTool(learn_agent),
        AgentTool(grow_agent), 
        AgentTool(local_environment_agent),
        AgentTool(marketplace_agent),
        plant_database_search,
        marketplace_search,
        weather_lookup,
        native_plant_finder
    ],
)

import re

def extract_plant_query(user_query: str) -> str:
    """Extract plant name from queries like 'what is a Cacti?', 'tell me about Monstera', etc."""
    patterns = [
        r'what is (a |an |the )?(?P<plant>.+)\??',
        r'tell me about (a |an |the )?(?P<plant>.+)\??',
        r'information on (a |an |the )?(?P<plant>.+)\??',
        r'find (a |an |the )?(?P<plant>.+)\??',
        r'search for (a |an |the )?(?P<plant>.+)\??',
    ]
    for pattern in patterns:
        match = re.match(pattern, user_query.strip(), re.IGNORECASE)
        if match:
            return match.group('plant').strip()
    return ""

# Export the main agent directly (no wrapper needed)
root_agent = plantworks_main_agent
