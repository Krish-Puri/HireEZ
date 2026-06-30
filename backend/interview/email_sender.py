"""
Email Service

Sends automated emails to candidates (test links, interview invitations).
Uses SMTP (Gmail or any provider).
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from backend.config import config


class EmailService:

    def _send(self, to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
        """
        Send an email via SMTP. Returns True on success, False on failure.
        """
        if not config.SMTP_USER or not config.SMTP_PASSWORD:
            print(f"[EmailService] SMTP not configured — would send to {to_email}: {subject}")
            return True  # Dev mode: log and continue

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config.EMAIL_FROM or config.SMTP_USER
        msg["To"] = to_email

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.sendmail(msg["From"], [to_email], msg.as_string())
            print(f"[EmailService] Sent email to {to_email}: {subject}")
            return True
        except Exception as e:
            print(f"[EmailService] Failed to send email to {to_email}: {e}")
            return False

    def send_test_link(
        self,
        to_email: str,
        candidate_name: str,
        test_link: str,
        job_title: Optional[str] = None,
    ) -> bool:
        """
        Send a test/assessment link to a shortlisted candidate.
        """
        subject = f"HireEZ: Your Assessment Link for {job_title or 'the Position'}"

        text_body = f"""
Hi {candidate_name},

Congratulations! You have been shortlisted for {job_title or "the position"} at our company.

Please complete the assessment by clicking the link below:
{test_link}

This link is personal to you and should not be shared.

Best regards,
HireEZ Recruitment Team
        """.strip()

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
    <h2>Congratulations, {candidate_name}! 🎉</h2>
    <p>You have been <strong>shortlisted</strong> for <strong>{job_title or 'the position'}</strong>.</p>
    <p>Please complete the assessment by clicking the button below:</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{test_link}" style="background-color: #4CAF50; color: white; padding: 14px 28px;
           text-decoration: none; border-radius: 5px; font-size: 16px;">
            Take Assessment
        </a>
    </div>
    <p style="color: #666; font-size: 12px;">
        This link is personal to you and should not be shared.<br>
        Complete the assessment at your earliest convenience.
    </p>
    <hr>
    <p style="color: #999; font-size: 12px;">Sent via HireEZ Recruitment Platform</p>
</body>
</html>
        """.strip()

        return self._send(to_email, subject, html_body, text_body)

    def send_interview_invitation(
        self,
        to_email: str,
        candidate_name: str,
        job_title: Optional[str],
        interview_link: str,
        interview_time_str: str,
        duration_minutes: int = 60,
    ) -> bool:
        """
        Send an interview invitation with a Google Meet link.
        """
        subject = f"HireEZ: Interview Invitation — {job_title or 'Position'}"

        text_body = f"""
Hi {candidate_name},

We are pleased to invite you to an interview for {job_title or 'the position'}.

📅 Date & Time: {interview_time_str}
⏱ Duration: {duration_minutes} minutes
🔗 Join: {interview_link}

Please join at the scheduled time using the link above.

Best regards,
HireEZ Recruitment Team
        """.strip()

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
    <h2>Interview Invitation 🎉</h2>
    <p>Hi <strong>{candidate_name}</strong>,</p>
    <p>We are pleased to invite you to an interview for <strong>{job_title or 'the position'}</strong>.</p>

    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <p style="margin: 5px 0;"><strong>📅 Date & Time:</strong> {interview_time_str}</p>
        <p style="margin: 5px 0;"><strong>⏱ Duration:</strong> {duration_minutes} minutes</p>
        <p style="margin: 5px 0;"><strong>🔗 Join:</strong> <a href="{interview_link}">{interview_link}</a></p>
    </div>

    <div style="text-align: center; margin: 30px 0;">
        <a href="{interview_link}" style="background-color: #4285F4; color: white; padding: 14px 28px;
           text-decoration: none; border-radius: 5px; font-size: 16px;">
            Join Google Meet
        </a>
    </div>

    <p>Please join at the scheduled time using the link above.</p>
    <hr>
    <p style="color: #999; font-size: 12px;">Sent via HireEZ Recruitment Platform</p>
</body>
</html>
        """.strip()

        return self._send(to_email, subject, html_body, text_body)


email_service = EmailService()
