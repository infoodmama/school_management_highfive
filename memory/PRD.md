# SchoolPro - School Management System PRD

## Credentials
- Super Admin: admin / 12345678
- Teacher: teach1 / pass123
- Parent: Set during student creation, login at /parent (e.g., ali / 123456 for studentCode 4543)

## WhatsApp Templates Configured
- fee_paid_bill: Invoice PDF + amount + fee name + student name
- absent_hifg: Student name + class + date
- holi: Event name + date

## Role-Based Access (Updated 2026-02-28)
- super_admin: Everything including Settings
- admin_role: Everything except Settings (incl. Approvals: Leave + Concessions)
- teacher: Students, Attendance, Calendar, Homework, Approvals (Leave ONLY, no Concessions tab)
- office_staff: Students, Fees, Expenses, Inventory

## All Implemented Features
- Login with role-based access (Admin/Teacher/Office Staff/Super Admin)
- Dashboard, Classes & Sections, Student CRUD (single/bulk/promote/parent credentials)
- Student Detail (attendance + fees + inventory)
- Attendance (take/view, bulk mark, WhatsApp absent alerts via template)
- Fee Management (term + custom, partial payment, max validation, payment popup dialog)
- Fee Status Report (class/section wise, all terms + custom, export)
- Transaction History with UPI screenshot popup (eye icon) + Invoice PDF download + Revert
- Fee Types with due dates, automated reminders
- Concessions (single + **bulk** — comma/newline separated student IDs)
- Expense Management, Inventory (inward + outward/issue to students)
- Event Calendar with WhatsApp notification checkbox
- Homework (full CRUD with file attachments), Staff Management with login
- Parent Portal (Overview, Attendance, Fees, Events, Homework, **Leave**)
- **Approvals Page** — Unified Leave + Concessions admin page with status filter, role-aware tabs
- **Leave Requests** — Parents submit via portal, Admins/Teachers approve/reject
- **Student Promotion with Fee Carryover** — ALL pending dues (T1+T2+T3 unpaid) roll into Term 1 of new class; Terms 2 & 3 reset to original fresh-year values
- Settings (WhatsApp phoneNumberId + token, Database connection, School profile)
- Connected to external MongoDB: 38.242.216.156 / school_management

## CHANGELOG

### 2026-02-28 (this fork)
- **Backend**
  - Fixed orphaned code in `send_fee_reminders` (broken due to concession-routes injection)
  - `promote_students` now puts ALL pending dues into new Term 1 only; Terms 2 & 3 keep fresh-year values; stores `previousYearDues` metadata on each student
  - Added `POST /api/concessions/bulk` accepting `studentCodes[]`, returns `{created, students, errors}`
  - Added `LeaveRequest` / `LeaveRequestCreate` models
  - Added `POST /api/leave-requests`, `GET /api/leave-requests` (filter by status/studentId/studentClass/section), `POST /{id}/approve`, `POST /{id}/reject`
- **Frontend**
  - New page `/approvals` (Approvals.js) with Leave + Concessions tabs; teacher sees Leave-only
  - ParentPortal gained a **Leave** tab — date range + reason + optional file upload + history list
  - Fees → Concessions tab now has Single/Bulk mode toggle; history card limited to last 4 records with tip to visit Approvals
  - AuthContext, Layout, App routes updated to expose `/approvals`
  - api.js extended with leave-requests + bulk concession helpers
  - Added `data-testid="parent-tab-{key}"` on Parent Portal tab buttons
- **Testing** — 100% pass on `iteration_10.json` (20/20 backend pytest + 3/3 frontend e2e flows)

### Earlier
- Custom PDF invoices (High Five International design) with sequential receipts
- External MongoDB integration
- Fee revert functionality
- Homework & Event file uploads
- Bulk student delete + pagination

## Prioritized Backlog
- **P2 — Refactor** `server.py` (~1586 lines) into routers: `/routes/students.py`, `/routes/fees.py`, `/routes/attendance.py`, etc.
- **P2 — Security** Add JWT/session auth tokens with route validation (currently role-based trust only)
- **P3** — Auto-mark attendance as `leave` when a leave request is approved (deferred per user: teacher still marks manually)
- **P3** — Concession bulk: checkbox selection from student list UI (current: paste student IDs textarea)
