import sqlite3
from datetime import datetime


DATABASE_NAME = "EBL_chatbot.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_memory (
           session_id TEXT PRIMARY KEY,
           summary TEXT,
           updated_at TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            complaint_id TEXT,
            user_message TEXT,
            bot_reply TEXT,
            source TEXT,
            blocked INTEGER,
            status TEXT,
            created_at TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS website_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT,
            page_url TEXT,
            page_text TEXT,
            status TEXT,
            updated_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_chat(
    session_id,
    user_message,
    bot_reply,
    source,
    blocked,
    status,
    complaint_id=""
):
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO chat_logs (
            session_id,
            complaint_id,
            user_message,
            bot_reply,
            source,
            blocked,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        complaint_id,
        user_message,
        bot_reply,
        source,
        1 if blocked else 0,
        status,
        created_at
    ))

    connection.commit()
    connection.close()


def get_chat_history(session_id, limit=6):
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_message, bot_reply
        FROM chat_logs
        WHERE session_id = ?
        AND blocked = 0
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, limit))

    rows = cursor.fetchall()
    connection.close()

    history = []

    rows.reverse()

    for row in rows:
        user_message = row[0]
        bot_reply = row[1]

        if user_message:
            history.append({
                "role": "user",
                "content": user_message
            })

        if bot_reply:
            history.append({
                "role": "assistant",
                "content": bot_reply
            })

    return history


def save_website_text(page_name, page_url, page_text):
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        DELETE FROM website_info
        WHERE page_url = ?
    """, (page_url,))

    cursor.execute("""
        INSERT INTO website_info (
            page_name,
            page_url,
            page_text,
            status,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        page_name,
        page_url,
        page_text,
        "active",
        updated_at
    ))

    connection.commit()
    connection.close()


def get_website_information():
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT page_name, page_url, page_text
        FROM website_info
        WHERE status = 'active'
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()
    connection.close()

    website_information = ""

    for row in rows:
        page_name = row[0]
        page_url = row[1]
        page_text = row[2]

        website_information += f"Page: {page_name}\n"
        website_information += f"URL: {page_url}\n"
        website_information += f"Content:\n{page_text}\n\n"

    return website_information


def get_session_summary(session_id):
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT summary
        FROM session_memory
        WHERE session_id = ?
    """, (session_id,))

    row = cursor.fetchone()
    connection.close()

    if row:
        return row[0]

    return ""


def save_session_summary(session_id, summary):
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT OR REPLACE INTO session_memory (
            session_id,
            summary,
            updated_at
        )
        VALUES (?, ?, ?)
    """, (
        session_id,
        summary,
        updated_at
    ))

    connection.commit()
    connection.close()

# Ensure all tables exist as soon as this module is imported.
create_database()

def clear_website_information():
    create_database()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM website_info")

    connection.commit()
    connection.close()