import openai

def init(api_key):
    openai.api_key = api_key


def generate_response(*args, listener):
    response = openai.Completion.create(
        engine='text-davinci-001',
        prompt=" ".join(args),
        temperature=0.9,
        max_tokens=2048)
    listener(response['choices'][0]['text'])

