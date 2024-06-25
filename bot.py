import logging
from telegram.ext import Updater
from datetime import datetime, time as dt_time
from openai import OpenAI
import requests

from comic import process_news

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get telegram api key
with open('telegram_key', 'r') as f:
    tg_api_key = f.read()

# Get openai api key
with open('openai_key', 'r') as f:
    openai_api_key = f.read()


CHANNEL_ID = '-1002202884623'
client = OpenAI(api_key=openai_api_key)


def post_daily_message(context):
    news, url = process_news(client)

    response = requests.get(url)
    if response.status_code == 200:
        context.bot.send_photo(chat_id=CHANNEL_ID,
                               photo=response.content,
                               caption=news[0]['url'])
    else:
        logger.error('Failed to fetch the image')


if __name__ == '__main__':
    updater = Updater(tg_api_key, use_context=True)
    job_queue = updater.job_queue

    now = datetime.now()
    t = dt_time(hour=now.hour-3, minute=now.minute, second=now.second+5)

    # Schedule the daily message at a specific time
    job_queue.run_daily(post_daily_message, time=t)

    updater.start_polling()
    updater.idle()
