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

# آدرس صفحه اصلی ورزش۳
BASE_URL = "https://www.varzesh3.com/"

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

        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if not href.startswith("/news/"):
                continue

            if href in seen:
                continue
            seen.add(href)

            match = re.search(r"/news/(\d+)", href)
            if not match:
                continue

            news_id = match.group(1)

            if already_sent(news_id):
                continue

            title = a.get_text(strip=True)
            if not title:
                continue

            full_link = f"https://www.varzesh3.com{href}"

            # تلاش برای پیدا کردن عکس خبر
            parent = a.find_parent("div", class_="newsbox-2-container")
            img_tag = parent.find("img") if parent else None
            img_url = None
            if img_tag and img_tag.has_attr("src"):
                img_url = img_tag["src"]
                if img_url.startswith("//"):
                    img_url = "https:" + img_url

            # ساخت پیام
            message = (
                "📣 <b>اخبار ورزشی</b>\n\n"
                f"<b>{escape(title)}</b>\n\n"
                f'<a href="{full_link}">مشاهده خبر</a>\n\n'
                "@akhbar_varzeshi_roz_iran"
            )

            if img_url:
                # اگر عکس داشت، عکس + متن
                bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=img_url,
                    caption=message,
                    parse_mode=ParseMode.HTML
                )
            else:
                # اگر عکس نداشت، فقط متن
                bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )

            mark_as_sent(news_id)
            print(f"خبر ارسال شد: {title}")
            break

    except Exception as e:
        print("خطا هنگام ارسال خبر:", e)

if __name__ == "__main__":
    send_news()
