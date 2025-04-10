import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Bot
import random

# تنظیمات شما
TOKEN = "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ"
CHANNEL_USERNAME = "@akhbar_varzeshi_roz_iran"
GOOGLE_API_KEY = "AIzaSyDyPE9Mk0JhL-wvzFEg1OGBqy6o8LjAaGc"
SEARCH_ENGINE_ID = "9171969b9d6eb4efa"

# تابع دریافت اخبار از RSS ورزش ۳
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

# ترجمه تیتر از فارسی به انگلیسی
def translate_title(title_fa):
    return GoogleTranslator(source='auto', target='en').translate(title_fa)

# جستجوی عکس مرتبط در گوگل
def search_image(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&searchType=image&key={GOOGLE_API_KEY}"
    response = requests.get(search_url).json()
    if "items" in response:
        images = response["items"]
        return images[0]["link"]
    return None

# ارسال پیام به تلگرام
def send_news():
    bot = Bot(token=TOKEN)
    news = get_latest_news()
    if news:
        title_fa, link = news
        title_en = translate_title(title_fa)
        image_url = search_image(title_en)
        message = f"📣 اخبار ورزشی\n\n🏆 {title_fa}\n🔗 {link}\n\n@akhbar_varzeshi_roz_iran"

        if image_url:
            bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_url, caption=message)
        else:
            bot.send_message(chat_id=CHANNEL_USERNAME, text=message)
    else:
        bot.send_message(chat_id=CHANNEL_USERNAME, text="هیچ خبری دریافت نشد.")

# اجرا
send_news()