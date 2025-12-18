import logging
import os

from mistralai import Mistral

logger = logging.getLogger(__name__)


def get_mistral_summary(input_text: str, system_prompt: str) -> str | None:
    """
    Gets a summary from Mistral AI.
    Returns the summary text or None if an error occurs.
    """
    try:
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            logger.error("MISTRAL_API_KEY environment variable not set.")
            return None

        client = Mistral(api_key=api_key)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
        ]
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.1,
        )
        summary = response.choices[0].message.content
        logger.info("Successfully got summary from Mistral AI.")
        return summary
    except Exception as e:
        logger.error(f"Mistral AI API error: {e}")
        return None


def format_for_prompt(item: dict, fields: list[tuple[str, str]]) -> str:
    """
    Formats an item object into a human-readable string for the AI.
    'fields' is a list of tuples, where each tuple contains the display name
    and the key to retrieve the value from the item dict.
    """
    lines = []
    for display_name, key in fields:
        if key == "organizer":
            organizer = item.get("organizer")
            if organizer and isinstance(organizer, dict):
                lines.append(f"Organizing Body: {organizer.get('name', 'N/A')}")
        elif key == "creator":
            creator = item.get("creator")
            if creator and isinstance(creator, dict):
                lines.append(f"Creator: {creator.get('name', 'N/A')}")
        else:
            lines.append(f"{display_name}: {item.get(key, 'N/A')}")
    return "\n".join(lines)


def json_to_prompt(objects: list[dict], formatter: callable) -> str:
    """
    Converts a list of objects into a formatted string prompt.
    """
    return "\n\n---\n\n".join(formatter(obj) for obj in objects)
