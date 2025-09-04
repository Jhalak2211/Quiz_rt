import smtplib
from email.mime.text import MIMEText
from config import Config

def send_quiz_link(to_email: str, candidate_name: str, link: str) -> tuple[bool, str]:
    body = f"""Hi {candidate_name},

Your quiz is ready. Please click the link below to start:
{link}

You have 5 minutes to complete 5 questions. Good luck!

Thanks,
HR Team
"""

    msg = MIMEText(body)
    msg["Subject"] = "Your Quiz Link"
    msg["From"] = Config.SMTP_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, str(e)
