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

# آدرس صفحه اصلی
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

        # فقط اولین خبر جدید پیدا شود
        first_news = soup.find("a", href=re.compile(r"^/news/\d+"))
        if not first_news:
            print("خبری پیدا نشد")
            return

        href = first_news.get("href")
        title = first_news.get_text(strip=True)

        if not href or not title:
            print("اطلاعات خبر ناقص است")
            return

        match = re.search(r"/news/(\d+)", href)
        if not match:
            print("فرمت لینک درست نیست")
            return

        news_id = match.group(1)
        if already_sent(news_id):
            print("این خبر قبلاً ارسال شده")
            return

        full_link = f"https://www.khabarvarzeshi.com{href}"
        message = (
            "📣 <b>اخبار ورزشی</b>\n\n"
            f"<b>{escape(title)}</b>\n\n"
            f'<a href="{full_link}">مشاهده خبر</a>\n\n'
            "@akhbar_varzeshi_roz_iran"
        )

        bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
        )

        mark_as_sent(news_id)
        print(f"خبر ارسال شد: {title}")

    except Exception as e:
        print("خطا هنگام ارسال خبر:", e)

if __name__ == "__main__":
    while True:
        send_news()
        time.sleep(300)  # هر ۵ دقیقه چک کن
