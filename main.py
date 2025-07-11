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

import asyncio
import logging
import os
from pathlib import Path

# Use ADK simulation until official package is available
from app.adk_simulation import run_server
from app import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Plantworks ADK application."""
    logger.info("🌱 Starting Plantworks ADK Server (Simulation Mode)")
    
    # Set up environment
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Server will run on {host}:{port}")
    logger.info(f"📚 Agent: {root_agent.name}")
    logger.info(f"🛠️ Tools available: {len(root_agent.tools)}")
    logger.info(f"👥 Sub-agents: {len(root_agent.sub_agents)}")
    
    # List available tools
    tool_names = [getattr(tool, '__name__', str(tool)) for tool in root_agent.tools]
    logger.info(f"🔧 Tools: {', '.join(tool_names)}")
    
    # Run the ADK server
    await run_server(
        agent=root_agent,
        host=host,
        port=port
    )

if __name__ == "__main__":
    asyncio.run(main())

