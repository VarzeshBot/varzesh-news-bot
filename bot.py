import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Bot
import os
from db import init_db, is_duplicate, save_news

# تنظیمات شما
TOKEN = os.environ.get("TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

# گرفتن خبر جدید از RSS
def get_latest_news():
    rss_url = "https://www.varzesh3.com/rss/all"
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, features="xml")
    items = soup.findAll("item")
    if not items:
        return None
    article = items[0]
    title = article.title.text
    link = article.link.text
    return title, link

# ترجمه تیتر
def translate_title(title_fa):
    return GoogleTranslator(source='auto', target='en').translate(title_fa)

# جستجوی عکس در گوگل
def search_image(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}&searchType=image"
    response = requests.get(search_url).json()
    if "items" in response:
        images = response["items"]
        return images[0]["link"]
    return None

# ارسال پیام به تلگرام
def send_news():
    init_db()

    bot = Bot(token=TOKEN)
    news = get_latest_news()
    if not news:
        return

    title_fa, link = news

    if is_duplicate(title_fa, link):
        print("خبر تکراری است، ارسال نمی‌شود.")
        return

    title_en = translate_title(title_fa)
    image_url = search_image(title_en)

    message = f"<b>اخبار ورزشی</b> 📣\n\n<b>{title_fa}</b>\n\n<a href='{link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

    if image_url:
        bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_url, caption=message, parse_mode='HTML')
    else:
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode='HTML')

    save_news(title_fa, link)

# اجرای اصلی
send_news()
