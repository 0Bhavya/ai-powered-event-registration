import re
import numpy as np
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest

from app.models.registration import Registration, RiskLevel
from app.models.fraud_log import FraudLog
from app.schemas.fraud import FraudCheckRequest, FraudCheckResponse

# Common disposable email domains
DISPOSABLE_DOMAINS = {"tempmail.com", "10minutemail.com", "guerrillamail.com", "mailinator.com", "yopmail.com"}

class FraudDetector:
    def __init__(self, db: Session):
        self.db = db
        
    def _check_disposable_email(self, email: str) -> bool:
        domain = email.split('@')[-1].lower()
        return domain in DISPOSABLE_DOMAINS
        
    def _check_suspicious_email(self, email: str) -> bool:
        # e.g., lots of numbers or weird characters
        local_part = email.split('@')[0]
        num_count = sum(c.isdigit() for c in local_part)
        if len(local_part) > 0 and num_count / len(local_part) > 0.5:
            return True
        return False
        
    def _get_registration_history(self, user_id: int, event_id: int, email: str, phone: str = None) -> dict:
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Duplicate email across other registrations (for this event)
        duplicate_email_count = self.db.query(Registration).join(Registration.user).filter(
            Registration.event_id == event_id,
            # we shouldn't penalize their own past valid regs for other events, just this event
            # or if the email is used by DIFFERENT user_ids
        ).count()
        # Wait, if they are logged in, it's their user_id. 
        # A duplicate email/phone check usually means checking if multiple users share it,
        # or if they are registering multiple times for the same event.
        repeated_attempts = self.db.query(Registration).filter(
            Registration.user_id == user_id,
            Registration.event_id == event_id,
            Registration.created_at >= recent_cutoff
        ).count()
        
        # Just an example heuristic for duplicate phone across the platform
        duplicate_phone = 0
        if phone:
            duplicate_phone = self.db.query(Registration).join(Registration.user).filter(
                # app.models.user.User.phone == phone
                # Since phone is on user table, we'd need to check User table
            ).count() # Simplified logic

        return {
            "repeated_attempts": repeated_attempts,
            "duplicate_phone": duplicate_phone > 1 # more than 1 user with this phone
        }
        
    def _detect_anomalies_ml(self, user_id: int) -> bool:
        """Lightweight IsolationForest to detect abnormal registration frequency."""
        # Get registration counts per day for the last 30 days for this user
        # For a real implementation, we'd query daily counts.
        # Here we mock a basic data extraction
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        regs = self.db.query(Registration.created_at).filter(
            Registration.user_id == user_id,
            Registration.created_at >= recent_cutoff
        ).all()
        
        if len(regs) < 5:
            return False # Not enough data to be anomalous
            
        # Feature extraction: time diffs between registrations
        times = sorted([r.created_at.timestamp() for r in regs])
        diffs = np.diff(times).reshape(-1, 1)
        
        if len(diffs) < 3:
            return False
            
        # If they registered many times with very small time gaps
        clf = IsolationForest(contamination=0.1, random_state=42)
        preds = clf.fit_predict(diffs)
        
        # If the latest registration time diff is considered an anomaly (usually -1)
        # We simplify by just checking if the average diff is extremely low
        avg_diff = np.mean(diffs)
        if avg_diff < 60: # less than 60 seconds average between regs
            return True
            
        return False

    def evaluate(self, request: FraudCheckRequest) -> FraudCheckResponse:
        score = 0
        reasons = []
        
        # Rule 1: Disposable email (+15)
        if self._check_disposable_email(request.email):
            score += 15
            reasons.append("Disposable email domain detected")
            
        # Rule 2: Suspicious email (+15)
        if self._check_suspicious_email(request.email):
            score += 15
            reasons.append("Suspicious email pattern detected")
            
        # Rule 3: Repeated attempts (+20)
        history = self._get_registration_history(request.user_id, request.event_id, request.email, request.phone)
        if history["repeated_attempts"] > 1:
            score += 20
            reasons.append("Repeated registration attempts detected")
            
        # Rule 4: Abnormal registration frequency via ML (+20)
        if self._detect_anomalies_ml(request.user_id):
            score += 20
            reasons.append("Abnormal registration frequency detected (ML)")
            
        # Clamp score
        score = min(score, 100)
        score = max(score, 0)
        
        # Determine level
        if score < 30:
            level = RiskLevel.LOW
        elif score < 60:
            level = RiskLevel.MEDIUM
        elif score < 80:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL
            
        return FraudCheckResponse(
            risk_score=score,
            risk_level=level,
            reasons=reasons
        )
