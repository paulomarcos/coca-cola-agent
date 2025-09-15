import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI

# --- Setup and Configuration ---
load_dotenv()

# Set up a basic logger for this module
log = logging.getLogger(__name__)

# --- Core Agent Function ---

def run_markdown_agent(campaign_package: list) -> BaseMessage:
    """
    Takes a creative brief and generates a markdown file.

    Args:
        campaign_package: A dictionary containing the campaign package

    Returns:
        A dictionary containing the generated ad copy.
    """

    # --- LLM Analysis Step ---
    try:
        log.info("Loading markdown prompt...")
        with open("prompts/markdown_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        log.error("Fatal: 'markdown_prompt.txt' file not found. Please create it.")
        raise

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    human_message = (
        "You are the Markdown Writer Agent. Your task is to generate a beautiful Markdown formatted file based"
        "on the contents of the campaign package. Each campaign should appear in its section, with the image following the header."
        f"Campaign package: {campaign_package}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]

    try:
        log.info(f"Invoking LLM to generate the markdown file.")
        response = llm.invoke(messages)
        log.info("Copy generated successfully.")
        return response
    except Exception as e:
        log.error(f"LLM invocation failed while generating the markdown file. Error: {e}")
        return BaseMessage(content="")


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
    campaign_copy = run_markdown(sample_creative_brief, test_city)

    print("\n--- TEST COMPLETE ---")
    print(f"Generated Copy for: {test_city}")
    print(json.dumps(campaign_copy, indent=2, ensure_ascii=False))