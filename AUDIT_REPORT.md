# Audit Report: AI-Powered Event Registration System

## Current Architecture
The system is built as a monolithic full-stack application using FastAPI (Python 3.12+).
- **Backend:** FastAPI, SQLAlchemy (ORM), Alembic (Migrations), Pydantic (Validation).
- **Database:** PostgreSQL.
- **Frontend:** Server-side rendered HTML using Jinja2 Templates, Vanilla JS, and Custom CSS (Glassmorphism design).
- **Deployment:** Configured for Render via `render.yaml` using Gunicorn and Uvicorn workers. Vercel deployment metadata is also present (`vercel.json`) but lacks the database component.

## Working Features
- **Authentication (JWT):** Argon2 hashing, RBAC (Admin, Staff, User).
- **Event Management:** Admin CRUD for events. 
- **Registration (Row-Level Locking):** Prevents race conditions and double-booking during high concurrency.
- **Fraud Detection:** Advanced `IsolationForest` ML model trained to detect bot-like rapid registration behavior, supplemented by heuristic checks (disposable emails).
- **QR Code Generation:** Secure generation and validation of ticket QR codes.
- **Attendance Scanner:** Staff can scan tickets. The system prevents double check-ins.
- **Audit Logging:** System automatically records admin/staff actions securely to `AdminAuditLog`.

## Partially Working Features
- **Payments (Razorpay):** API endpoints exist and verify signatures correctly, but it relies on a local `DEMO_MODE` flag and mock signatures in some tests. 
- **Notifications (Emails):** Background tasks fire successfully after a payment is confirmed, but the actual SMTP/SendGrid implementation is mocked out (logging to terminal).

## Missing Features
- **Feedback & Sentiment Analysis:** The database model `Feedback` exists, but there are no API endpoints to submit feedback, nor is there any TextBlob sentiment analysis logic hooked up.
- **Frontend Admin Analytics:** The frontend dashboard for admins relies on a mocked API endpoint (`/api/stats`).
- **User Dashboard UI:** Users can't actually view their generated tickets easily from a frontend gallery (needs UI verification).

## Bugs
- **None explicitly identified** during standard flow, but the lack of comprehensive automated tests leaves edge cases untested.

## Security Issues
- **None critical.** Row-level locking is used for seats, Argon2 for hashing, and JWT for sessions. However, the Razorpay webhook verification might need hardening if exposed publicly without IP whitelisting.

## Database Issues
- **None.** Migrations are managed well via Alembic, and `render.yaml` handles migrations on deployment securely.

## API Issues
- The `/api/stats` endpoint is hardcoded to return fake data (`"total_registrations": 10247`, etc.).

## UI/UX Issues
- The user dashboard and admin panels are mostly static templates that need fully dynamic JS wiring to their respective robust backend APIs.

## Deployment Issues
- Render free tier drops connection after 15 minutes of inactivity (Cold Starts).
- Vercel config (`vercel.json`) exists but cannot be used without a standalone PostgreSQL provider (like Neon).

## Flowchart Coverage

| Flowchart Stage | Backend | Frontend | Database | Tested | Status |
|---|---|---|---|---|---|
| 1. Authentication | Yes | Yes | Yes | Manual | ✅ Working |
| 2. Event Discovery | Yes | Yes | Yes | Manual | ✅ Working |
| 3. Registration (Concurrency) | Yes | Yes | Yes | Script | ✅ Working |
| 4. Fraud Detection (ML) | Yes | No | Yes | Script | ✅ Working |
| 5. Payment (Razorpay) | Yes | No | Yes | Script | ⚠️ Partially Mapped |
| 6. Ticket / QR Generation | Yes | Yes | Yes | Script | ✅ Working |
| 7. Check-in (Attendance) | Yes | No | Yes | Script | ✅ Working |
| 8. Post-Event Feedback | No | No | Yes | No | ❌ Missing |
| 9. Admin Analytics | Mocked | No | No | No | ❌ Missing |
