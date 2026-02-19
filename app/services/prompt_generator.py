from google import genai
from typing import Literal
from app.utils import read_prompt
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

api_key = os.getenv("GEMINI_API_KEY")

def generate_prompts_from_prompt(text: str) -> list[str]:
    # Define the schema for a media segment
    class MediaSegment:
        def __init__(self):
            self.segment_number: int
            self.type: Literal["image", "video"]
            self.duration_seconds: int  # For images: 2-5 seconds, for videos: 4 seconds
            self.prompt: str

    # Your system prompt (use the updated one from the artifact)
    system_prompt = read_prompt("prompt_generator_prompt")

    client = genai.Client(api_key=api_key)
    input_text = text

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "segment_number": {
                            "type": "integer",
                            "description": "Sequential order of the segment"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["image", "video"],
                            "description": "Type of media segment"
                        },
                        "duration_seconds": {
                            "type": "integer",
                            "description": "Duration in seconds. For videos: always 5. For images: 2-5 seconds based on content importance"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Complete self-contained prompt for generating the media"
                        }
                    },
                    "required": ["segment_number", "type", "duration_seconds", "prompt"]
                }
            }
        },
        contents=input_text,
    )

    # Parse the response
    segments = response.parsed
    return segments