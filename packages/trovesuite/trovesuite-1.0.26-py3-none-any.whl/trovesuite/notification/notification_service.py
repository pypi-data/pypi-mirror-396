import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..entities.sh_response import Respons
from .notification_read_dto import (
    NotificationEmailServiceReadDto,
    NotificationSMSServiceReadDto
)
from .notification_write_dto import (
    NotificationEmailServiceWriteDto,
    NotificationSMSServiceWriteDto
)

class NotificationService:

    @staticmethod
    def send_email(data: NotificationEmailServiceWriteDto) -> Respons[NotificationEmailServiceReadDto]:
        """
        Send an email (single or multiple recipients) via Gmail SMTP.
        Supports both plain text and HTML email bodies.
        """

        # Extract input data
        receiver_email = data.receiver_email
        text_message = data.text_message
        html_message = getattr(data, "html_message", None)
        sender_email = data.sender_email
        password = data.password
        subject = data.subject

        # Allow single email or list
        if isinstance(receiver_email, str):
            receiver_email = [receiver_email]

        # Create the email container
        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)
        message["Subject"] = subject

        # Attach plain text
        message.attach(MIMEText(text_message, "plain"))

        # Attach HTML if provided
        if html_message:
            message.attach(MIMEText(html_message, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())

            return Respons[NotificationEmailServiceReadDto](
                detail=f"Email successfully sent to {len(receiver_email)} recipient(s)",
                error=None,
                data=[],
                status_code=200,
                success=True,
            )

        except Exception as e:
            print(e)
            return Respons[NotificationEmailServiceReadDto](
                detail="An error occurred while sending the email",
                error=str(e),
                data=[],
                status_code=500,
                success=False,
            )

    @staticmethod
    def send_sms(data: NotificationSMSServiceWriteDto) -> Respons[NotificationSMSServiceReadDto]:
        pass
