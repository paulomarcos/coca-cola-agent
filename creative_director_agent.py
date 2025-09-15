import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# --- Setup and Configuration ---
load_dotenv()

# Set up a basic logger for this module
log = logging.getLogger(__name__)

# --- Core Agent Function ---

def run_creative_director(analyzed_event: Dict) -> Dict:
    """
    Takes a high-potential analyzed event and generates a strategic creative brief.

    Args:
        analyzed_event: A dictionary for a single event that has been scored
                        as high-potential by the TrendAnalyzer agent.

    Returns:
        A dictionary containing the creative brief.
    """
    log.info(f"Initiating creative direction for event: '{analyzed_event.get('event_title')}'")

    # --- LLM Analysis Step ---
    try:
        log.info("Loading creative director prompt...")
        with open("prompts/creative_director_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        log.error("Fatal: 'creative_director_prompt.txt' file not found. Please create it.")
        raise

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7) # Higher temp for more creative output
    structured_llm = llm.with_structured_output(schema={
        "title": "CreativeBrief",
        "description": "The strategic creative brief for a marketing campaign.",
        "type": "object",
        "properties": {
            "marketing_angle": {"type": "string"},
            "target_emotion": {"type": "string"},
            "key_message": {"type": "string"},
            "target_audience": {"type": "string"}
        },
        "required": ["marketing_angle", "target_emotion", "key_message", "target_audience"]
    })

    event_details = json.dumps(analyzed_event, indent=2)
    human_message = (
        "You are the Creative Director. Here is the high-potential marketing opportunity "
        "identified by the TrendAnalyzer. Your task is to develop a creative brief based on it.\n\n"
        f"Event Details:\n{event_details}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]

    try:
        log.info("Invoking LLM to generate creative brief...")
        response = structured_llm.invoke(messages)
        log.info("Creative brief generated successfully.")
        return response
    except Exception as e:
        log.error(f"LLM invocation failed while generating creative brief. Error: {e}")
        return {}


# --- Standalone Test Block ---

if __name__ == "__main__":
    print("Running CreativeDirector Agent in standalone test mode...")

    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # For LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "CokeConnect AI - CreativeDirector (Test)"

    # Sample input data mimicking a high-potential event
    sample_analyzed_event = {
      "event_title": "The Queens Night Market Returns With Over 50 Food Vendors",
      "event_url": "https://gothamist.com/arts-entertainment/the-queens-night-market-returns-with-over-50-food-vendors",
      "city": "New York",
      "summary": "The Queens Night Market, a large, open-air food festival in NYC, is returning. It's known for its diverse, affordable food options and large, happy crowds.",
      "marketing_potential_score": 9,
      "reasoning": "Excellent potential. This event has a huge audience, is centered around food and community, and strongly aligns with Coca-Cola's values of togetherness and happiness."
    }

    # Execute the agent's main function
    creative_brief = run_creative_director(sample_analyzed_event)

    print("\n--- TEST COMPLETE ---")
    print("Generated Creative Brief:")
    print(json.dumps(creative_brief, indent=2))