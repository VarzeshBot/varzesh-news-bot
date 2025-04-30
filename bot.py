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

# اتصال به دیتابیس برای جلوگیری از ارسال تکراری
conn = sqlite3.connect("news.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (id TEXT PRIMARY KEY)")
conn.commit()

# آدرس سایت فوتبالی
BASE_URL = "https://footballi.net/news/latest"

# بررسی تکراری بودن
def already_sent(news_id):
    cursor.execute("SELECT 1 FROM sent_news WHERE id=?", (news_id,))
    return cursor.fetchone() is not None

# ثبت خبر ارسال‌شده
def mark_as_sent(news_id):
    cursor.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

# تابع اصلی ارسال خبر
def send_news():
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        news_items = soup.select(".latest-news-list .news-item")
        print("تعداد خبر پیدا شده:", len(news_items))

        for item in news_items:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            full_link = f"https://footballi.net{href}"

            title_tag = item.select_one(".text-container")
            title = title_tag.get_text(strip=True) if title_tag else "خبر جدید"

            match = re.search(r"/news/(\d+)", href)
            if not match:
                continue
            news_id = match.group(1)

            if already_sent(news_id):
                continue

            # دریافت عکس
            img_tag = item.find("img")
            img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            caption = f"📣 <b>اخبار ورزشی</b>\n\n<b>{escape(title)}</b>\n\n<a href='{full_link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

            if img_url:
                bot.send_photo(chat_id=CHANNEL_ID, photo=img_url, caption=caption, parse_mode=ParseMode.HTML)
            else:
                bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode=ParseMode.HTML)

            mark_as_sent(news_id)
            print(f"خبر ارسال شد: {title}")
            break  # فقط یک خبر ارسال شود
    except Exception as e:
        print("خطا هنگام ارسال خبر:", e)

# اجرای دائمی
if __name__ == "__main__":
    while True:
        send_news()
        time.sleep(300)  # هر ۵ دقیقه
