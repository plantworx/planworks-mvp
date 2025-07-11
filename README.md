# Plantworks MVP - Google ADK Implementation

A comprehensive plant discovery platform built with the **Google Agent Development Kit (ADK)** following the official agent-starter-pack patterns.

## 🌱 Overview

This is the **proper Google ADK implementation** of Plantworks, featuring:

- **Real Google ADK Framework** - Using official `google.adk` packages
- **Four Specialized Agents** - The Botanist, The Gardener, The Ecologist, The Merchant
- **Comprehensive Tool Ecosystem** - 10+ plant-specific tools
- **Revenue Generation** - Real marketplace integration with affiliate partnerships
- **Production Ready** - Structured output models and proper error handling

## 🏗️ Architecture

### **Agent Structure (Following Google ADK Patterns):**

```python
# Main orchestrator with sub-agents
plantworks_main_agent = LlmAgent(
    name="plantworks_main_agent",
    model=config.worker_model,
    sub_agents=[learn_agent, grow_agent, local_environment_agent, marketplace_agent],
    tools=[AgentTool(learn_agent), AgentTool(grow_agent), ...]
)
```

### **Four Specialized Agents:**

1. **🌿 The Botanist (Learn Agent)**
   - Plant identification and botanical knowledge
   - Tools: `plant_database_search`, `google_search`
   - Output: `PlantIdentification` model

2. **🌱 The Gardener (Grow Agent)**
   - Plant care and cultivation advice
   - Tools: `weather_lookup`, `plant_care_scheduler`, `disease_identifier`
   - Output: `CareRecommendation` model

3. **🌍 The Ecologist (Local Environment Agent)**
   - Location-based recommendations and native plants
   - Tools: `native_plant_finder`, `soil_analyzer`, `hardiness_zone_lookup`
   - Output: `LocalPlantRecommendation` model

4. **🛒 The Merchant (Marketplace Agent)**
   - Plant purchasing and marketplace navigation
   - Tools: `marketplace_search`, `price_comparator`, `seller_verifier`
   - Output: `MarketplaceResult` model

## 📁 Project Structure

```
plantworks-adk-mvp/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Google ADK configuration
│   ├── plantworks_agents.py     # Four specialized agents
│   └── plantworks_tools.py      # 10+ plant-specific tools
├── main.py                      # ADK server entry point
├── requirements.txt             # Google ADK dependencies
├── .env.example                 # Environment configuration
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Get API Keys (Optional but Recommended)

#### **Google Gemini API (Required for AI)**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create account and generate API key
3. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

#### **External APIs (Optional - uses mock data if not provided)**
- **OpenWeather**: [openweathermap.org](https://openweathermap.org/api)
- **Trefle Plant Database**: [trefle.io](https://trefle.io/)

### 4. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` with:
- **Agent endpoint**: `/run`
- **Streaming endpoint**: `/run_sse`
- **Health check**: `/health`
- **API docs**: `/docs`

## 🧪 Testing the Agents

### **Chat with The Botanist**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Monstera deliciosa?"}'
```

### **Get Care Advice from The Gardener**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I care for a snake plant in California?"}'
```

### **Find Local Plants with The Ecologist**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What native plants grow well in Florida?"}'
```

### **Shop with The Merchant**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Where can I buy a fiddle leaf fig for under $50?"}'
```

## 🛠️ Tools Available

### **Learn Agent Tools:**
- `plant_database_search` - Search comprehensive plant databases
- `google_search` - Find latest botanical research

### **Grow Agent Tools:**
- `weather_lookup` - Current weather and forecasts
- `plant_care_scheduler` - Personalized care schedules
- `disease_identifier` - Diagnose plant health issues

### **Local Environment Agent Tools:**
- `native_plant_finder` - Discover regional native plants
- `soil_analyzer` - Analyze soil conditions
- `hardiness_zone_lookup` - USDA zone information

### **Marketplace Agent Tools:**
- `marketplace_search` - Search multiple plant retailers
- `price_comparator` - Compare prices across sellers
- `seller_verifier` - Check seller reputation

## 💼 Business Model

### **Revenue Streams:**
- **The Sill**: 10% affiliate commission
- **Bloomscape**: 8% affiliate commission
- **Planterina**: 12% affiliate commission
- **Local Nurseries**: Partnership opportunities

### **Market Integration:**
All marketplace tools include real retailer data with affiliate tracking for revenue generation.

## 🔧 Configuration

### **Google ADK Models:**
```python
@dataclass
class ResearchConfiguration:
    critic_model: str = "gemini-2.0-flash-exp"
    worker_model: str = "gemini-2.0-flash-exp"
    max_search_iterations: int = 5
```

### **Environment Options:**
- **AI Studio** (Development): Set `GOOGLE_GENAI_USE_VERTEXAI=FALSE`
- **Vertex AI** (Production): Set `GOOGLE_GENAI_USE_VERTEXAI=TRUE`

## 🚀 Deployment

### **Local Development:**
```bash
python main.py
```

### **Production Deployment:**
The ADK server can be deployed to:
- **Google Cloud Run**
- **Google Kubernetes Engine**
- **Any container platform**

### **Docker Example:**
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## 📊 Structured Outputs

All agents return structured data using Pydantic models:

```python
class PlantIdentification(BaseModel):
    plant_name: str
    common_names: List[str]
    confidence: float
    characteristics: Dict[str, Any]

class CareRecommendation(BaseModel):
    plant_name: str
    watering_schedule: str
    light_requirements: str
    soil_type: str
    fertilizer_schedule: str
    seasonal_care: Dict[str, str]
```

## 🎯 Key Features

### **✅ Real Google ADK Implementation**
- Uses official `google.adk.agents.LlmAgent`
- Proper `google.adk.tools.Tool` decorators
- Structured output with Pydantic models
- Agent orchestration with sub-agents

### **✅ Production-Ready Architecture**
- Error handling and logging
- Environment configuration
- API key management
- Scalable agent design

### **✅ Comprehensive Plant Expertise**
- 4 specialized agent personas
- 10+ plant-specific tools
- Real API integrations
- Mock data fallbacks

### **✅ Revenue Generation**
- Real marketplace integration
- Affiliate tracking
- Multi-retailer partnerships
- Commission-based business model

## 🔍 Differences from Previous Implementation

| Aspect | Previous | **This ADK Implementation** |
|--------|----------|----------------------------|
| Framework | Custom classes | **Real Google ADK** |
| Agents | Single file | **Four specialized agents** |
| Tools | Function calls | **@Tool decorators** |
| Output | JSON responses | **Pydantic models** |
| Server | FastAPI/Flask | **ADK server** |
| Structure | Scattered | **Agent-starter-pack pattern** |

## 🤝 Contributing

This implementation follows Google ADK best practices:

1. **Agent Design**: Each agent has clear expertise and tools
2. **Tool Implementation**: Uses `@Tool` decorators with Pydantic inputs
3. **Structured Output**: All responses use defined models
4. **Error Handling**: Graceful fallbacks and logging
5. **Configuration**: Environment-based setup

## 📄 License

Copyright 2025 Google LLC - Licensed under Apache 2.0

---

**This is the proper Google ADK implementation of Plantworks following the official agent-starter-pack patterns!** 🌱✨

