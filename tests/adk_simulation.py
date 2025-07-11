# ADK Simulation Layer
# This simulates the Google ADK structure until the official package is available

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from abc import ABC, abstractmethod
from pydantic import BaseModel
import inspect

logger = logging.getLogger(__name__)

# Simulate google.adk.tools.Tool decorator
def Tool(func: Callable) -> Callable:
    """Decorator to mark functions as ADK tools."""
    func._is_adk_tool = True
    return func

# Simulate google.adk.agents.BaseAgent
class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = []
    
    @abstractmethod
    async def _run_async_impl(self, ctx: 'InvocationContext') -> AsyncGenerator[Dict[str, Any], None]:
        """Implementation of agent execution."""
        pass

# Simulate google.adk.agents.LlmAgent
class LlmAgent(BaseAgent):
    """LLM-based agent implementation."""
    
    def __init__(
        self,
        name: str,
        model: str,
        description: str,
        instruction: str,
        tools: List[Callable] = None,
        sub_agents: List[BaseAgent] = None,
        output_schema: BaseModel = None
    ):
        super().__init__(name)
        self.model = model
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        self.output_schema = output_schema
        
        logger.info(f"Created LlmAgent: {name} with {len(self.tools)} tools")
    
    async def _run_async_impl(self, ctx: 'InvocationContext') -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the agent with the given context."""
        user_message = ctx.session.state.get("user_query", "")
        
        logger.info(f"[{self.name}] Processing: {user_message[:100]}...")
        
        # Simulate agent processing
        response = await self._process_message(user_message)
        
        yield {
            "type": "agent_response",
            "agent": self.name,
            "content": response,
            "model": self.model
        }
    
    async def _process_message(self, message: str) -> str:
        """Process a message using available tools and expert knowledge."""
        message_lower = message.lower()
        
        # Route to appropriate handlers based on agent type and message content
        if self.name == "learn_agent" or "botanist" in self.description.lower():
            return await self._handle_plant_identification(message)
        elif self.name == "grow_agent" or "gardener" in self.description.lower():
            return await self._handle_plant_care(message)
        elif self.name == "local_environment_agent" or "ecologist" in self.description.lower():
            return await self._handle_local_environment(message)
        elif self.name == "marketplace_agent" or "merchant" in self.description.lower():
            return await self._handle_marketplace(message)
        else:
            # Main agent - route to appropriate sub-agent
            return await self._route_to_specialist(message)
    
    async def _route_to_specialist(self, message: str) -> str:
        """Route queries to the appropriate specialist agent."""
        message_lower = message.lower()
        
        # Prioritize care queries over identification
        if any(keyword in message_lower for keyword in ["care", "water", "fertilize", "grow", "how do i", "how to", "yellowing", "brown", "dying", "watering", "light", "humidity"]):
            return await self._handle_plant_care(message)
        elif any(keyword in message_lower for keyword in ["buy", "purchase", "price", "seller", "where can i", "shop", "store", "find", "cost"]):
            return await self._handle_marketplace(message)
        elif any(keyword in message_lower for keyword in ["native", "local", "zone", "climate", "hardiness", "soil"]):
            return await self._handle_local_environment(message)
        elif any(keyword in message_lower for keyword in ["identify", "what is", "species", "botanical", "tell me about"]):
            return await self._handle_plant_identification(message)
        else:
            return await self._handle_general_query(message)
    
    async def _handle_plant_identification(self, message: str) -> str:
        """Handle plant identification queries with expert knowledge."""
        message_lower = message.lower()
        
        # Check for specific plants mentioned and provide expert knowledge
        if "monstera deliciosa" in message_lower or "monstera" in message_lower:
            return """🌿 **Monstera deliciosa - The Swiss Cheese Plant**

As The Botanist, I'm excited to share my expertise about this magnificent plant!

**Scientific Classification:**
• **Scientific Name:** *Monstera deliciosa*
• **Family:** Araceae (Aroid family)
• **Common Names:** Swiss Cheese Plant, Split-leaf Philodendron, Ceriman
• **Origin:** Tropical rainforests of southern Mexico and Panama

**Identification Features:**
• **Leaves:** Large, heart-shaped when young, developing characteristic splits (fenestrations) as they mature
• **Size:** Can reach 10+ feet indoors, 70+ feet in nature
• **Growth Pattern:** Climbing vine with aerial roots
• **Fenestrations:** The iconic "holes" develop after the plant matures (usually 2-3 years)

**Why the Holes?** The fenestrations likely evolved to:
- Reduce wind resistance in storms
- Allow light to reach lower leaves
- Prevent the large leaves from tearing

**Botanical Facts:**
• The fruit is edible when fully ripe (hence "deliciosa")
• It's a hemiepiphyte - starts on ground, climbs trees
• Produces calcium oxalate crystals (toxic if eaten raw)
• Can live 40+ years with proper care

**Care Summary:**
• **Light:** Bright, indirect light
• **Water:** When top inch of soil is dry
• **Humidity:** 40-60% preferred
• **Support:** Provide a moss pole for climbing

This is one of my favorite plants - it's both stunning and relatively easy to care for! Would you like specific care advice or help finding one to purchase?"""

        elif "snake plant" in message_lower or "sansevieria" in message_lower:
            return """🌿 **Sansevieria trifasciata - The Snake Plant**

As The Botanist, let me tell you about this remarkable succulent!

**Scientific Classification:**
• **Scientific Name:** *Sansevieria trifasciata* (recently reclassified to *Dracaena trifasciata*)
• **Family:** Asparagaceae (formerly Agavaceae)
• **Common Names:** Snake Plant, Mother-in-Law's Tongue, Viper's Bowstring Hemp
• **Origin:** West Africa (Nigeria to Congo)

**Identification Features:**
• **Leaves:** Thick, sword-like, upright growth
• **Pattern:** Dark green with lighter green horizontal stripes
• **Edges:** Yellow margins on many varieties
• **Height:** 1-4 feet typically, can reach 6+ feet
• **Texture:** Thick, succulent-like, waxy surface

**Botanical Adaptations:**
• CAM photosynthesis - opens stomata at night to conserve water
• Rhizomatous root system for water storage
• Extremely drought tolerant
• Natural air purifier (NASA Clean Air Study)

**Varieties:**
• **'Laurentii':** Classic yellow-edged variety
• **'Moonshine':** Silvery-green leaves
• **'Cylindrica':** Cylindrical leaves
• **'Hahnii':** Dwarf bird's nest variety

**Survival Adaptations:**
• Can survive months without water
• Tolerates low light conditions
• Resistant to most pests
• Propagates easily from leaf cuttings

**Fun Facts:**
• Used historically for bowstring fiber
• Considered lucky in feng shui
• One of the most tolerant houseplants
• Can bloom with small, fragrant white flowers

This plant is perfect for beginners - nearly indestructible! Need care tips or shopping advice?"""

        elif "fiddle leaf fig" in message_lower or "ficus lyrata" in message_lower:
            return """🌿 **Ficus lyrata - The Fiddle Leaf Fig**

As The Botanist, I'm delighted to share the fascinating details of this Instagram-famous plant!

**Scientific Classification:**
• **Scientific Name:** *Ficus lyrata*
• **Family:** Moraceae (Fig family)
• **Common Names:** Fiddle Leaf Fig, Banjo Fig
• **Origin:** Western Africa (Cameroon to Sierra Leone)

**Identification Features:**
• **Leaves:** Large, violin-shaped (hence "fiddle"), leathery texture
• **Size:** 6-10 feet indoors, 50+ feet in nature
• **Veining:** Prominent light green veins on dark green leaves
• **Growth:** Single trunk or branching tree form
• **Bark:** Smooth, light gray

**Botanical Characteristics:**
• **Leaf Size:** Can reach 18 inches long, 12 inches wide
• **Sap:** Milky latex (can cause skin irritation)
• **Root System:** Extensive, can become root-bound quickly
• **Natural Habitat:** Understory of tropical rainforests

**Why So Popular?**
• Architectural, statement-making appearance
• Large, dramatic foliage
• Tree-like structure perfect for modern interiors
• Photogenic for social media

**Growth Patterns:**
• **Young plants:** Bushy with smaller leaves
• **Mature plants:** Tree-like with larger, more defined leaves
• **Branching:** Can be encouraged through pruning
• **Growth rate:** Moderate to fast in ideal conditions

**Botanical Challenges:**
• Sensitive to environmental changes
• Prone to leaf drop when stressed
• Requires consistent care routine
• Native to stable tropical conditions

**Care Requirements:**
• **Light:** Bright, indirect light (6+ hours)
• **Water:** Consistent moisture, not soggy
• **Humidity:** 40-50% minimum
• **Temperature:** 65-75°F consistently

This beauty requires more attention than most houseplants, but the dramatic results are worth it! Would you like detailed care instructions or help finding a healthy specimen?"""

        # Use plant_database_search tool for other plants
        for tool in self.tools:
            if hasattr(tool, '__name__') and 'plant_database_search' in tool.__name__:
                try:
                    from .plantworks_tools import PlantSearchInput
                    # Extract plant name from message
                    plant_query = message.replace("what is", "").replace("identify", "").replace("tell me about", "").strip()
                    result = tool(PlantSearchInput(query=plant_query, limit=1))
                    if result.get("results"):
                        plant = result["results"][0]
                        return f"""🌿 **{plant.get('common_name', 'Unknown Plant')}**

As The Botanist, here's what I know about this plant:

**Scientific Name:** *{plant.get('scientific_name', 'Unknown')}*
**Family:** {plant.get('family', 'Unknown')}
**Care Level:** {plant.get('care_level', 'Unknown')}

**Light Requirements:** {plant.get('light_requirements', 'Unknown')}
**Watering:** {plant.get('water_frequency', 'Unknown')}

**Description:** {plant.get('description', 'No description available')}

**Botanical Notes:**
This plant belongs to the {plant.get('family', 'Unknown')} family, which includes many fascinating species with unique adaptations. The care level is rated as {plant.get('care_level', 'unknown')}, making it {'suitable for beginners' if plant.get('care_level') == 'Easy' else 'requiring some experience' if plant.get('care_level') == 'Intermediate' else 'best for experienced gardeners'}.

Would you like more detailed care instructions, or are you interested in finding where to purchase this plant?

*Source: {plant.get('source', 'Plant Database')}*"""
                except Exception as e:
                    logger.error(f"Tool execution error: {e}")
        
        # Fallback for unknown plants
        return """🌿 **Plant Identification Assistance**

As The Botanist, I'd love to help identify your plant! However, I need a bit more specific information to provide accurate identification.

**For better identification, please tell me:**
• **Plant name** if you know it (common or scientific)
• **Leaf shape and size** (round, pointed, heart-shaped, etc.)
• **Growth pattern** (upright, trailing, bushy, tree-like)
• **Special features** (variegation, flowers, unique characteristics)
• **Where you saw it** (houseplant, garden, wild)

**Popular Plants I Can Help With:**
• Monstera deliciosa (Swiss Cheese Plant)
• Sansevieria (Snake Plant)
• Ficus lyrata (Fiddle Leaf Fig)
• Pothos varieties
• Philodendron species
• And hundreds more!

**Or try asking:**
• "What is Monstera deliciosa?"
• "Tell me about snake plants"
• "Identify Ficus lyrata"

I'm here to share my botanical expertise - just give me a plant name or better description!"""
    
    async def _handle_plant_care(self, message: str) -> str:
        """Handle plant care queries."""
        message_lower = message.lower()
        
        # Check for specific plants mentioned
        if "monstera" in message_lower:
            return """🌱 **Monstera deliciosa Care Guide**

As The Gardener, here's my expert care advice for your Monstera:

**💧 Watering:**
• Water when top 1-2 inches of soil are dry
• Typically every 1-2 weeks
• Use filtered or distilled water if possible
• Ensure drainage holes to prevent root rot

**☀️ Light Requirements:**
• Bright, indirect light (6+ hours daily)
• Avoid direct sunlight (causes leaf burn)
• East or north-facing windows are ideal
• Can tolerate lower light but growth slows

**🌡️ Temperature & Humidity:**
• Temperature: 65-80°F (18-27°C)
• Humidity: 40-60% (use humidifier if needed)
• Avoid cold drafts and heating vents

**🌿 Support & Growth:**
• Provide moss pole or trellis for climbing
• Aerial roots help the plant climb naturally
• Rotate weekly for even growth
• Fenestrations develop with maturity and proper light

**🍃 Fertilizing:**
• Feed monthly during growing season (spring/summer)
• Use balanced liquid fertilizer (20-20-20)
• Reduce to every 2-3 months in winter
• Dilute to half strength to avoid burning

**✂️ Pruning & Maintenance:**
• Remove yellow or damaged leaves
• Wipe leaves weekly with damp cloth
• Prune for shape in spring
• Propagate stem cuttings in water

**🚨 Common Problems:**
• **Yellow leaves:** Overwatering or natural aging
• **Brown tips:** Low humidity or fluoride in water
• **No fenestrations:** Insufficient light or young plant
• **Drooping:** Underwatering or root bound

**Repotting:**
• Every 2-3 years or when root bound
• Use well-draining potting mix
• Go up one pot size only

Your Monstera can live for decades with proper care! Any specific issues you're experiencing?"""

        elif "snake plant" in message_lower or "sansevieria" in message_lower:
            return """🌱 **Snake Plant Care Guide**

As The Gardener, here's how to keep your Snake Plant thriving:

**💧 Watering (Most Important!):**
• Water every 2-6 weeks depending on season
• Allow soil to dry completely between waterings
• Water less in winter (monthly or less)
• Better to underwater than overwater
• Water at soil level, avoid getting leaves wet

**☀️ Light Requirements:**
• Tolerates low to bright indirect light
• Avoid direct sunlight (can bleach leaves)
• Perfect for offices and low-light rooms
• Growth faster in brighter conditions

**🌡️ Temperature:**
• Thrives in 60-80°F (15-27°C)
• Tolerates temperature fluctuations well
• Avoid freezing temperatures
• Normal household humidity is fine

**🏺 Soil & Potting:**
• Well-draining cactus/succulent mix
• Add perlite or sand for extra drainage
• Terra cotta pots help soil dry faster
• Repot every 3-5 years or when pot-bound

**🍃 Fertilizing:**
• Feed 2-3 times during growing season
• Use diluted liquid fertilizer
• Not necessary but promotes growth
• Skip fertilizing in winter

**✂️ Maintenance:**
• Wipe leaves with damp cloth monthly
• Remove damaged or yellowing leaves at base
• Divide rhizomes when repotting for new plants

**🌱 Propagation:**
• Leaf cuttings in water or soil
• Division of rhizomes (fastest method)
• Be patient - slow to root but very reliable

**🚨 Troubleshooting:**
• **Soft, mushy leaves:** Overwatering/root rot
• **Wrinkled leaves:** Severe underwatering
• **Brown tips:** Fluoride in water or low humidity
• **Slow growth:** Normal! They're naturally slow

**Why Snake Plants Are Perfect:**
• Nearly indestructible
• Air purifying qualities
• Low maintenance
• Tolerates neglect
• Perfect for beginners

This is one of the most forgiving plants you can grow! What specific questions do you have?"""

        # General care advice
        return """🌱 **Plant Care Guidance**

As The Gardener, I recommend:

**General Care Tips:**
• **Watering:** Check soil moisture before watering
• **Light:** Most houseplants prefer bright, indirect light
• **Humidity:** 40-60% humidity is ideal for most plants
• **Fertilizing:** Feed during growing season (spring/summer)

**Seasonal Adjustments:**
• **Winter:** Reduce watering and stop fertilizing
• **Spring:** Resume regular feeding and increase watering
• **Summer:** Monitor for heat stress and increase humidity

For specific care advice, please tell me:
1. What plant you're caring for
2. Your location/climate
3. Current growing conditions

I can then provide personalized care schedules and troubleshooting!"""
    
    async def _handle_local_environment(self, message: str) -> str:
        """Handle local environment and native plant queries."""
        return """🌍 **Local Environment & Native Plants**

As The Ecologist, I help you choose plants that thrive in your specific location!

**Benefits of Native Plants:**
• Support local wildlife and pollinators
• Require less water and maintenance
• Adapted to your climate conditions
• Help preserve regional biodiversity

**What I Can Help With:**
• USDA hardiness zone determination
• Native plant recommendations by region
• Soil analysis and improvement
• Climate-appropriate plant selection
• Sustainable gardening practices

**Tell me your location and I'll provide:**
• Native plants for your area
• Hardiness zone information
• Soil recommendations
• Best planting times
• Local growing challenges

**Popular Native Plant Categories:**
• **Trees:** Oak, Maple, Pine species
• **Shrubs:** Viburnum, Elderberry, Native azaleas
• **Perennials:** Coneflowers, Black-eyed Susan, Native grasses
• **Groundcovers:** Wild ginger, Native violets

Where are you located? I'll provide specific recommendations for your area!"""
    
    async def _handle_marketplace(self, message: str) -> str:
        """Handle marketplace and shopping queries."""
        message_lower = message.lower()
        
        # Use marketplace_search tool if available
        for tool in self.tools:
            if hasattr(tool, '__name__') and 'marketplace_search' in tool.__name__:
                try:
                    from .plantworks_tools import MarketplaceSearchInput
                    
                    # Extract plant name and price from message
                    plant_name = "snake plant"  # default
                    max_price = None
                    
                    if "snake plant" in message_lower:
                        plant_name = "snake plant"
                    elif "monstera" in message_lower:
                        plant_name = "monstera"
                    elif "fiddle leaf fig" in message_lower:
                        plant_name = "fiddle leaf fig"
                    
                    # Extract price if mentioned
                    import re
                    price_match = re.search(r'\$(\d+)', message)
                    if price_match:
                        max_price = float(price_match.group(1))
                    elif "under" in message_lower and any(char.isdigit() for char in message):
                        numbers = re.findall(r'\d+', message)
                        if numbers:
                            max_price = float(numbers[-1])
                    
                    result = tool(MarketplaceSearchInput(
                        plant_name=plant_name,
                        location="nationwide",
                        max_price=max_price
                    ))
                    
                    if result.get("products"):
                        response = f"""🛒 **Plant Marketplace Results**

Found {result['total_found']} options for **{result['plant_name']}**:

"""
                        for product in result["products"]:
                            response += f"""**{product['seller']}** - ${product['price']:.2f}
• Size: {product['size']}
• Rating: {product['rating']}/5 ({product['reviews']} reviews)
• Availability: {product['availability']}
• [Shop Now]({product['affiliate_url']})

"""
                        
                        response += """
**💡 Shopping Tips:**
• The Sill is our featured partner with excellent quality
• Compare shipping costs (free over certain amounts)
• Check seller ratings and return policies
• Consider plant size vs. price value

**Revenue Note:** We earn small commissions from partner sales, which helps keep Plantworks free!"""
                        
                        return response
                    
                except Exception as e:
                    logger.error(f"Marketplace tool error: {e}")
        
        return """🛒 **Plant Marketplace Guide**

As The Merchant, I help you find the best plants at great prices!

**Featured Partners:**
• **The Sill** - Premium houseplants, excellent packaging
• **Bloomscape** - Large plants, direct from greenhouse
• **Planterina** - Unique varieties, great prices

**What to Consider:**
• Plant size and maturity
• Shipping protection (especially in winter)
• Seller reputation and reviews
• Return/guarantee policies

**Tell me:**
1. What plant are you looking for?
2. Your budget range
3. Your location (for shipping)

I'll find the best options and compare prices across trusted sellers!"""
    
    async def _handle_general_query(self, message: str) -> str:
        """Handle general plant-related queries."""
        return """🌱 **Welcome to Plantworks!**

I'm your plant expert team, ready to help with:

**🌿 Plant Identification** (The Botanist)
• Identify plants from descriptions
• Learn botanical facts and care basics
• Discover plant families and characteristics

**🌱 Plant Care** (The Gardener)  
• Personalized care schedules
• Troubleshoot plant problems
• Seasonal care adjustments

**🌍 Local Environment** (The Ecologist)
• Find native plants for your area
• Soil and climate recommendations
• Sustainable gardening practices

**🛒 Plant Shopping** (The Merchant)
• Compare prices across retailers
• Find trusted sellers
• Get the best deals on quality plants

**How can I help you today?** Just ask about:
• "What is [plant name]?" for identification
• "How do I care for [plant]?" for growing tips
• "Where can I buy [plant]?" for shopping help
• "What native plants grow in [location]?" for local recommendations

I'm here to help you succeed with plants! 🌿"""

# Simulate google.adk.core.InvocationContext
class InvocationContext:
    """Context for agent invocation."""
    
    def __init__(self, session_state: Dict[str, Any]):
        self.session = SessionState(session_state)

class SessionState:
    """Session state container."""
    
    def __init__(self, state: Dict[str, Any]):
        self.state = state

# Simulate google.adk.tools.AgentTool
class AgentTool:
    """Tool wrapper for agents."""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.name = f"agent_tool_{agent.name}"

# Server implementation
async def run_server(agent: BaseAgent, host: str = "0.0.0.0", port: int = 8000):
    """Run the ADK server."""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    import os
    
    app = FastAPI(title="Plantworks ADK Server", version="1.0.0")
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    class ChatRequest(BaseModel):
        message: str
        session_id: Optional[str] = None
    
    class ChatResponse(BaseModel):
        response: str
        agent: str
        model: str
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "agent": agent.name}
    
    @app.post("/run", response_model=ChatResponse)
    async def run_agent(request: ChatRequest):
        try:
            # Create invocation context
            ctx = InvocationContext({"user_query": request.message})
            
            # Run agent
            response_content = ""
            agent_name = agent.name
            model_name = getattr(agent, 'model', 'simulated')
            
            async for event in agent._run_async_impl(ctx):
                if event.get("type") == "agent_response":
                    response_content = event.get("content", "")
                    agent_name = event.get("agent", agent.name)
                    model_name = event.get("model", model_name)
            
            return ChatResponse(
                response=response_content,
                agent=agent_name,
                model=model_name
            )
        
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root():
        return {
            "message": "Plantworks ADK Server",
            "agent": agent.name,
            "endpoints": {
                "chat": "/run",
                "health": "/health",
                "docs": "/docs"
            }
        }
    
    logger.info(f"🌱 Plantworks ADK Server starting on {host}:{port}")
    logger.info(f"📚 Agent: {agent.name}")
    logger.info(f"🛠️ Tools: {len(agent.tools)}")
    
    # Run the server
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# Mock Google Search tool
def Google Search(query: str) -> Dict[str, Any]:
    """Mock Google search tool."""
    return {
        "query": query,
        "results": [
            {
                "title": f"Search results for: {query}",
                "url": "https://example.com",
                "snippet": "Mock search result for demonstration"
            }
        ]
    }