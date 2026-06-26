from mistralai.client import Mistral
import os
from dotenv import load_dotenv
from src.research_digest.model import EntryCreate

load_dotenv()

"""
You help to summarize, tags, and extract action item into a JSON for my research digestion tool as you are fed articles, notes, meeting transcripts you are expected to extract well. The dictionary should only have 3 properties: summary (string), tags ([string]), action_item (str). Reminder to not use ```json ``` format
"""


def summarize(text):
    with Mistral(
        api_key=os.getenv("API_KEY", ""),
    ) as mistral:
        res = mistral.chat.parse(
            model="magistral-small-2509",
            messages=[
                {
                    "role": "system",
                    "content": "You help to summarize, tags, and extract action item as you are fed articles, notes, meeting transcripts you are expected to extract well.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            stream=False,
            response_format=EntryCreate,
        )
        print(f"RESS: {res}")
        entry = res.choices[0].message.parsed
        return entry
