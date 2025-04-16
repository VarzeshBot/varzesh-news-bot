import sqlite3

def init_db():
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_news (
            title TEXT,
            link TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_duplicate(title, link):
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sent_news WHERE title=? OR link=?", (title, link))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_news(title, link):
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sent_news (title, link) VALUES (?, ?)", (title, link))
    conn.commit()
    conn.close()
