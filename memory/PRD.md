# SchoolPro - School Management System PRD

## Credentials
- Admin: admin / 12345678
- Teacher: teach1 / pass123
- Parent: Set during student creation, login at /parent

## WhatsApp Templates Configured
- fee_paid_bill: Invoice PDF + amount + fee name + student name
- absent_hifg: Student name + class + date  
- holi: Event name + date

## All Implemented Features
- Login with role-based access (Admin/Teacher/Office Staff)
- Dashboard, Classes & Sections, Student CRUD (single/bulk/promote/parent credentials)
- Student Detail (attendance + fees + inventory)
- Attendance (take/view, bulk mark, WhatsApp absent alerts via template)
- Fee Management (term + custom, partial payment, max validation, payment popup dialog)
- Fee Status Report (class/section wise, all terms + custom, export)
- Transaction History with UPI screenshot popup (eye icon) + Invoice PDF download
- Fee Types with due dates, automated reminders
- Expense Management, Inventory (inward + outward/issue to students)
- Event Calendar with WhatsApp notification checkbox
- Homework (full CRUD), Staff Management with login
- Parent Portal (attendance, fees, events, homework)
- Settings (WhatsApp phoneNumberId + token, Database connection)
- Connected to external MongoDB: 38.242.216.156 / school_management
