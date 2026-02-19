from google import genai
from app.utils import read_prompt
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

api_key = os.getenv("GEMINI_API_KEY")

def generate_script_from_prompt(segments: list[str], main_prompt: str) -> list[str]:
    client = genai.Client(api_key=api_key)

    # Your segment list (provided as context)
    segments_context = segments

    input_text = f"""Main Prompt: {main_prompt}

    Segment List Context:
    {segments_context}

    Generate a voice-over script for each segment with appropriate timing."""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        config={
            "system_instruction": read_prompt("script_generator_prompt"),
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "number",
                            "description": "Starting timestamp in seconds"
                        },
                        "end_time": {
                            "type": "number",
                            "description": "Ending timestamp in seconds"
                        },
                        "script": {
                            "type": "string",
                            "description": "The narration text to be spoken during this time period"
                        }
                    },
                    "required": ["start_time", "end_time", "script"]
                }
            }
        },
        contents=input_text,
    )

    # Parse the response
    script_segments = response.parsed
    return script_segments