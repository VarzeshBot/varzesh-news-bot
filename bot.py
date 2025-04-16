import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Bot
import os

# دریافت متغیرها از محیط اجرا
TOKEN = os.environ.get("TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

# حافظه موقتی (فقط در زمان اجرای فعلی)
latest_sent_title = None
latest_sent_link = None

# دریافت خبر از RSS
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

# ترجمه عنوان
def translate_title(title_fa):
    return GoogleTranslator(source='auto', target='en').translate(title_fa)

# جستجوی عکس مرتبط در گوگل
def search_image(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}&searchType=image"
    response = requests.get(search_url).json()
    if "items" in response:
        return response["items"][0]["link"]
    return None

# ارسال خبر
def send_news():
    global latest_sent_title, latest_sent_link

    bot = Bot(token=TOKEN)
    news = get_latest_news()

    if news:
        title_fa, link = news

        # جلوگیری از تکراری بودن در زمان اجرای فعلی
        if title_fa == latest_sent_title or link == latest_sent_link:
            print("خبر تکراری است، ارسال نمی‌شود.")
            return

        title_en = translate_title(title_fa)
        image_url = search_image(title_en)

        message = f"<b>اخبار ورزشی</b> 🏆\n\n<b>{title_fa}</b>\n\n<a href='{link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

        if image_url:
            bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_url, caption=message, parse_mode="HTML")
        else:
            bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="HTML")

        latest_sent_title = title_fa
        latest_sent_link = link
        print("خبر ارسال شد.")

# اجرای اصلی
send_news()
