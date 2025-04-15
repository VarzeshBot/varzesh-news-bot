import requests
import json
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Bot


# تنظیمات شما
TOKEN = "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ"
CHANNEL_USERNAME = "@akhbar_varzeshi_roz_iran"
GOOGLE_API_KEY = "AIzaSyDyPE9Mk0JhL-wvzFEg1OGBqy6o8LjAaGc"
SEARCH_ENGINE_ID = "9171969b9d6eb4efa"

# دریافت آخرین خبر از RSS
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

# ترجمه عنوان خبر
def translate_title(title_fa):
    return GoogleTranslator(source='auto', target='en').translate(title_fa)

# جستجوی عکس مرتبط
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

# ارسال پیام به تلگرام
def send_news():
    bot = Bot(token=TOKEN)
    news = get_latest_news()
    if news:
        title_fa, link = news

        # بررسی تکراری بودن
        last = read_last_news()
        if title_fa == last["last_title"] or link == last["last_link"]:
            print("خبر جدیدی نیست.")
            return

        # ادامه ارسال اگر خبر جدید بود
        title_en = translate_title(title_fa)
        image_url = search_image(title_en)
        message = f"📣 اخبار ورزشی\n\n🏆 {title_fa}\n\n🔗 {link}\n\n@akhbar_varzeshi_roz_iran"

        if image_url:
            bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_url, caption=message)
        else:
            bot.send_message(chat_id=CHANNEL_USERNAME, text=message)

        # ذخیره این خبر به‌عنوان آخرین خبر
        write_last_news(title_fa, link)

send_news()
