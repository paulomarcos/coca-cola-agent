import os
import json
import logging
import base64
from dotenv import load_dotenv
from typing import Dict
from datetime import datetime

from openai import OpenAI

# --- Setup and Configuration ---
load_dotenv()

# Set up a basic logger for this module
log = logging.getLogger(__name__)

IMAGE_DIRECTORY = "campaign-images/"

# --- Core Agent Function ---

def run_image_creator(prompt_data: Dict) -> Dict:
    """
    Takes an image prompt and uses the OpenAI API to generate and save an image.

    Args:
        prompt_data: A dictionary from the VisualStrategist, containing the
                     key "image_prompt".

    Returns:
        A dictionary with the creation status and filename.
    """
    image_prompt = prompt_data.get("image_prompt")
    if not image_prompt:
        log.error("No image_prompt found in the input data.")
        return {"status": "Failed", "error": "No prompt provided."}

    log.info("Initiating image creation process...")
    log.info(f"Using prompt: '{image_prompt[:100]}...'") # Log first 100 chars

    try:
        client = OpenAI()

        # This API call is based on your instruction to use gpt-4.1-mini's
        # built-in image generation tool.
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"{image_prompt}",
            tools=[{"type": "image_generation"}]
        )

        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        image_b64_data = image_data[0]

        if not image_b64_data:
             raise ValueError("Image generation was called, but no b64_json data was returned.")

        # Decode the Base64 string to binary data
        image_bytes = base64.b64decode(image_b64_data)

        # Generate a unique filename with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{IMAGE_DIRECTORY}campaign_image_{timestamp}.png"

        # Save the image to a file
        log.info(f"Saving image to file: {filename}")
        with open(filename, "wb") as f:
            f.write(image_bytes)

        return {"status": "Success", "filename": filename}

    except Exception as e:
        log.error(f"Image creation failed. Error: {e}", exc_info=True)
        return {"status": "Failed", "error": str(e)}


# --- Standalone Test Block ---

if __name__ == "__main__":
    print("Running ImageCreator Agent in standalone test mode...")

    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Sample input data mimicking the output of the VisualStrategist
    sample_prompt_data = {
        "image_prompt": "Vibrant and dynamic close-up shot of an ice-cold Coca-Cola glass bottle, beaded with condensation, resting on a worn wooden table at the bustling Queens Night Market. The bottle is surrounded by a colorful array of small plates from different food vendors, with steam gently rising. The background is a lively but softly blurred scene of diverse crowds of people laughing, with colorful strings of lights and neon signs creating a beautiful bokeh effect. The overall lighting is warm and inviting, capturing a mood of joyful discovery and urban energy. --ar 16:9 --style raw, cinematic, photorealistic, 8k, hyper-detailed"
    }

    # Execute the agent's main function
    result = run_image_creator(sample_prompt_data)

    print("\n--- TEST COMPLETE ---")
    print("Result:")
    print(json.dumps(result, indent=2))

    if result.get("status") == "Success":
        print(f"\nImage successfully created and saved as '{result.get('filename')}' in your current directory.")