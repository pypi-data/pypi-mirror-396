import json
import logging
from typing import Any, Dict
from ollama import Client

from txn_msg_parser.constants import DEFAULT_HOST, DEFAULT_MODEL

logger = logging.getLogger(__name__)


class AIFactory:
    def __init__(self, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST):
        self.model = model
        self.host = host

    def ask(self, prompt: str) -> Dict[str, Any]:
        client = Client(host=self.host)
        response = client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "num_predict": -1,
            },
            think=False,
        )

        content = response["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Model output: {content}")
            logger.error(e)
            raise e
