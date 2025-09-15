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

def run_visual_strategist(creative_brief: Dict, city: str) -> Dict:
    """
    Takes a creative brief and generates a detailed text-to-image prompt.

    Args:
        creative_brief: A dictionary containing the strategic direction from the
                        CreativeDirector agent.
        city: The target city, to add visual context.

    Returns:
        A dictionary containing the generated image prompt.
    """
    log.info(f"Initiating visual strategy for city: {city}")
    log.info(f"Working from creative angle: '{creative_brief.get('marketing_angle')}'")

    # --- LLM Analysis Step ---
    try:
        log.info("Loading visual strategist prompt...")
        with open("prompts/visual_strategist_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        log.error("Fatal: 'visual_strategist_prompt.txt' file not found. Please create it.")
        raise

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    structured_llm = llm.with_structured_output(schema={
        "title": "ImagePrompt",
        "description": "A detailed prompt for a text-to-image generation model.",
        "type": "object",
        "properties": {
            "image_prompt": {
                "type": "string",
                "description": "The complete, detailed text-to-image prompt."
            }
        },
        "required": ["image_prompt"]
    })

    brief_details = json.dumps(creative_brief, indent=2)
    human_message = (
        "You are the Visual Strategist. Your task is to generate a text-to-image prompt "
        f"that captures the essence of the following creative brief for the city of **{city}**.\n\n"
        f"Creative Brief:\n{brief_details}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]

    try:
        log.info("Invoking LLM to generate image prompt...")
        response = structured_llm.invoke(messages)
        log.info("Image prompt generated successfully.")
        return response
    except Exception as e:
        log.error(f"LLM invocation failed while generating image prompt. Error: {e}")
        return {}


# --- Standalone Test Block ---

if __name__ == "__main__":
    print("Running VisualStrategist Agent in standalone test mode...")

    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # For LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "CokeConnect AI - VisualStrategist (Test)"

    # Sample input data mimicking a creative brief from the Director
    sample_creative_brief = {
        "marketing_angle": "Position Coca-Cola as the essential, refreshing companion to the diverse and exciting flavors of the Queens Night Market.",
        "target_emotion": "Joyful Discovery",
        "key_message": "Every flavor finds its perfect partner with an ice-cold Coke.",
        "target_audience": "Adventurous foodies and groups of friends exploring the vibrant Queens Night Market."
    }

    test_city = "New York"

    # Execute the agent's main function
    image_prompt_data = run_visual_strategist(sample_creative_brief, test_city)

    print("\n--- TEST COMPLETE ---")
    print("Generated Image Prompt Data:")
    print(json.dumps(image_prompt_data, indent=2, ensure_ascii=False))