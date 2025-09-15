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

def run_copywriter(creative_brief: Dict, city: str) -> Dict:
    """
    Takes a creative brief and generates various pieces of marketing copy.

    Args:
        creative_brief: A dictionary containing the strategic direction from the
                        CreativeDirector agent.
        city: The target city for which to write the copy (e.g., "New York").

    Returns:
        A dictionary containing the generated ad copy.
    """
    log.info(f"Initiating copywriting for city: {city}")
    log.info(f"Working from creative angle: '{creative_brief.get('marketing_angle')}'")

    # --- LLM Analysis Step ---
    try:
        log.info("Loading copywriter prompt...")
        with open("prompts/copywriter_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        log.error("Fatal: 'copywriter_prompt.txt' file not found. Please create it.")
        raise

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    structured_llm = llm.with_structured_output(schema={
        "title": "CampaignCopy",
        "description": "The generated text assets for the marketing campaign.",
        "type": "object",
        "properties": {
            "slogan": {
                "type": "string",
                "description": "A short, punchy slogan for a digital ad."
            },
            "social_media_post": {
                "type": "string",
                "description": "A ready-to-publish post for Instagram or X, including hashtags."
            },
            "web_banner_copy": {
                "type": "string",
                "description": "Slightly longer copy suitable for a web banner."
            }
        },
        "required": ["slogan", "social_media_post", "web_banner_copy"]
    })

    brief_details = json.dumps(creative_brief, indent=2)
    human_message = (
        "You are the Copywriter. Your task is to generate copy for the city of "
        f"**{city}**. Strictly adhere to the following creative brief and all of your instructions.\n\n"
        f"Creative Brief:\n{brief_details}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]

    try:
        log.info(f"Invoking LLM to generate copy for {city}...")
        response = structured_llm.invoke(messages)
        log.info("Copy generated successfully.")
        return response
    except Exception as e:
        log.error(f"LLM invocation failed while generating copy. Error: {e}")
        return {}


# --- Standalone Test Block ---

if __name__ == "__main__":
    print("Running Copywriter Agent in standalone test mode...")

    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # For LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "CokeConnect AI - Copywriter (Test)"

    # Sample input data mimicking a creative brief from the Director
    sample_creative_brief = {
        "marketing_angle": "Position Coca-Cola as the essential, refreshing companion to the diverse and exciting flavors of the Queens Night Market.",
        "target_emotion": "Joyful Discovery",
        "key_message": "Every flavor finds its perfect partner with an ice-cold Coke.",
        "target_audience": "Adventurous foodies and groups of friends exploring the vibrant Queens Night Market."
    }

    test_city = "New York" # Change to "São Paulo" or "Tokyo" to test localization

    # Execute the agent's main function
    campaign_copy = run_copywriter(sample_creative_brief, test_city)

    print("\n--- TEST COMPLETE ---")
    print(f"Generated Copy for: {test_city}")
    print(json.dumps(campaign_copy, indent=2, ensure_ascii=False))