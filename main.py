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

from dotenv import load_dotenv; load_dotenv()
import asyncio
import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from app import root_agent
from app.plantworks_agents import extract_plant_query
from app.plantworks_tools import plant_database_search, PlantSearchInput
from app.plant_rag_api import router as plant_rag_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App --- 
app = FastAPI(
    title="Plantworks ADK Server",
    description="An API for interacting with the Plantworks agent.",
    version="1.0.0"
)

# Mount the plant RAG API at /api
app.include_router(plant_rag_router, prefix="/api")

# Initialize the runner once at startup
runner = InMemoryRunner(agent=root_agent)

class ChatRequest(BaseModel):
    query: str
    user_id: str = "web_user"
    session_id: str = "web_session"

class ChatResponse(BaseModel):
    response: str

@app.on_event("startup")
async def startup_event():
    logger.info("🌱 Initializing Plantworks Agent Runner")
    logger.info(f"📚 Agent: {root_agent.name}")
    logger.info(f"🛠️ Tools available: {len(root_agent.tools)}")
    logger.info(f"👥 Sub-agents: {len(root_agent.sub_agents)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🤖 Shutting down runner.")
    await runner.close()

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Receives a query and returns the agent's response."""
    logger.info(f"Received query for user '{request.user_id}' in session '{request.session_id}': {request.query}")
    # Directly send all queries to the LLM agent (no plant query routing)

    # Pass the user query as a Content object with a list of Part objects (only 'text'), matching ADK runner schema
    message = Content(parts=[Part(text=request.query)])
    logger.info(f"Message sent to agent runner: {message}")
    final_response = "Sorry, I could not process your request."

    try:
        # Ensure a session exists before running the agent
        session_service = runner.session_service
        session = await session_service.get_session(
            session_id=request.session_id, app_name=runner.app_name, user_id=request.user_id
        )
        if not session:
            logger.info(f"Creating new session: {request.session_id}")
            await session_service.create_session(
                session_id=request.session_id, user_id=request.user_id, app_name=runner.app_name
            )

        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=message
        ):
            logger.info(f"Received event: {event}")
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Combine all text parts to form the final response.
                    text_parts = [part.text for part in event.content.parts if part.text]
                    if text_parts:
                        final_response = "".join(text_parts)
                break # Exit after getting the final message
        
        logger.info(f"Agent response: {final_response}")
        return ChatResponse(response=final_response)
    except Exception as e:
        logger.error(f"An error occurred during agent execution: {e}", exc_info=True)
        return ChatResponse(response="An error occurred while processing your request.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "127.0.0.1")
    logger.info(f"🚀 Starting FastAPI server on {host}:{port} (reload enabled)")
    # Always enable reload for development convenience
    uvicorn.run("main:app", host=host, port=port, reload=True)
