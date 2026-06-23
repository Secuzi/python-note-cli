from mistralai.client import Mistral
import os
from dotenv import load_dotenv

load_dotenv()


def summarize(text):
    with Mistral(
        api_key=os.getenv("API_KEY", ""),
    ) as mistral:
        res = mistral.chat.complete(
            model="magistral-small-2509",
            messages=[
                {
                    "role": "system",
                    "content": "You help to summarize, tags, and extract action item into a JSON for my research digestion tool as you are fed articles, notes, meeting transcripts you are expected to extract well. The dictionary should only have 3 properties: summary (string), tags ([string]), action_item (str). Reminder to not use ```json ``` format",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            stream=False,
            response_format={
                "type": "text",
            },
        )

        # Handle response
        # 1. Go into the first item of the 'choices' list
        choice = res.choices[0]

        # 2. Access the 'message' object
        message = choice.message

        # 3. Access the 'content' list.
        # Index 0 is the ThinkChunk, Index 1 is the TextChunk we want.
        text_chunk = message.content[1]

        # 4. Extract the actual text string
        return text_chunk.text
