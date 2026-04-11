# SchoolPro - School Management System PRD

## Original Problem Statement
School management system with modules: Student Management, Attendance Management, Fee Management, Inventory Management, Event Calendar, Homework. With updates for: Classes & Sections management, Custom fee types with due dates, Database connection settings, Partial payment, Student detail view, Fee reminders.

## Architecture
- **Backend**: FastAPI + MongoDB (Motor async driver)
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Database**: MongoDB (configurable via Settings page)
- **WhatsApp**: Custom API integration (crm.abhiit.com)

## What's Been Implemented (April 11, 2026)
- [x] Dashboard with stats
- [x] Classes & Sections CRUD with dropdown integration
- [x] Student Management (add single/bulk CSV, edit, delete, promote, filters)
- [x] Student Detail view with attendance history + fee status (paid/pending)
- [x] Attendance Management (take/view with dropdowns, bulk mark, WhatsApp alerts, export)
- [x] Fee Management (term fees + custom fees, partial payment with custom amount)
- [x] Fee Types CRUD (custom fees with class/section, notice/due dates)
- [x] Automated Fee Reminders via WhatsApp
- [x] Expense Management (with mandatory bill upload)
- [x] Inventory Management (item name, qty, category, purchase date, amount)
- [x] Event Calendar (monthly view with events)
- [x] Homework Management (class, section, subject, title, desc, due date, assigned by)
- [x] WhatsApp API Settings
- [x] Database Connection Settings
- [x] Student form focus bug FIX

## P1 (Next)
- Edit homework/events
- Attendance report generation (PDF)
- Parent login portal

## P2 (Future)
- Report card generation
- Multi-school support
- SMS fallback notifications
