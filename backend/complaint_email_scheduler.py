from apscheduler.schedulers.background import BackgroundScheduler

from database import (
    get_due_three_day_complaints,
    mark_three_day_email_sent,
)

from email_sender import send_three_day_followup_email


scheduler = None


def check_due_complaint_emails():
    print("Checking due complaint emails...")

    complaints = get_due_three_day_complaints()

    for complaint in complaints:
        try:
            sent = send_three_day_followup_email(
                complaint["customer_email"],
                complaint,
            )

            if sent:
                mark_three_day_email_sent(complaint["complaint_id"])
                print(f"Three-day email sent for complaint: {complaint['complaint_id']}")

        except Exception as error:
            print(f"Failed to send three-day email for {complaint['complaint_id']}: {error}")


def start_complaint_email_scheduler():
    global scheduler

    if scheduler is not None:
        return

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        check_due_complaint_emails,
        "interval",
        minutes=1,
    )

    scheduler.start()
    print("Complaint email scheduler started. It will check every 1 minute.")