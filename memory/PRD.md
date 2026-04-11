# SchoolPro - School Management System PRD

## Original Problem Statement
School management system with modules: Student Management, Attendance Management, Fee Management, Inventory Management, Event Calendar, Homework. With updates for: Classes & Sections management, Custom fee types with due dates, Database connection settings.

## Architecture
- **Backend**: FastAPI + MongoDB (Motor async driver)
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Database**: MongoDB (configurable via Settings page)
- **WhatsApp**: Custom API integration (crm.abhiit.com)

## User Personas
- School Admin / Office Staff: Manages students, takes attendance, collects fees
- Principal: Views dashboard stats, manages classes

## Core Requirements
1. Student Management (add single/bulk, view/edit/delete, promote)
2. Attendance Management (take/view, WhatsApp alerts for absent)
3. Fee Management (term fees + custom fees, UPI/Cash, day sheet, export)
4. Expense Management (add expenses with mandatory bill upload)
5. Classes & Sections management (used in all dropdowns)
6. Custom Fee Types with notice dates and due dates
7. Database Connection settings (connect own MongoDB)
8. WhatsApp API settings (custom endpoint)

## What's Been Implemented (April 11, 2026)
- [x] Dashboard with stats (Total Students, Present Today, Absent Today, Fees Collected)
- [x] Classes & Sections CRUD with dropdown integration
- [x] Student Management (add single, bulk CSV, edit, delete, promote, filters)
- [x] Attendance Management (take/view with dropdowns, bulk mark, WhatsApp alerts, export CSV/Excel)
- [x] Fee Management (term fees + custom fees, UPI/Cash with screenshot upload, day sheet, export)
- [x] Fee Types CRUD (custom fees with class/section, notice start date, due date)
- [x] Expense Management (add with mandatory bill upload, date filters)
- [x] WhatsApp API Settings page
- [x] Database Connection Settings (test connection before switching)

## P0/P1/P2 Features Remaining
### P1 (Next Phase)
- Inventory Management module
- Event Calendar module
- Homework module
- Student attendance percentage on individual student profile

### P2 (Future)
- Parent login portal
- Report card generation
- Automated fee reminders
- SMS notifications backup
- Multi-school support

## Next Tasks
1. Implement Inventory Management module
2. Build Event Calendar with Shadcn Calendar
3. Create Homework module (assign/view/submit)
4. Add student detail view with complete attendance history
