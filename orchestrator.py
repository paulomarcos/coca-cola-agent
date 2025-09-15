import json
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

# --- Agent Function Imports ---
# We now import the real agent functions from all our modules.
from event_scanner_agent import run_scanner_for_city
from trend_analyzer_agent import run_analyzer_on_events
from creative_director_agent import run_creative_director
from copywriter_agent import run_copywriter
from visual_strategist_agent import run_visual_strategist
from image_creator_agent import run_image_creator
from markdown_writer_agent import run_markdown_agent

# --- Logging Configuration ---

# Set up logging to both file and console
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

CAMPAIGN_PACKAGES_DIR = "campaign-packages/"

# Avoid adding handlers if they already exist
if not logger.handlers:
    # File handler
    file_handler = logging.FileHandler("logs/orchestrator.log")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)


# --- Core Pipeline Logic ---

def run_daily_marketing_pipeline():
    """
    The main job that the scheduler will run. It orchestrates the entire
    process from scanning to final asset creation.
    """
    logging.info("="*80)
    logging.info("STARTING FULL DAILY MARKETING PIPELINE RUN")
    logging.info("="*80)

    targets = {
        "São Paulo": "https://g1.globo.com/sp/sao-paulo/",
        "New York": "https://gothamist.com/",
        "Tokyo": "https://www.timeout.com/tokyo/things-to-do"
    }

    completed_campaigns = []

    # --- STAGE 1 & 2: SCAN AND ANALYZE ALL CITIES ---
    all_high_potential_events = []
    for city, url in targets.items():
        try:
            logging.info(f"--- Stage 1: Scanning {city} ---")
            raw_events_data = run_scanner_for_city(url)

            if raw_events_data and raw_events_data.get("events"):
                logging.info(f"--- Stage 2: Analyzing Events for {city} ---")
                analyzed_events = run_analyzer_on_events(city, raw_events_data)

                high_potential_events = [
                    event for event in analyzed_events
                    if event.get("marketing_potential_score", 0) >= 7
                ]
                if high_potential_events:
                    logging.info(f"Found {len(high_potential_events)} high-potential opportunities for {city}.")
                    all_high_potential_events.extend(high_potential_events)
            else:
                logging.warning(f"No events found or returned from scanner for {city}.")
        except Exception as e:
            logging.error(f"An error occurred during scan/analysis for {city}: {e}", exc_info=True)

    # --- STAGE 3: CREATIVE GENERATION FOR HIGH-POTENTIAL EVENTS ---
    if not all_high_potential_events:
        logging.warning("No high-potential events found across all cities. Ending pipeline run.")
        return

    logging.info(f"\n--- Stage 3: Starting Creative Generation for {len(all_high_potential_events)} events ---")
    for event in all_high_potential_events:
        try:
            event_title = event.get('event_title')
            city = event.get('city')
            logging.info(f"\n>>> Generating campaign for: '{event_title}' in {city} <<<")

            # Creative Director
            creative_brief = run_creative_director(event)
            if not creative_brief:
                logging.error(f"Failed to generate creative brief for '{event_title}'. Skipping.")
                continue

            # Parallel Creative Work: Copy and Visuals
            logging.info(f"Generating copy and visuals for '{event_title}'...")
            campaign_copy = run_copywriter(creative_brief, city)
            image_prompt_data = run_visual_strategist(creative_brief, city)

            # Image Creation
            image_creation_result = {}
            if image_prompt_data and image_prompt_data.get("image_prompt"):
                image_creation_result = run_image_creator(image_prompt_data)
            else:
                logging.error(f"Failed to get image prompt for '{event_title}'.")

            # --- STAGE 4: AGGREGATE FINAL CAMPAIGN PACKAGE ---
            final_campaign_package = {
                "source_event": event,
                "creative_brief": creative_brief,
                "text_assets": campaign_copy,
                "visual_assets_status": image_creation_result
            }
            completed_campaigns.append(final_campaign_package)
            logging.info(f">>> Successfully created full campaign package for '{event_title}' <<<")

        except Exception as e:
            logging.error(f"A critical error occurred while generating campaign for '{event.get('event_title')}': {e}", exc_info=True)

    # --- STAGE 5: SAVE FINAL RESULTS ---
    if completed_campaigns:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{CAMPAIGN_PACKAGES_DIR}full_campaign_packages_{timestamp}.json"

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(completed_campaigns, f, indent=2, ensure_ascii=False)

        logging.info(f"\nSuccessfully saved {len(completed_campaigns)} full campaign packages to {output_filename}")
    else:
        logging.warning("Pipeline run completed, but no campaign packages were generated.")

    # --- STAGE 6: SAVE MARKDOWN FILE ---
    markdown_text = run_markdown_agent(completed_campaigns)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    with open(f"{timestamp}.md", "w", encoding="utf-8") as f:
        f.write(markdown_text.content)
    logging.info(f"\nSuccessfully saved full campaign packages as {timestamp}.md")

    logging.info("="*80)
    logging.info("FULL DAILY MARKETING PIPELINE RUN FINISHED")
    logging.info("="*80)


# --- Scheduler Setup and Main Execution Block ---

def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(run_daily_marketing_pipeline, 'cron', hour=3, minute=0)

    logging.info("Scheduler configured to run daily at 3:00 AM. Press Ctrl+C to exit.")

    # For immediate testing, uncomment the line below.
    logging.info("Running an initial job now for testing purposes...")
    run_daily_marketing_pipeline()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
