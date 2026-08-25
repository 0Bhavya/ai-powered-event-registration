import logging
from typing import Optional
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_ticket_email(
        recipient_email: str,
        attendee_name: str,
        event_title: str,
        ticket_code: str,
        qr_file_path: Optional[str] = None
    ) -> bool:
        """
        Sends an email containing the event ticket and QR code.
        In demo mode, this just logs to the console to mock the email dispatch.
        """
        subject = f"Your Ticket for {event_title} is Confirmed!"
        body = f"""
        Dear {attendee_name},
        
        Thank you for registering for '{event_title}'. Your payment was successful and your ticket is attached.
        
        Ticket Code: {ticket_code}
        """
        
        # In a real scenario, integrate smtplib or a provider API like SendGrid here.
        # e.g., if not settings.demo_payment_mode: sendgrid.send(...)
        
        logger.info(f"--- MOCK EMAIL DISPATCH ---")
        logger.info(f"To: {recipient_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body.strip()}")
        if qr_file_path:
            logger.info(f"Attachment: [QR Code from {qr_file_path}]")
        logger.info(f"---------------------------")
        
        return True
