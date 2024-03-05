from typing import Optional

from openai import OpenAI
import logging as log

openai_client: Optional[OpenAI] = None


def init(api_key: str):
    global openai_client
    openai_client = OpenAI(api_key=api_key)


def generate_response(prompt: str) -> Optional[str]:
    log.info(f'generate_response >> requesting: {prompt}')
    try:
        response = openai_client.completions.create(
            model='gpt-3.5-turbo-instruct',
            prompt=prompt,
            max_tokens=2048)
        log.info(f"generate_response >> response: {response}")
        return response.choices[0].text

    except Exception as e:
        log.error(f"generate_response >> {e}")
