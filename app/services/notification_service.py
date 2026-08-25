import logging
import smtplib
from email.message import EmailMessage
from typing import Optional
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.notification import Notification
from app.database.session import SessionLocal

settings = get_settings()
logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_ticket_email(
        user_id: int,
        registration_id: int,
        recipient_email: str,
        attendee_name: str,
        event_title: str,
        ticket_code: str,
        qr_file_path: Optional[str] = None
    ) -> bool:
        """
        Sends an email containing the event ticket and QR code.
        Falls back to demo mode (console logging) if credentials are not provided.
        """
        subject = f"Your Ticket for {event_title} is Confirmed!"
        body = f"""
        Dear {attendee_name},
        
        Thank you for registering for '{event_title}'. Your payment was successful and your ticket is attached.
        
        Ticket Code: {ticket_code}
        """
        
        # Check if we should use real SMTP
        use_smtp = all([
            not settings.demo_payment_mode,
            settings.smtp_server,
            settings.smtp_username,
            settings.smtp_password
        ])
        
        if use_smtp:
            try:
                msg = EmailMessage()
                msg.set_content(body.strip())
                msg['Subject'] = subject
                msg['From'] = settings.smtp_from_email
                msg['To'] = recipient_email
                
                # Attach QR if exists
                if qr_file_path:
                    try:
                        with open(qr_file_path, 'rb') as f:
                            img_data = f.read()
                        msg.add_attachment(img_data, maintype='image', subtype='png', filename='ticket_qr.png')
                    except Exception as e:
                        logger.warning(f"Could not attach QR code: {e}")
                        
                with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                    server.starttls()
                    server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg)
                    
                logger.info(f"Ticket email sent successfully to {recipient_email}")
                status_val = "SENT"
                success = True
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                status_val = "FAILED"
                success = False
                
            db = SessionLocal()
            try:
                notif = Notification(
                    user_id=user_id,
                    registration_id=registration_id,
                    type="TICKET_CONFIRMATION",
                    recipient=recipient_email,
                    status=status_val
                )
                db.add(notif)
                db.commit()
            finally:
                db.close()
                
            return success
        else:
            # Fallback to mock logging
            logger.info(f"--- MOCK EMAIL DISPATCH ---")
            logger.info(f"To: {recipient_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body.strip()}")
            if qr_file_path:
                logger.info(f"Attachment: [QR Code from {qr_file_path}]")
            logger.info(f"---------------------------")
            
            
            db = SessionLocal()
            try:
                notif = Notification(
                    user_id=user_id,
                    registration_id=registration_id,
                    type="TICKET_CONFIRMATION_MOCK",
                    recipient=recipient_email,
                    status="SENT"
                )
                db.add(notif)
                db.commit()
            finally:
                db.close()
                
            return True
