import os
import re
import time
import sqlite3
from html import escape
import requests
from bs4 import BeautifulSoup
from telegram import Bot, ParseMode

# اطلاعات ربات
TOKEN = "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ"
CHANNEL_ID ="@akhbar_varzeshi_roz_iran"

# ساخت بات تلگرام
bot = Bot(token=TOKEN)

# اتصال به دیتابیس
conn = sqlite3.connect("news.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (id TEXT PRIMARY KEY)")
conn.commit()

# آدرس صفحه اخبار ورزش ۳
BASE_URL = "https://www.varzesh3.com/news"

def already_sent(news_id):
    cursor.execute("SELECT 1 FROM sent_news WHERE id=?", (news_id,))
    return cursor.fetchone() is not None

def mark_as_sent(news_id):
    cursor.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

def send_news():
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        news_boxes = soup.find_all("div", class_="newsbox-2-container")
        seen = set()

        for box in news_boxes:
            a_tag = box.find("a", href=True)
            if not a_tag:
                continue

            href = a_tag['href']
            title = a_tag.get_text(strip=True)

            if not href or not title:
                continue

            if href in seen or not href.startswith("/news/"):
                continue
            seen.add(href)

            news_id_match = re.search(r"/news/(\d+)", href)
            if not news_id_match:
                continue

            news_id = news_id_match.group(1)
            if already_sent(news_id):
                continue

            full_link = f"https://www.varzesh3.com{href}"
            message = f"<b>📣 اخبار ورزشی</b>\n\n<b>{escape(title)}</b>\n<a href='{full_link}'>مطالعه خبر</a>"

            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            mark_as_sent(news_id)
            print("خبر ارسال شد:", title)
            break  # فقط یک خبر در هر بار اجرا

    except Exception as e:
        print("خطا در دریافت یا ارسال خبر:", e)

# اجرای اصلی
if __name__ == "__main__":
    send_news()
