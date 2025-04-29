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

# آدرس سایت اصلی
BASE_URL = "https://www.khabarvarzeshi.com/service/allnews"

# ذخیره لینک‌های ارسال شده برای جلوگیری از تکراری‌ها
sent_links = set()

def send_news():
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        news_items = soup.select("ul.list > li")

        for item in news_items:
            a_tag = item.find("a", href=True, title=True)
            img_tag = item.find("img", src=True)

            if not a_tag or not img_tag:
                continue

            title = a_tag["title"].strip()
            link = a_tag["href"]
            img_url = img_tag["src"]

            if not link.startswith("http"):
                full_link = f"https://www.khabarvarzeshi.com{link}"
            else:
                full_link = link

            if full_link in sent_links:
                continue

            message = f"<b>📣 اخبار ورزشی</b>\n\n<b>{escape(title)}</b>\n\n<a href='{full_link}'>مشاهده خبر</a>\n\n@akhbar_varzeshi_roz_iran"

            # ارسال پیام به کانال همراه با عکس
            bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img_url,
                caption=message,
                parse_mode=ParseMode.HTML
            )

            sent_links.add(full_link)

            print(f"خبر ارسال شد: {title}")
            break  # فقط یک خبر جدید در هر اجرا

    except Exception as e:
        print("خطا در ارسال خبر:", e)

if __name__== "__main__":
    while True:
        send_news()
        time.sleep(300)  # هر ۵ دقیقه (۳۰۰ ثانیه) یکبار
