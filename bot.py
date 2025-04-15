import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Bot
import json
import os

# تنظیمات شما
TOKEN = os.environ.get
 "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ"
CHANNEL_USERNAME = os.environ.get
 "@akhbar_varzeshi_roz_iran"
GOOGLE_API_KEY = os.environ.get
 "AIzaSyDyPE9Mk0JhL-wvzFEg1OGBqy6o8LjAaGc"
SEARCH_ENGINE_ID = os.environ.get
 "9171969b9d6eb4efa"
# دریافت آخرین خبر RSS
def get_latest_news():
    rss_url = "https://www.varzesh3.com/news/rss/all"
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

# ذخیره آخرین خبر
def write_last_news(title, link):
    with open("last_news.json", "w") as file:
        json.dump({"last_title": title, "last_link": link}, file)

# خواندن آخرین خبر
def read_last_news():
    try:
        with open("last_news.json", "r") as file:
            return json.load(file)
    except:
        return {"last_title": "", "last_link": ""}

# ارسال خبر به تلگرام
def send_news():
    bot = Bot(token=TOKEN)
    news = get_latest_news()
    if news:
        title_fa, link = news

        # بررسی تکراری نبودن
        last = read_last_news()
        if title_fa == last["last_title"] or link == last["last_link"]:
            print("خبر تکراری است، ارسال نمی‌شود.")
            return

        # ادامه فقط اگر خبر جدید بود
        title_en = translate_title(title_fa)
        image_url = search_image(title_en)

        # پیام HTML حرفه‌ای
        message = f"<b>📣 اخبار ورزشی</b>\n\n<b>{title_fa}</b>\n\n<a href='{link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

        if image_url:
            bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_url, caption=message, parse_mode='HTML')
        else:
            bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode='HTML')

        write_last_news(title_fa, link)

# اجرای اصلی
send_news()
