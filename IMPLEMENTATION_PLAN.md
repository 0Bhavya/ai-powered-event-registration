# Implementation Plan

Based on the audit of the existing deployed application, the following implementation plan prioritizes the missing, mocked, and partially implemented features to bring the system to 100% flowchart coverage and production readiness.

## Priority 0 (P0) — Critical Functionality / Security
1. **Real Payment Integration Fixes:**
   - Ensure the Razorpay frontend checkout script is fully wired into `events.html` and `dashboard.html`.
   - Remove any hardcoded bypasses unless `DEMO_MODE` is strictly enabled.

## Priority 1 (P1) — End-to-End Flow
1. **Feedback & Sentiment Analysis API:**
   - Create `app/api/feedback.py`.
   - Implement `TextBlob` sentiment analysis on feedback submission.
   - Save the sentiment score and text to the `Feedback` model.
2. **Real Notifications:**
   - Update `app/services/notification_service.py` to actually dispatch emails (e.g., using `smtplib` or an async HTTP client for SendGrid), reading credentials from `.env`.

## Priority 2 (P2) — UI/UX
1. **User Dashboard Completion:**
   - Wire `static/js/main.js` to fetch and render the user's purchased tickets (including the QR code image) from the backend.
2. **Staff Scanner UI:**
   - Create a frontend interface for Staff to input/scan the QR token and hit the `/api/attendance/scan` endpoint.

## Priority 3 (P3) — Analytics
1. **Admin Analytics API:**
   - Refactor `/api/stats` in `app/main.py`.
   - Query the real database to aggregate `total_registrations`, `total_events`, `attendance_rate`, and `average_sentiment`.
2. **Admin Dashboard UI:**
   - Wire the frontend Admin Dashboard to consume the real `/api/stats` and display the `AdminAuditLog` records dynamically.

## Priority 4 (P4) — Optimization / Polish / Tests
1. **Comprehensive Test Suite:**
   - Convert `scripts/test_advanced.py` into proper `pytest` files in the `tests/` directory.
   - Add unit tests for the ML Fraud Detector and Ticket generation.
2. **Cleanup Deployment Files:**
   - Delete `vercel.json` to prevent deployment confusion, as Render is the chosen infrastructure.
