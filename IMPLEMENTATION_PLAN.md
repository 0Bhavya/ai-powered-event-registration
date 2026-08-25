# Implementation Plan

This plan prioritizes stabilizing the production environment, fixing E2E gaps (specifically the missing feedback UI), and expanding the test suite.

## P0 — Security/data-loss/runtime issues
*No critical P0 issues found affecting the immediate runtime stability.*

## P1 — Broken end-to-end workflow

### 1. Implement User Feedback UI
- **Problem:** The backend fully supports TextBlob sentiment analysis (`/api/feedback`), but attendees have no way to access this from the browser.
- **Files Affected:** `templates/dashboard.html`, `static/js/main.js`.
- **Proposed Solution:** Add a "Submit Feedback" button next to past/attended events on the user dashboard. Open a modal to capture a 1-5 rating and comment, and POST to `/api/feedback`.
- **Dependencies:** None.
- **Acceptance Criteria:** A user can successfully submit a review from their dashboard, and the resulting sentiment score dynamically updates the Admin Analytics page.

## P2 — Missing flowchart functionality

### 1. Granular Admin Event Management
- **Problem:** Admins cannot edit, delete, or cleanly browse individual events via the UI.
- **Files Affected:** `templates/admin.html`, `app/main.py`.
- **Proposed Solution:** Build a dedicated `/admin/events` page with a table to perform CRUD operations on the `Event` model.
- **Dependencies:** `/api/events` backend routes.
- **Acceptance Criteria:** Admins can create and delete events natively from the UI without relying on the generic "Create Demo Event" button.

## P3 — UI/UX and animations

### 1. Event Details Page
- **Problem:** Users register via a modal; they cannot view an expanded page for an event.
- **Files Affected:** `app/main.py`, `templates/event_detail.html`.
- **Proposed Solution:** Implement `/events/{id}` serving a detailed Jinja2 template.
- **Dependencies:** Frontend design alignment.
- **Acceptance Criteria:** Clicking an event card directs the user to a dedicated SEO-friendly details page.

## P4 — Analytics/polish

### 1. Formalize Pytest Suite
- **Problem:** 90% of the backend features (Payments, ML, JWT) are tested via ad-hoc `.py` scripts instead of the formal `pytest` suite.
- **Files Affected:** `tests/test_auth.py`, `tests/test_registrations.py`, `tests/test_fraud.py`.
- **Proposed Solution:** Port all logic from `scripts/test_p1.py` and `scripts/test_p2p3.py` into formal asynchronous `pytest` files using `TestClient`.
- **Dependencies:** None.
- **Acceptance Criteria:** `pytest -v` executes the entire e2e workflow and reports 20+ passing tests.

## P5 — Production/Vercel readiness

### 1. Clean Deployment Artifacts
- **Problem:** The repository contains unused `vercel.json` configurations which confuse developers about the infrastructure platform.
- **Files Affected:** `vercel.json`.
- **Proposed Solution:** Delete `vercel.json`.
- **Dependencies:** None.
- **Acceptance Criteria:** Only `render.yaml` remains as the source of truth for IaC deployment.
