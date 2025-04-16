import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram import Bot
import os
import sqlite3

# متغیرهای محیطی
TOKEN = os.environ.get("TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

# اتصال به پایگاه داده SQLite
conn = sqlite3.connect("news.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (link TEXT PRIMARY KEY)")
conn.commit()

# دریافت خبر جدید از RSS ورزش ۳
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

# ترجمه عنوان برای جستجوی عکس
def translate_title(title_fa):
    return GoogleTranslator(source='auto', target='en').translate(title_fa)

# جستجوی عکس در گوگل
def search_image(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}&searchType=image"
    response = requests.get(search_url).json()
    if "items" in response:
        return response["items"][0]["link"]
    return None

# ارسال خبر
def send_news():
    bot = Bot(token=TOKEN)
    news = get_latest_news()

    if not news:
        print("هیچ خبری دریافت نشد.")
        return

    title_fa, link = news

    # بررسی در دیتابیس که تکراری نباشه
    cursor.execute("SELECT link FROM sent_news WHERE link = ?", (link,))
    if cursor.fetchone():
        print("خبر تکراری است، ارسال نمی‌شود.")
        return

    # ترجمه و جستجوی تصویر
    title_en = translate_title(title_fa)
    image_url = search_image(title_en)

    # آماده‌سازی پیام
    message = f"<b>اخبار ورزشی</b> 🏆\n\n<b>{title_fa}</b>\n\n<a href='{link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

    if image_url:
        bot.send_photo(chat_id=CHANNEL_USERNAME, photo=image_url, caption=message, parse_mode="HTML")
    else:
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="HTML")

    # ذخیره لینک در دیتابیس برای جلوگیری از تکرار
    cursor.execute("INSERT INTO sent_news (link) VALUES (?)", (link,))
    conn.commit()
    print("خبر ارسال شد.")

# اجرای اصلی
send_news()
