from openpyxl import Workbook, load_workbook
from datetime import datetime
import os


EXCEL_FILE = "chat_logs.xlsx"


def create_excel_file_if_not_exists():
    if not os.path.exists(EXCEL_FILE):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Chat Logs"

        sheet.append([
            "session_id",
            "complaint_id",
            "user_message",
            "bot_reply",
            "source",
            "blocked",
            "status",
            "created_at"
        ])

        workbook.save(EXCEL_FILE)


def save_chat_to_excel(
    session_id,
    user_message,
    bot_reply,
    source,
    blocked,
    status,
    complaint_id=""
):
    create_excel_file_if_not_exists()

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook.active

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append([
        session_id,
        complaint_id,
        user_message,
        bot_reply,
        source,
        blocked,
        status,
        created_at
    ])

    workbook.save(EXCEL_FILE)


def get_chat_history_from_excel(session_id, limit=6):
    create_excel_file_if_not_exists()

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook.active

    history = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        row_session_id = row[0]
        user_message = row[2]
        bot_reply = row[3]
        blocked = row[5]

        if row_session_id == session_id and blocked == False:
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

    return history[-limit:]