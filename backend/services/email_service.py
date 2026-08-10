"""
Email Service

Sends test links and interview invitations via SMTP.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config import config


def _send_email(to_email: str, subject: str, html_body: str, plain_body: str = "") -> bool:
    """Low-level SMTP send. Returns True on success, False on failure."""
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        print(f"[EMAIL] SMTP not configured — skipping email to {to_email}")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = config.EMAIL_FROM or config.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())
        print(f"[EMAIL] Sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] Authentication failed for {to_email}: {e}. Check your SMTP_PASSWORD (App Password, not your Google password)")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL] SMTP error sending to {to_email}: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL] Failed to send to {to_email}: {e}")
        return False


def _send_test_link_impl(to_email: str, candidate_name: str, test_link: str) -> bool:
    """Send a test link to a shortlisted candidate."""
    subject = "HireEZ: Your Assessment Test Link"

    plain_body = f"""
Hi {candidate_name},

Congratulations! You have been shortlisted for the next stage of our hiring process.

Please complete the assessment using the link below:
{test_link}

Best of luck!

Regards,
HireEZ Hiring Team
""".strip()

    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #0d1117; color: #e6edf3; padding: 40px;">
  <div style="max-width: 600px; margin: auto; background: #161b22; border-radius: 8px; padding: 32px; border: 1px solid #30363d;">
    <h2 style="color: #58a6ff;">🎉 Congratulations, {candidate_name}!</h2>
    <p>You have been <strong>shortlisted</strong> for the next stage of our hiring process.</p>
    <p>Please complete your assessment using the link below:</p>
    <div style="text-align: center; margin: 32px 0;">
      <a href="{test_link}" style="background-color: #238636; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: bold;">Take Assessment</a>
    </div>
    <p style="color: #8b949e; font-size: 13px;">Or copy this link: {test_link}</p>
    <hr style="border-color: #30363d;">
    <p style="color: #8b949e; font-size: 13px;">Best of luck! — <em>HireEZ Hiring Team</em></p>
  </div>
</body>
</html>
"""

    return _send_email(to_email, subject, html_body, plain_body)


def _send_interview_invite_impl(
    to_email: str,
    candidate_name: str,
    interview_link: str,
    interview_time: str,
) -> bool:
    """Send a Google Meet interview invitation to a candidate."""
    subject = "HireEZ: Your Interview Invitation"

    plain_body = f"""
Hi {candidate_name},

You have been invited for an interview.

Date & Time: {interview_time}
Meeting Link: {interview_link}

Join using the link above at the scheduled time.

Best regards,
HireEZ Hiring Team
""".strip()

    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #0d1117; color: #e6edf3; padding: 40px;">
  <div style="max-width: 600px; margin: auto; background: #161b22; border-radius: 8px; padding: 32px; border: 1px solid #30363d;">
    <h2 style="color: #58a6ff;">📅 Interview Invitation</h2>
    <p>Hi <strong>{candidate_name}</strong>,</p>
    <p>You have been invited for an interview. Please find the details below:</p>
    <table style="background: #0d1117; border-radius: 6px; padding: 16px; margin: 24px 0; width: 100%;">
      <tr><td style="padding: 8px 0; color: #8b949e;">Date & Time</td><td style="padding: 8px 0; font-weight: bold;">{interview_time}</td></tr>
      <tr><td style="padding: 8px 0; color: #8b949e;">Meeting Link</td><td style="padding: 8px 0;"><a href="{interview_link}" style="color: #58a6ff;">Join Google Meet</a></td></tr>
    </table>
    <div style="text-align: center; margin: 32px 0;">
      <a href="{interview_link}" style="background-color: #1f6feb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: bold;">Join Interview</a>
    </div>
    <hr style="border-color: #30363d;">
    <p style="color: #8b949e; font-size: 13px;">Best regards — <em>HireEZ Hiring Team</em></p>
  </div>
</body>
</html>
"""

    return _send_email(to_email, subject, html_body, plain_body)


class EmailService:
    def send_test_link(self, to_email: str, candidate_name: str, test_link: str) -> bool:
        return _send_test_link_impl(to_email, candidate_name, test_link)

    def send_interview_invite(self, to_email: str, candidate_name: str, interview_link: str, interview_time: str) -> bool:
        return _send_interview_invite_impl(to_email, candidate_name, interview_link, interview_time)


email_service = EmailService()