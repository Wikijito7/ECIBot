from typing import Optional

from hugchat import hugchat
from hugchat.hugchat import ChatBot
from hugchat.login import Login
from openai import OpenAI
import logging as log


class AiClient:
    def generate_response(self, prompt: str) -> Optional[str]:
        pass


class OpenAiClient(AiClient):
    def __init__(self, api_key: str):
        self.__openai_client: Optional[OpenAI] = OpenAI(api_key=api_key)

    def generate_response(self, prompt: str) -> Optional[str]:
        log.info(f'OpenAiClient generate_response >> requesting: {prompt}')
        try:
            response = self.__openai_client.completions.create(
                model='gpt-3.5-turbo-instruct',
                prompt=prompt,
                max_tokens=2048)
            log.info(f"OpenAiClient generate_response >> response: {response}")
            return response.choices[0].text

        except Exception as e:
            log.error(f"OpenAiClient generate_response >> {e}")


class HuggingChatClient(AiClient):
    def __init__(self, email: str, password: str):
        sign = Login(email, password)
        cookies = sign.login()
        self.__hugging_chat_client: Optional[ChatBot] = hugchat.ChatBot(cookies=cookies.get_dict())

    def generate_response(self, prompt: str) -> Optional[str]:
        log.info(f'HuggingChatClient generate_response >> requesting: {prompt}')
        try:
            response = self.__hugging_chat_client.chat(prompt)
            log.info(f"HuggingChatClient generate_response >> response: {response}")
            return response.text

        except Exception as e:
            log.error(f"HuggingChatClient generate_response >> {e}")
