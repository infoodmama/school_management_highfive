# SchoolPro - School Management System PRD

## Architecture
- Backend: FastAPI + MongoDB (Motor async) | Frontend: React 19 + Tailwind + Shadcn/UI
- Auth: Role-based (Admin/Teacher/Office Staff/Parent)
- WhatsApp: Custom API | PDF: ReportLab

## Credentials
- Admin: admin / 12345678 (all access)
- Teacher: teach1 / pass123 (students, attendance, calendar, homework)
- Parent: Set during student creation, login at /parent

## Role Access Matrix
- Admin: Dashboard, Classes, Students, Attendance, Fees, Expenses, Inventory, Calendar, Homework, Staff, Settings
- Teacher: Students, Attendance, Calendar, Homework
- Office Staff: Students, Fees, Expenses, Inventory
- Parent: Own child's attendance, fees, events, homework (at /parent)

## Implemented Features
- [x] Login system with role-based access control
- [x] Dashboard, Classes & Sections CRUD
- [x] Student CRUD (single/bulk CSV, promote, parent credentials)
- [x] Student Detail (attendance + fees + inventory issued)
- [x] Attendance (take/view, bulk mark, WhatsApp alerts, export)
- [x] Fee Management (term + custom fees, partial payment, max validation)
- [x] Payment popup dialog, transaction history with UPI screenshot popup (eye icon)
- [x] Invoice PDF generation & download
- [x] Fee Types with due dates, automated reminders
- [x] Expense Management, Inventory (inward + outward/issue to students)
- [x] Event Calendar, Homework (full CRUD)
- [x] Staff Management (teachers + office staff with login)
- [x] Parent Portal (login, attendance, fees, events, homework)
- [x] Settings (WhatsApp API, Database connection)
