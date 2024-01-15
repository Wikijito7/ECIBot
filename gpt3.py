import openai

def init(api_key):
    openai.api_key = api_key


def generate_response(*args):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=" ".join(args),
        temperature=0.7,
        max_tokens=1024)
    return response['choices'][0]['text']

