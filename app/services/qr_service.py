import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from typing import Optional
from pathlib import Path

from app.config import get_settings

settings = get_settings()

class QRService:
    def __init__(self):
        self.base_url = settings.app_url
        self.qr_dir = settings.static_dir / "images" / "qr"
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_qr_code(self, qr_token: str, ticket_code: str) -> str:
        """
        Generates a QR code encoding the verification URL and saves it to static files.
        Returns the relative path to the image.
        """
        verification_url = f"{self.base_url}/verify-ticket/{qr_token}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage, 
            module_drawer=RoundedModuleDrawer()
        )
        
        filename = f"{ticket_code}_{qr_token[:8]}.png"
        filepath = self.qr_dir / filename
        
        img.save(filepath)
        
        # Return relative URL path for DB storage
        return f"/static/images/qr/{filename}"
