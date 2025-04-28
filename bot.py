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
CHANNEL_ID = "@akhbar_varzeshi_roz_iran"  # آیدی کانال تلگرام شما

bot = Bot(token=TOKEN)

conn = sqlite3.connect("news.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (id TEXT PRIMARY KEY)")
conn.commit()

BASE_URL = "https://www.varzesh3.com"

def already_sent(news_id):
    cursor.execute("SELECT 1 FROM sent_news WHERE id=?", (news_id,))
    return cursor.fetchone() is not None

def mark_as_sent(news_id):
    cursor.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

def send_news():
    try:
        response = requests.get(f"{BASE_URL}/news", timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # بررسی لینک‌های معتبر
        news_links = soup.select("a[href^='/news/']")
        seen = set()

        for a in news_links:
            href = a.get("href")
            title = a.get("title") or a.get_text(strip=True)

            if not href or not title or href in seen:
                continue
            seen.add(href)

            match = re.search(r"/news/(\d+)", href)
            if not match:
                continue

            news_id = match.group(1)
            if already_sent(news_id):
                continue

            full_link = f"{BASE_URL}{href}"
            message = f"<b>📣 {escape(title)}</b>\n<a href='{full_link}'>مطالعه خبر</a>"

            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            mark_as_sent(news_id)
            break

    except Exception as e:
        print("خطا:", e)
if __name__ == "__main__":
    response = requests.get(f"{BASE_URL}/news", timeout=10)
    soup = BeautifulSoup(response.text, "lxml")

    news_links = soup.select("a[href^='/news/']")
    print(f"تعداد لینک‌های خبری که پیدا شد: {len(news_links)}")
send_news()
