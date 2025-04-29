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

# آدرس صفحه اخبار
BASE_URL = "https://www.khabarvarzeshi.com/service/allnews"

# بررسی خبرهای ارسال شده
def already_sent(news_id):
    cursor.execute("SELECT 1 FROM sent_news WHERE id=?", (news_id,))
    return cursor.fetchone() is not None

def mark_as_sent(news_id):
    cursor.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

# ارسال خبر
def send_news():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        news_links = soup.find_all("a", href=re.compile(r"^/news/\d+"))
        seen = set()

        for a in news_links:
            href = a.get("href")
            title = a.get_text(strip=True)

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

            message = (
                "📣 <b>اخبار ورزشی</b>\n\n"
                f"<b>{escape(title)}</b>\n\n"
                f"<a href='{full_link}'>مشاهده خبر</a>\n\n"
                "@akhbar_varzeshi_roz_iran"
            )

            bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

            mark_as_sent(news_id)
            print(f"خبر ارسال شد: {title}")
            break  # فقط یک خبر جدید بفرستد
    except Exception as e:
        print("❌ خطا هنگام ارسال خبر:", e)

# اجرای اصلی
if __name__ == "__main__":
    while True:
        send_news()
        time.sleep(300)  # هر ۵ دقیقه یکبار
