import os
import re
import time
import sqlite3
from html import escape
import requests
from bs4 import BeautifulSoup
from telegram import Bot, ParseMode

# حذف دیتابیس قبلی برای تست اولیه (در حالت نهایی بهتر است حذف نشود)
if os.path.exists("news.db"):
    os.remove("news.db")

# اطلاعات کانال
TOKEN = os.getenv("BOT_TOKEN", "8107821630:AAGYeDcX9u0gsuGRL0bscEtNullhjeo8cIQ")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@akhbar_varzeshi_roz_iran")

bot = Bot(token=TOKEN)

# اتصال به دیتابیس برای جلوگیری از ارسال تکراری
conn = sqlite3.connect("news.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (id TEXT PRIMARY KEY)")
conn.commit()

# آدرس صفحه اصلی اخبار
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

        # پیدا کردن لینک‌های خبر
        news_blocks = soup.select("li[class*=mass] a[href*='/news/']")
       print("تعداد خبر پیدا شده:", len(news_blocks))

 seen = set()

        for a in news_blocks:
            href = a.get("href")
            title = a.get("title")
            img_tag = a.find("img")

            if not href or not title or href in seen:
                continue

            seen.add(href)
            match = re.search(r"/news/(\\d+)", href)
            if not match:
                continue

            news_id = match.group(1)
            if already_sent(news_id):
                continue

            full_link = f"https://www.khabarvarzeshi.com{href}"
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            message = (
                "📣 <b>اخبار ورزشی</b>\n\n"
                f"<b>{escape(title)}</b>\n\n"
                f"<a href='{full_link}'>مشاهده خبر</a>\n"
                "@akhbar_varzeshi_roz_iran"
            )

            bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url if image_url else "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Placeholder_view_vector.svg/800px-Placeholder_view_vector.svg.png",
                caption=message,
                parse_mode=ParseMode.HTML
            )

            mark_as_sent(news_id)
            print(f"خبر ارسال شد: {title}")
            break  # فقط یک خبر ارسال شود

    except Exception as e:
        print("خطا در ارسال خبر:", e)

# اجرای دائم هر ۵ دقیقه
while True:
    send_news()
    time.sleep(300)
