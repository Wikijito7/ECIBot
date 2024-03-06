from typing import Optional

from openai import OpenAI
import logging as log


class OpenAiClient:
    def __init__(self, api_key: str):
        self.__openai_client: Optional[OpenAI] = OpenAI(api_key=api_key)

    def generate_response(self, prompt: str) -> Optional[str]:
        log.info(f'generate_response >> requesting: {prompt}')
        try:
            response = self.__openai_client.completions.create(
                model='gpt-3.5-turbo-instruct',
                prompt=prompt,
                max_tokens=2048)
            log.info(f"generate_response >> response: {response}")
            return response.choices[0].text

        except Exception as e:
            log.error(f"generate_response >> {e}")
