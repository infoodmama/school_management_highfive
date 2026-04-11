# SchoolPro - School Management System PRD

## Architecture
- Backend: FastAPI + MongoDB (Motor async) | Frontend: React 19 + Tailwind + Shadcn/UI
- WhatsApp: Custom API (crm.abhiit.com) | PDF: ReportLab

## Implemented Features (April 11, 2026)
- [x] Dashboard, Classes & Sections CRUD
- [x] Student CRUD (single/bulk CSV, promote, parent login credentials)
- [x] Student Detail View (attendance + fees + inventory issued)
- [x] Attendance (take/view, bulk mark, WhatsApp alerts, CSV/Excel export)
- [x] Fee Management (term + custom fees, partial payment, custom amount with max validation)
- [x] Transaction History with UPI screenshots and Invoice PDF download
- [x] Fee Types (custom fees with class/section, notice/due dates)
- [x] Automated Fee Reminders via WhatsApp
- [x] Expense Management (mandatory bill upload)
- [x] Inventory (inward + outward/issue to students, stock deduction)
- [x] Event Calendar (monthly grid, CRUD)
- [x] Homework (assign with class/section/subject, CRUD, overdue detection)
- [x] Staff Management (teachers + office staff with login credentials)
- [x] Parent Portal (/parent - login with credentials, view attendance/fees/events/homework)
- [x] Settings (WhatsApp API, Database connection)

## Next Tasks
- Report card generation (PDF)
- Multi-school support
- SMS fallback notifications
- Salary/payroll for staff
