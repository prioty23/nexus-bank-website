import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


def is_email_enabled():
    return os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"


def send_email(to_email, subject, body):
    if not is_email_enabled():
        print("Email notification is disabled.")
        return False

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Eastern Bank PLC AI Assistant")

    if not smtp_host or not smtp_email or not smtp_password:
        print("SMTP settings are missing in .env")
        return False

    message = MIMEMultipart()
    message["From"] = f"{smtp_from_name} <{smtp_email}>"
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_email, smtp_password)
    server.send_message(message)
    server.quit()

    return True


def send_three_day_followup_email(to_email, complaint):
    subject = f"Complaint Follow-up - {complaint['complaint_id']}"

    body = (
        "Dear Customer,\n\n"
        "This is a follow-up regarding your Eastern Bank PLC complaint.\n\n"
        f"Complaint ID: {complaint['complaint_id']}\n"
        f"Issue Type: {complaint['issue_type']}\n"
        f"Current Status: {complaint['status']}\n"
        f"Created At: {complaint['created_at']}\n"
        f"Last Updated: {complaint['updated_at']}\n\n"
        "Your complaint is still under review. You will be notified again "
        "when the complaint is resolved or rejected.\n\n"
        #"For your security, please do not share OTP, PIN, password, CVV "
        #"or full card number through email.\n\n"
        "Regards,\n"
        "Eastern Bank PLC."
    )

    return send_email(to_email, subject, body)


def send_final_status_email(to_email, complaint):
    subject = f"Complaint Status Update - {complaint['complaint_id']}"

    body = (
        "Dear Customer,\n\n"
        "Your complaint status has been updated.\n\n"
        f"Complaint ID: {complaint['complaint_id']}\n"
        f"Issue Type: {complaint['issue_type']}\n"
        f"Current Status: {complaint['status']}\n"
        f"Created At: {complaint['created_at']}\n"
        f"Last Updated: {complaint['updated_at']}\n\n"
        "For your security, please do not share OTP, PIN, password, CVV "
        "or full card number through email.\n\n"
        "Regards,\n"
        "Eastern Bank PLC."
    )

    return send_email(to_email, subject, body)