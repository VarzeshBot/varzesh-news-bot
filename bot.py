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

# حذف دیتابیس قبلی فقط بار اول
if os.path.exists("news.db"):
    os.remove("news.db")

# اتصال به دیتابیس
conn = sqlite3.connect("news.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS sent_news (id TEXT PRIMARY KEY)")
conn.commit()

# آدرس سایت خبرورزشی
BASE_URL = "https://www.khabarvarzeshi.com/service/allnews"

# بررسی تکراری بودن
def already_sent(news_id):
    cursor.execute("SELECT 1 FROM sent_news WHERE id=?", (news_id,))
    return cursor.fetchone() is not None

# ذخیره خبر جدید
def mark_as_sent(news_id):
    cursor.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

# ارسال خبر
def send_news():
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        news_blocks = soup.select("li[class*=mass] a[href*='/news/']")

        print("تعداد خبر پیدا شده:", len(news_blocks))
        seen = set()

        for a in news_blocks:
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

            # گرفتن عکس
            parent_li = a.find_parent("li")
            img_tag = parent_li.find("img") if parent_li else None
            img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            # ساخت پیام
            caption = f"📣 <b>اخبار ورزشی</b>\n\n<b>{escape(title)}</b>\n\n<a href='{full_link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

            # ارسال به تلگرام
            if img_url:
                bot.send_photo(chat_id=CHANNEL_ID, photo=img_url, caption=caption, parse_mode=ParseMode.HTML)
            else:
                bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode=ParseMode.HTML)

            mark_as_sent(news_id)
            print(f"خبر ارسال شد: {title}")
            break  # فقط یک خبر در هر بار اجرا

    except Exception as e:
        print("خطا هنگام ارسال خبر:", e)

# اجرای دائم
if __name__ == "__main__":
    while True:
        send_news()
        time.sleep(300)  # هر ۵ دقیقه یک بار
