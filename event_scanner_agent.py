import os
import json
import logging
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# --- Setup and Configuration ---
load_dotenv()

# Set up a basic logger for this module
log = logging.getLogger(__name__)

# --- Core Agent Function ---

def run_scanner_for_city(url: str) -> dict:
    """
    Runs the complete event scanning process for a single URL.

    This function encapsulates the agent's logic:
    1. Scrapes the provided URL for its text content.
    2. Uses a configured LLM with a system prompt to analyze the text.
    3. Returns a structured dictionary of found events.

    Args:
        url: The URL of the city's news or event website to scan.

    Returns:
        A dictionary containing the list of events, or an empty dict on failure.
    """
    log.info(f"Initiating event scan for URL: {url}")

    # --- 1. Scraping Step ---
    try:
        log.info("Scraping website content...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')
        text_content = soup.get_text(separator=' ', strip=True)
        scraped_content = text_content[:15000] # Limit content size for LLM
        log.info(f"Scraping successful. Content length: {len(scraped_content)} chars.")

    except requests.RequestException as e:
        log.error(f"Failed to scrape URL {url}. Error: {e}")
        return {} # Return empty dict on failure

    # --- 2. LLM Analysis Step ---
    try:
        log.info("Analyzing content with LLM...")
        with open("prompts/event_scanner_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        log.error("Fatal: 'event_scanner_prompt.txt' file not found.")
        raise

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(schema={
        "title": "Events",
        "description": "A list of extracted events",
        "type": "object",
        "properties": { "events": { "type": "array", "items": { "type": "object", "properties": { "event_title": {"type": "string"}, "event_url": {"type": "string"}}, "required": ["event_title", "event_url"]}}},
        "required": ["events"]
    })

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Here is the scraped text from the website. Please analyze it and extract the events:\n\n{scraped_content}")
    ]

    try:
        response = structured_llm.invoke(messages)
        log.info(f"LLM analysis complete. Found {len(response.get('events', []))} potential events.")
        return response
    except Exception as e:
        log.error(f"LLM invocation failed. Error: {e}")
        return {}


# --- Standalone Test Block ---

if __name__ == "__main__":
    # This block allows you to test this agent script in isolation.
    print("Running EventScanner Agent in standalone test mode...")

    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # For LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "CokeConnect AI - EventScanner (Test)"

    # Define a target to test
    test_url = "https://gothamist.com/"

    # Execute the agent's main function
    result = run_scanner_for_city(test_url)

    print("\n--- TEST COMPLETE ---")
    print("Result:")
    print(json.dumps(result, indent=2))