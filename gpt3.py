from openai import OpenAI
import logging as log

client = None


def init(api_key):
    global client
    client = OpenAI(api_key=api_key)


def generate_response(*args):
    log.info(f'generate_response >> requesting: {" ".join(args)}')
    prompt = " ".join(args)
    tokens = 4096 - len(prompt)
    try:
        response = client.completions.create(
            model='gpt-3.5-turbo-instruct',
            prompt=prompt,
            max_tokens=2048)
        log.info(f"generate_response >> response: {response}")
        return response.choices[0].text

    except Exception as e:
        log.error(f"generate_response >> {e}")
