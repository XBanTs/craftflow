# craftflow_config/email_backend.py
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, HtmlContent

logger = logging.getLogger(__name__)


class SendGridAPIEmailBackend(BaseEmailBackend):
    """
    Sends emails via SendGrid Web API (HTTPS).
    Works on Render's free tier where SMTP ports are blocked.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = settings.SENDGRID_API_KEY
        if not api_key:
            logger.error("SENDGRID_API_KEY not set. Cannot send emails.")
            return 0

        sg = SendGridAPIClient(api_key)
        sent_count = 0

        for message in email_messages:
            try:
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    plain_text_content=message.body,
                )

                # Attach HTML alternative if available
                if hasattr(message, 'alternatives'):
                    for content, mime_type in message.alternatives:
                        if mime_type == 'text/html':
                            mail.html_content = HtmlContent(content)
                            break

                response = sg.send(mail)

                if response.status_code in [200, 201, 202]:
                    sent_count += 1
                else:
                    logger.error(
                        f"SendGrid API error: {response.status_code} – {response.body}"
                    )
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid API: {e}")
                continue

        return sent_count