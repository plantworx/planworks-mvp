import os
import requests
import json

def test_agent_routing():
    """
    Regression test: Ensure the Plantworks agent routes plant queries to sub-agents/tools and does NOT reply with readiness/generic responses.
    """
    url = os.getenv("PLANTWORKS_API_URL", "http://127.0.0.1:8000/chat")
    payload = {
        "user_id": "test_user",
        "session_id": "test_session",
        "query": "How do I care for a cactus?"
    }
    resp = requests.post(url, json=payload, timeout=20)
    assert resp.status_code == 200, f"Non-200 response: {resp.status_code}, Body: {resp.text}"
    data = resp.json()
    response_text = data.get("response", "")
    # Should not be a readiness message
    forbidden = ["I'm ready", "ready to receive", "process your plant-related questions"]
    assert not any(frag in response_text for frag in forbidden), f"Agent responded with readiness/generic message: {response_text}"
    # Should mention care or cactus or route to a sub-agent/tool
    assert any(word in response_text.lower() for word in ["cactus", "water", "light", "soil", "grow", "care", "agent", "tool"]), f"Agent did not route or answer plant care: {response_text}"
    print("✅ Agent routing test passed: Response was not generic and referenced plant care or sub-agent/tool.")

if __name__ == "__main__":
    test_agent_routing()
