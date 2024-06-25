import requests
from openai import OpenAI


HEADLINE_RATING_PREPROMPT = "Filter out unsuitable news, summarize, and rank these news articles based on their potential for creating an ironic comic using float numbers (from 0.0 to 1.0). News with politics or events with regular people are best and should be rated higher. Games, entertainment, tech or sports are worst and should be rated lower. Here are the articles:\n\n"
HEADLINE_RATING_POSTPROMPT = "\nProvide the summaries and rankings in the format: <article index>: <summary> - <ranking score from 0.0 to 1.0)>\n"


# Get news api key
with open('news_key', 'r') as f:
    news_api_key = f.read()


def get_news(client):
    articles = fetch_news()

    articles = summarize_and_rank_news(client, articles)

    return articles

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?category=general&country=ru&apiKey={news_api_key}"

    response = requests.get(url)
    news = response.json()

    return news['articles']

def summarize_and_rank_news(client, articles):
    # Constructing the prompt for processing multiple articles in one go
    prompt = HEADLINE_RATING_PREPROMPT
    for i, article in enumerate(articles):
        prompt += f"{i+1}. {article['title']} {article['description']}\n"
    prompt += HEADLINE_RATING_POSTPROMPT

    response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=1500
    )

    # Parsing the response
    processed_articles = []
    lines = response.choices[0].text.strip().split("\n")
    for line in lines:
        if ":" in line:
            index, summary_rank = line.split(":", 1)
            summary, rank = summary_rank.rsplit(" - ", 1)
            processed_articles.append((articles[int(index)-1], summary.strip(), float(rank.strip())))

    # Sorting articles based on ranking score
    ranked_articles = sorted(processed_articles, key=lambda x: x[2], reverse=True)
    return ranked_articles


if __name__ == '__main__':
    with open('openai_key', 'r') as f:
        openai_api_key = f.read()
    client = OpenAI(api_key=openai_api_key)

    r = get_news(client)
