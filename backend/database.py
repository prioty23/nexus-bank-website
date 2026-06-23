import sqlite3
from datetime import datetime


DATABASE_NAME = "ebl_chatbot.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

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