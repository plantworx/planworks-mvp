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

from typing import List, Dict, Any

from google.adk.agents import BaseAgent, LlmAgent
from pydantic import BaseModel, Field

from .config import config
from .botanist_agent import botanist_agent
from .ecologist_agent import ecologist_agent


# --- Structured Output Models ---
class PlantIdentification(BaseModel):
    """Model for plant identification results."""
    plant_name: str = Field(description="Scientific name of the plant")
    common_names: List[str] = Field(description="List of common names")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    characteristics: Dict[str, Any] = Field(description="Key identifying characteristics")



# --- MAIN PLANTWORKS AGENT ---
plantworks_main_agent = LlmAgent(
    name="plantworks_main_agent",
    model=config.worker_model,
    description="Main coordinator.",
    instruction=f"""You are an assistant.
    Delegate plant identification queries to tasks to Botanist.
    Delegate queries about growing plants in a particular area or location to Ecologist.
    For all other queries say you are unable to respond.
    """,
    sub_agents=[botanist_agent, ecologist_agent],
)

# Export the main agent directly (no wrapper needed)
root_agent = plantworks_main_agent