import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import json
import sqlite3
import os
from deep_translator import GoogleTranslator

# اطلاعات ربات
TOKEN = "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ"
CHANNEL_ID = "@akhbar_varzeshi_roz_iran"

# لینک RSS
RSS_FEED = "https://www.varzesh3.com/rss/all"

# تابع ترجمه تیتر
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return ""

# تابع دریافت عکس از unsplash
def get_unsplash_image(query):
    try:
        response = requests.get(f"https://source.unsplash.com/featured/?{query}")
        return response.url
    except:
        return None

# اتصال به دیتابیس SQLite
conn = sqlite3.connect("news.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS news (link TEXT PRIMARY KEY)''')
conn.commit()

# ارسال خبر به تلگرام
def send_news():
    feed = feedparser.parse(RSS_FEED)

    for entry in feed.entries:
        title = entry.title
        link = entry.link

        # بررسی تکراری نبودن لینک
        cursor.execute("SELECT link FROM news WHERE link=?", (link,))
        if cursor.fetchone():
            continue

        # دریافت تصویر مرتبط
        translated_title = translate_to_english(title)
        image_url = get_unsplash_image(translated_title)

        # ساخت پیام
        caption = f"<b>📣 {title}</b>\n<a href='{link}'>مطالعه خبر</a>"
        bot = Bot(token=TOKEN)

        # ارسال با عکس
        if image_url:
            bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption, parse_mode="HTML")
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML")

        # ذخیره لینک در دیتابیس
        cursor.execute("INSERT INTO news (link) VALUES (?)", (link,))
        conn.commit()

        # فقط یک خبر ارسال شود
        break

send_news()
