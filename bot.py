import os
import re
import time
import sqlite3
from html import escape
import requests
from bs4 import BeautifulSoup
from telegram import Bot, ParseMode

# اطلاعات کانال
TOKEN = os.getenv("BOT_TOKEN", "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@akhbar_varzeshi_roz_iran")

bot = Bot(token=TOKEN)

# اتصال به دیتابیس
conn = sqlite3.connect("news.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (id TEXT PRIMARY KEY)")
conn.commit()

# آدرس صفحه‌ی خبرها
BASE_URL = "https://www.khabarvarzeshi.com/service/allnews"

def already_sent(news_id):
    cursor.execute("SELECT 1 FROM sent_news WHERE id=?", (news_id,))
    return cursor.fetchone() is not None

def mark_as_sent(news_id):
    cursor.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

def send_news():
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")

        # پیدا کردن خبرها
        news_list = soup.select("ul.news li")

        seen = set()

        for item in news_list:
            a_tag = item.find("a", href=True)
            img_tag = item.find("img", src=True)

            if not a_tag or not img_tag:
                continue

            href = a_tag["href"]
            title = a_tag.get("title", "").strip()
            img_url = img_tag["src"]

            if not href or not title or href in seen:
                continue
            seen.add(href)

            match = re.search(r"/news/(\d+)", href)
            if not match:
                continue

            news_id = match.group(1)
            if already_sent(news_id):
                continue

            full_link = f"https://www.khabarvarzeshi.com{href}"

            caption = (
                "📣 <b>اخبار ورزشی</b>\n\n"
                f"<b>{escape(title)}</b>\n\n"
                f'<a href="{full_link}">مشاهده خبر</a>\n\n'
                "@akhbar_varzeshi_roz_iran"
            )

            # ارسال عکس همراه با متن
            bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img_url,
                caption=caption,
                parse_mode="HTML"
            )

            mark_as_sent(news_id)
            print(f"خبر ارسال شد: {title}")
            break  # فقط یک خبر در هر بار
    except Exception as e:
        print("خطا در ارسال خبر:", e)

if _name_ == "_main_":
    while True:
        send_news()
        time.sleep(300)  # هر 5 دقیقه
