import logging
from openai import OpenAI, BadRequestError
from news import get_news


IMAGE_GENERATION_PROMPT = '''Take the main subjects and actions from the following news headline and create a funny and ironic caricature comic. The caricature comic should have no text in any form or language. Use bright and colorful images. Exaggerate the subjects and actions to create humor and irony. Mock common stereotypes in a light-hearted and humorous way. Ensure the caricature comic makes fun of all elements involved. Keep the scenes dynamic and engaging, with characters displaying exaggerated emotions and actions. No speech bubbles or written text should appear in the images. Make the setting and characters vivid and entertaining.
News Headline: {russian_text}'''


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def send_prompt_to_openai(client, prompt_text):
    """
    Sends the defined prompt to the OpenAI API and returns the response.
    """

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt_text,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


def process_news(client):
    # Define the prompt

    news = get_news(client)

    for n in news:
        try:
            logger.info(f'Trying {n}')
            req = IMAGE_GENERATION_PROMPT.format(russian_text=n[1])

            # Send the prompt and get the response
            pic_url = send_prompt_to_openai(client, req)

            logger.info('Success')
            break
        except BadRequestError:
            logger.info('Failure')
            continue
    return n, pic_url


if __name__ == '__main__':
    with open('openai_key', 'r') as f:
        openai_api_key = f.read()
    client = OpenAI(api_key=openai_api_key)

    n, p = process_news(client)
    print(n)
    print(p)
