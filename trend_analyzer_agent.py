import os
import json
import logging
from dotenv import load_dotenv
from typing import List, Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# --- Setup and Configuration ---
load_dotenv()

# Set up a basic logger for this module
log = logging.getLogger(__name__)

# --- Core Agent Function ---

def run_analyzer_on_events(city: str, events_data: dict) -> list:
    """
    Analyzes a dictionary of raw events to score their marketing potential.

    This function encapsulates the TrendAnalyzer agent's logic:
    1. Takes a list of raw events for a specific city.
    2. Uses a configured LLM with a detailed system prompt to analyze them.
    3. The LLM is instructed to access the event URLs for context.
    4. Returns a list of events with analysis and a marketing score.

    Args:
        city: The city to which the events belong.
        events_data: A dictionary from the scanner, e.g., {"events": [...]}.

    Returns:
        A list of analyzed event dictionaries. Returns an empty list on failure.
    """
    log.info(f"Initiating trend analysis for {city}...")

    raw_events = events_data.get("events")
    if not raw_events:
        log.warning(f"No raw events provided for {city}. Skipping analysis.")
        return []

    # --- LLM Analysis Step ---
    try:
        log.info("Loading trend analyzer prompt...")
        with open("prompts/trend_analyzer_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt_template = f.read()
    except FileNotFoundError:
        log.error("Fatal: 'trend_analyzer_prompt.txt' file not found.")
        raise

    system_prompt = system_prompt_template.format(city=city)

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(schema={
        "title": "AnalyzedEvents",
        "description": "A list of analyzed events with marketing potential scores.",
        "type": "object",
        "properties": {
            "analyzed_events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "event_title": {"type": "string"},
                        "event_url": {"type": "string"},
                        "city": {"type": "string"},
                        "summary": {"type": "string"},
                        "marketing_potential_score": {"type": "integer"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["event_title", "event_url", "city", "summary", "marketing_potential_score", "reasoning"]
                }
            }
        },
        "required": ["analyzed_events"]
    })

    events_json_string = json.dumps(raw_events, indent=2)
    human_message = (
        f"Here is the list of potential events for {city}. "
        f"Please analyze each one based on my instructions. Your ability to access the event_url for full context is crucial for an accurate analysis.\n\n"
        f"{events_json_string}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]

    try:
        log.info(f"Invoking LLM for analysis of {len(raw_events)} events...")
        response = structured_llm.invoke(messages)
        analyzed_events = response.get("analyzed_events", [])
        log.info(f"LLM analysis complete. Processed {len(analyzed_events)} events.")
        return analyzed_events
    except Exception as e:
        log.error(f"LLM invocation failed during trend analysis. Error: {e}")
        return []


# --- Standalone Test Block ---

if __name__ == "__main__":
    # This block allows you to test this agent script in isolation.
    print("Running TrendAnalyzer Agent in standalone test mode...")

    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # For LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "CokeConnect AI - TrendAnalyzer (Test)"

    # Sample input data that mimics the output of the EventScanner
    sample_events_data = {
        "events": [
            {
                "event_title": "Massive Heatwave Hits NYC: Temps to Soar to 95°F",
                "event_url": "https://gothamist.com/news/massive-heatwave-hits-nyc-temps-to-soar-to-95f-this-weekend"
            },
            {
                "event_title": "The Queens Night Market Returns With Over 50 Food Vendors",
                "event_url": "https://gothamist.com/arts-entertainment/the-queens-night-market-returns-with-over-50-food-vendors"
            },
            {
                "event_title": "MTA Announces Weekend Service Changes on the L Train",
                "event_url": "https://gothamist.com/news/mta-announces-weekend-service-changes-on-the-l-train"
            }
        ]
    }

    test_city = "New York"

    # Execute the agent's main function
    result = run_analyzer_on_events(test_city, sample_events_data)

    print("\n--- TEST COMPLETE ---")
    print("Result:")
    print(json.dumps(result, indent=2))