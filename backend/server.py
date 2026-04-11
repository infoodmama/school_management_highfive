from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import csv
import io
from openpyxl import Workbook
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class ClassSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    className: str
    sections: List[str]
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClassSectionCreate(BaseModel):
    className: str
    sections: List[str]

class FeeType(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    feeName: str
    amount: float
    applicableClass: Optional[str] = None
    applicableSection: Optional[str] = None
    noticeStartDate: Optional[str] = None
    dueDate: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeeTypeCreate(BaseModel):
    feeName: str
    amount: float
    applicableClass: Optional[str] = None
    applicableSection: Optional[str] = None
    noticeStartDate: Optional[str] = None
    dueDate: Optional[str] = None

class DatabaseSettings(BaseModel):
    mongoUrl: str
    dbName: str

class Student(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    studentName: str
    rollNo: str
    studentClass: str
    section: str
    fatherName: str
    motherName: str
    mobile: str
    address: str
    feeTerm1: float
    feeTerm2: float
    feeTerm3: float
    parentUsername: Optional[str] = None
    parentPassword: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudentCreate(BaseModel):
    studentName: str
    rollNo: str
    studentClass: str
    section: str
    fatherName: str
    motherName: str
    mobile: str
    address: str
    feeTerm1: float
    feeTerm2: float
    feeTerm3: float
    parentUsername: Optional[str] = None
    parentPassword: Optional[str] = None

class StudentUpdate(BaseModel):
    studentName: Optional[str] = None
    rollNo: Optional[str] = None
    studentClass: Optional[str] = None
    section: Optional[str] = None
    fatherName: Optional[str] = None
    motherName: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    feeTerm1: Optional[float] = None
    feeTerm2: Optional[float] = None
    feeTerm3: Optional[float] = None
    parentUsername: Optional[str] = None
    parentPassword: Optional[str] = None

class AttendanceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    studentId: str
    rollNo: str
    studentName: str
    studentClass: str
    section: str
    date: str
    status: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AttendanceSubmit(BaseModel):
    studentClass: str
    section: str
    date: str
    records: List[Dict]

class FeePayment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    studentId: str
    rollNo: str
    studentName: str
    termNumber: Optional[int] = None
    feeTypeId: Optional[str] = None
    feeName: Optional[str] = None
    amount: float
    paymentMode: str
    upiScreenshot: Optional[str] = None
    receiptNumber: str
    paymentDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeePaymentCreate(BaseModel):
    studentId: str
    rollNo: str
    studentName: str
    termNumber: Optional[int] = None
    feeTypeId: Optional[str] = None
    feeName: Optional[str] = None
    amount: float
    paymentMode: str
    upiScreenshot: Optional[str] = None

class Expense(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    expenseName: str
    amount: float
    date: str
    billUrl: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExpenseCreate(BaseModel):
    expenseName: str
    amount: float
    date: str
    billUrl: str

class WhatsAppSettings(BaseModel):
    apiUrl: str
    accessToken: str

class PromoteRequest(BaseModel):
    fromClass: str
    toClass: str

class InventoryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itemName: str
    quantity: int
    category: str
    purchaseDate: str
    amount: float
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InventoryItemCreate(BaseModel):
    itemName: str
    quantity: int
    category: str
    purchaseDate: str
    amount: float

class InventoryIssue(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itemId: str
    itemName: str
    studentId: str
    rollNo: str
    studentName: str
    quantity: int
    date: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InventoryIssueCreate(BaseModel):
    itemId: str
    rollNo: str
    quantity: int
    date: str

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    date: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventCreate(BaseModel):
    title: str
    description: str
    date: str

class Homework(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    studentClass: str
    section: str
    subject: str
    title: str
    description: str
    dueDate: str
    assignedBy: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HomeworkCreate(BaseModel):
    studentClass: str
    section: str
    subject: str
    title: str
    description: str
    dueDate: str
    assignedBy: str

class Staff(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str  # teacher, office_staff
    mobile: str
    subject: Optional[str] = None
    joiningDate: str
    username: str
    password: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StaffCreate(BaseModel):
    name: str
    role: str
    mobile: str
    subject: Optional[str] = None
    joiningDate: str
    username: str
    password: str

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    mobile: Optional[str] = None
    subject: Optional[str] = None
    joiningDate: Optional[str] = None
    password: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# ==================== WHATSAPP SERVICE ====================

async def send_whatsapp_message(mobile, message, settings=None):
    try:
        if not settings or not settings.get('apiUrl') or not settings.get('accessToken'):
            return {"success": False, "message": "WhatsApp not configured"}
        headers = {"Authorization": f"Bearer {settings['accessToken']}", "Content-Type": "application/json"}
        payload = {"to": mobile, "recipient_type": "individual", "type": "text", "text": {"body": message}}
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(settings['apiUrl'], headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    except Exception as e:
        logger.error(f"WhatsApp send failed: {str(e)}")
        return {"success": False, "message": str(e)}

# ==================== PDF INVOICE GENERATION ====================

def generate_invoice_pdf(payment_data, student_data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=20, spaceAfter=10)
    elements = []

    elements.append(Paragraph("SchoolPro - Fee Receipt", title_style))
    elements.append(Spacer(1, 5*mm))

    info_data = [
        ["Receipt No:", payment_data.get('receiptNumber', '')],
        ["Date:", payment_data.get('paymentDate', '')[:10] if isinstance(payment_data.get('paymentDate'), str) else datetime.now().strftime('%Y-%m-%d')],
        ["Student Name:", student_data.get('studentName', '')],
        ["Roll No:", student_data.get('rollNo', '')],
        ["Class:", f"{student_data.get('studentClass', '')} - {student_data.get('section', '')}"],
        ["Father Name:", student_data.get('fatherName', '')],
        ["Mobile:", student_data.get('mobile', '')],
    ]
    t = RLTable(info_data, colWidths=[120, 350])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8*mm))

    fee_label = f"Term {payment_data.get('termNumber')}" if payment_data.get('termNumber') else (payment_data.get('feeName') or 'Custom Fee')
    pay_data = [
        ["Fee Type", "Amount", "Payment Mode"],
        [fee_label, f"Rs. {payment_data.get('amount', 0):,.2f}", payment_data.get('paymentMode', '').upper()],
    ]
    pt = RLTable(pay_data, colWidths=[200, 150, 120])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(pt)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("This is a computer-generated receipt.", styles['Normal']))

    doc.build(elements)
    buf.seek(0)
    return buf

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/login")
async def login(data: LoginRequest):
    # Check admin
    if data.username == "admin" and data.password == "12345678":
        return {"success": True, "user": {"name": "Admin", "username": "admin"}, "role": "admin"}
    # Check staff
    staff = await db.staff.find_one({"username": data.username, "password": data.password}, {"_id": 0})
    if staff:
        return {"success": True, "user": {k: v for k, v in staff.items() if k != 'password'}, "role": staff['role']}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.post("/auth/staff-login")
async def staff_login(data: LoginRequest):
    staff = await db.staff.find_one({"username": data.username, "password": data.password}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "user": {k: v for k, v in staff.items() if k != 'password'}, "role": staff['role']}

@api_router.post("/auth/parent-login")
async def parent_login(data: LoginRequest):
    student = await db.students.find_one({"parentUsername": data.username, "parentPassword": data.password}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "student": {k: v for k, v in student.items() if k != 'parentPassword'}, "role": "parent"}

# ==================== CLASS & SECTION ROUTES ====================

@api_router.post("/classes", response_model=ClassSection)
async def create_class_section(data: ClassSectionCreate):
    existing = await db.classes.find_one({"className": data.className}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Class already exists")
    obj = ClassSection(**data.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.classes.insert_one(doc)
    return obj

@api_router.get("/classes")
async def get_classes():
    return await db.classes.find({}, {"_id": 0}).to_list(100)

@api_router.put("/classes/{class_id}")
async def update_class_section(class_id: str, data: ClassSectionCreate):
    result = await db.classes.update_one({"id": class_id}, {"$set": {"className": data.className, "sections": data.sections}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    return await db.classes.find_one({"id": class_id}, {"_id": 0})

@api_router.delete("/classes/{class_id}")
async def delete_class_section(class_id: str):
    result = await db.classes.delete_one({"id": class_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted"}

# ==================== FEE TYPES ROUTES ====================

@api_router.post("/fee-types", response_model=FeeType)
async def create_fee_type(data: FeeTypeCreate):
    obj = FeeType(**data.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.fee_types.insert_one(doc)
    return obj

@api_router.get("/fee-types")
async def get_fee_types(applicableClass: Optional[str] = None):
    query = {}
    if applicableClass:
        query['$or'] = [{'applicableClass': applicableClass}, {'applicableClass': None}, {'applicableClass': ''}]
    return await db.fee_types.find(query, {"_id": 0}).to_list(500)

@api_router.put("/fee-types/{fee_type_id}")
async def update_fee_type(fee_type_id: str, data: FeeTypeCreate):
    result = await db.fee_types.update_one({"id": fee_type_id}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Fee type not found")
    return await db.fee_types.find_one({"id": fee_type_id}, {"_id": 0})

@api_router.delete("/fee-types/{fee_type_id}")
async def delete_fee_type(fee_type_id: str):
    result = await db.fee_types.delete_one({"id": fee_type_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fee type not found")
    return {"message": "Fee type deleted"}

# ==================== DATABASE SETTINGS ====================

@api_router.get("/settings/database")
async def get_database_settings():
    settings = await db.settings.find_one({"type": "database"}, {"_id": 0})
    if not settings:
        return {"mongoUrl": os.environ.get('MONGO_URL', ''), "dbName": os.environ.get('DB_NAME', '')}
    return settings

@api_router.put("/settings/database")
async def update_database_settings(data: DatabaseSettings):
    global client, db
    # Add authSource=admin if not already in URL for authenticated connections
    mongo_url = data.mongoUrl
    if '@' in mongo_url and 'authSource' not in mongo_url:
        if '?' not in mongo_url:
            if not mongo_url.endswith('/'):
                mongo_url = f"{mongo_url}/"
            mongo_url = f"{mongo_url}?authSource=admin"
        else:
            mongo_url = f"{mongo_url}&authSource=admin"
    try:
        test_client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        await test_client[data.dbName].command('ping')
        test_client.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not connect: {str(e)}")
    # Switch connection
    client.close()
    client = AsyncIOMotorClient(mongo_url)
    db = client[data.dbName]
    # Save settings in the NEW database
    await db.settings.update_one({"type": "database"}, {"$set": {"mongoUrl": data.mongoUrl, "dbName": data.dbName}}, upsert=True)
    return {"message": "Database connected successfully"}

# ==================== STUDENT ROUTES ====================

@api_router.post("/students", response_model=Student)
async def create_student(student: StudentCreate):
    existing = await db.students.find_one({"rollNo": student.rollNo}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Roll number already exists")
    student_obj = Student(**student.model_dump())
    doc = student_obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.students.insert_one(doc)
    return student_obj

@api_router.post("/students/bulk")
async def bulk_upload_students(file: UploadFile = File(...)):
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        added, errors = 0, []
        for row in csv_reader:
            try:
                student_data = StudentCreate(
                    studentName=row['Student Name'].strip(), rollNo=row['Roll No'].strip(),
                    studentClass=row['Class'].strip(), section=row['Section'].strip(),
                    fatherName=row['Father Name'].strip(), motherName=row['Mother Name'].strip(),
                    mobile=row['Mobile Number'].strip(), address=row['Address'].strip(),
                    feeTerm1=float(row['Fee Term1']), feeTerm2=float(row['Fee Term2']), feeTerm3=float(row['Fee Term3']),
                    parentUsername=row.get('Parent Username', '').strip() or None,
                    parentPassword=row.get('Parent Password', '').strip() or None,
                )
                existing = await db.students.find_one({"rollNo": student_data.rollNo}, {"_id": 0})
                if existing:
                    errors.append(f"Roll {student_data.rollNo} exists")
                    continue
                student_obj = Student(**student_data.model_dump())
                doc = student_obj.model_dump()
                doc['createdAt'] = doc['createdAt'].isoformat()
                await db.students.insert_one(doc)
                added += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
        return {"added": added, "errors": errors}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/students/sample-csv")
async def download_sample_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student Name', 'Roll No', 'Class', 'Section', 'Father Name', 'Mother Name', 'Mobile Number', 'Address', 'Fee Term1', 'Fee Term2', 'Fee Term3', 'Parent Username', 'Parent Password'])
    writer.writerow(['John Doe', '101', '1', 'A', 'Robert Doe', 'Jane Doe', '9876543210', '123 Main St', '5000', '5000', '5000', 'parent101', 'pass101'])
    writer.writerow(['Alice Smith', '102', '1', 'A', 'Michael Smith', 'Sarah Smith', '9876543211', '456 Oak Ave', '5000', '5000', '5000', 'parent102', 'pass102'])
    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sample_students.csv"})

@api_router.get("/students", response_model=List[Student])
async def get_students(studentClass: Optional[str] = None, section: Optional[str] = None, search: Optional[str] = None):
    query = {}
    if studentClass: query['studentClass'] = studentClass
    if section: query['section'] = section
    if search: query['$or'] = [{'studentName': {'$regex': search, '$options': 'i'}}, {'rollNo': {'$regex': search, '$options': 'i'}}]
    students = await db.students.find(query, {"_id": 0}).to_list(1000)
    for s in students:
        if isinstance(s.get('createdAt'), str): s['createdAt'] = datetime.fromisoformat(s['createdAt'])
    return students

@api_router.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, update_data: StudentUpdate):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict: await db.students.update_one({"id": student_id}, {"$set": update_dict})
    updated = await db.students.find_one({"id": student_id}, {"_id": 0})
    if isinstance(updated.get('createdAt'), str): updated['createdAt'] = datetime.fromisoformat(updated['createdAt'])
    return Student(**updated)

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await db.students.delete_one({"id": student_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}

@api_router.post("/students/promote")
async def promote_students(request: PromoteRequest):
    result = await db.students.update_many({"studentClass": request.fromClass}, {"$set": {"studentClass": request.toClass}})
    return {"message": f"Promoted {result.modified_count} students from {request.fromClass} to {request.toClass}"}

# ==================== ATTENDANCE ROUTES ====================

@api_router.post("/attendance")
async def mark_attendance(data: AttendanceSubmit):
    await db.attendance.delete_many({"studentClass": data.studentClass, "section": data.section, "date": data.date})
    records = []
    for record in data.records:
        att = AttendanceRecord(studentId=record['studentId'], rollNo=record['rollNo'], studentName=record['studentName'],
                               studentClass=data.studentClass, section=data.section, date=data.date, status=record['status'])
        doc = att.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        records.append(doc)
    if records: await db.attendance.insert_many(records)
    return {"message": f"Attendance marked for {len(records)} students"}

@api_router.get("/attendance")
async def get_attendance(studentClass: Optional[str] = None, section: Optional[str] = None, startDate: Optional[str] = None, endDate: Optional[str] = None):
    query = {}
    if studentClass: query['studentClass'] = studentClass
    if section: query['section'] = section
    if startDate and endDate: query['date'] = {'$gte': startDate, '$lte': endDate}
    elif startDate: query['date'] = startDate
    return await db.attendance.find(query, {"_id": 0}).to_list(10000)

@api_router.get("/attendance/export")
async def export_attendance(studentClass: str, section: str, startDate: str, endDate: str, format: str = 'csv'):
    records = await db.attendance.find({"studentClass": studentClass, "section": section, "date": {'$gte': startDate, '$lte': endDate}}, {"_id": 0}).to_list(10000)
    if format == 'xlsx':
        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance"
        ws.append(['Roll No', 'Student Name', 'Date', 'Status'])
        for r in records: ws.append([r['rollNo'], r['studentName'], r['date'], r['status']])
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": f"attachment; filename=attendance.xlsx"})
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Roll No', 'Student Name', 'Date', 'Status'])
    for r in records: writer.writerow([r['rollNo'], r['studentName'], r['date'], r['status']])
    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=attendance.csv"})

@api_router.post("/attendance/send-alerts")
async def send_attendance_alerts(data: Dict):
    absent_records = data.get('absentRecords', [])
    settings_doc = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    sent_count = 0
    for record in absent_records:
        message = f"Dear Parent, {record['studentName']} (Roll: {record['rollNo']}) was absent on {record['date']} in Class {record['studentClass']}-{record['section']}."
        result = await send_whatsapp_message(record.get('mobile', ''), message, settings_doc)
        if result.get('success'): sent_count += 1
    return {"message": f"Alerts sent to {sent_count} parents"}

# ==================== FEE ROUTES ====================

@api_router.get("/fees/student/{roll_no}")
async def get_student_fees(roll_no: str):
    student = await db.students.find_one({"rollNo": roll_no}, {"_id": 0})
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    payments = await db.fee_payments.find({"rollNo": roll_no}, {"_id": 0}).to_list(100)
    paid_terms, paid_custom = {}, {}
    for p in payments:
        if p.get('termNumber'):
            k = f"term{p['termNumber']}"
            paid_terms[k] = paid_terms.get(k, 0) + p['amount']
        if p.get('feeTypeId'):
            paid_custom[p['feeTypeId']] = paid_custom.get(p['feeTypeId'], 0) + p['amount']
    custom_fees = await db.fee_types.find({
        "$or": [
            {"applicableClass": student.get('studentClass', ''), "applicableSection": student.get('section', '')},
            {"applicableClass": student.get('studentClass', ''), "applicableSection": {"$in": [None, ""]}},
            {"applicableClass": {"$in": [None, ""]}, "applicableSection": {"$in": [None, ""]}},
        ]
    }, {"_id": 0}).to_list(500)
    return {"student": student, "payments": payments, "paidTerms": paid_terms, "paidCustomFees": paid_custom, "customFees": custom_fees}

@api_router.post("/fees/payment")
async def create_fee_payment(payment: FeePaymentCreate):
    receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
    payment_obj = FeePayment(**payment.model_dump(), receiptNumber=receipt_number)
    doc = payment_obj.model_dump()
    doc['paymentDate'] = doc['paymentDate'].isoformat()
    await db.fee_payments.insert_one(doc)
    settings_doc = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    student = await db.students.find_one({"rollNo": payment.rollNo}, {"_id": 0})
    if student:
        fee_label = f"Term: {payment.termNumber}" if payment.termNumber else f"Fee: {payment.feeName or 'Custom'}"
        message = f"Payment Receipt\nStudent: {payment.studentName}\nAmount: Rs.{payment.amount}\n{fee_label}\nMode: {payment.paymentMode}\nReceipt: {receipt_number}\nDate: {datetime.now().strftime('%Y-%m-%d')}"
        await send_whatsapp_message(student.get('mobile', ''), message, settings_doc)
    return payment_obj

@api_router.get("/fees/invoice/{payment_id}")
async def download_invoice(payment_id: str):
    payment = await db.fee_payments.find_one({"id": payment_id}, {"_id": 0})
    if not payment: raise HTTPException(status_code=404, detail="Payment not found")
    student = await db.students.find_one({"rollNo": payment['rollNo']}, {"_id": 0})
    if not student: student = {"studentName": payment.get('studentName', ''), "rollNo": payment.get('rollNo', ''), "studentClass": "", "section": "", "fatherName": "", "mobile": ""}
    buf = generate_invoice_pdf(payment, student)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice_{payment['receiptNumber']}.pdf"})

@api_router.get("/fees/day-sheet")
async def get_day_sheet(date: Optional[str] = None):
    if not date: date = datetime.now().strftime('%Y-%m-%d')
    start = datetime.fromisoformat(f"{date}T00:00:00")
    end = datetime.fromisoformat(f"{date}T23:59:59")
    payments = await db.fee_payments.find({"paymentDate": {"$gte": start.isoformat(), "$lte": end.isoformat()}}, {"_id": 0}).to_list(1000)
    total = sum(p['amount'] for p in payments)
    upi_total = sum(p['amount'] for p in payments if p['paymentMode'] == 'upi')
    cash_total = sum(p['amount'] for p in payments if p['paymentMode'] == 'cash')
    return {"date": date, "payments": payments, "total": total, "upiTotal": upi_total, "cashTotal": cash_total, "count": len(payments)}

@api_router.get("/fees/export")
async def export_fees(startDate: str, endDate: str, format: str = 'csv'):
    start = datetime.fromisoformat(f"{startDate}T00:00:00")
    end = datetime.fromisoformat(f"{endDate}T23:59:59")
    payments = await db.fee_payments.find({"paymentDate": {"$gte": start.isoformat(), "$lte": end.isoformat()}}, {"_id": 0}).to_list(10000)
    if format == 'xlsx':
        wb = Workbook()
        ws = wb.active
        ws.append(['Receipt No', 'Roll No', 'Student Name', 'Fee Type', 'Amount', 'Mode', 'Date'])
        for p in payments:
            d = p['paymentDate'][:10] if isinstance(p['paymentDate'], str) else p['paymentDate'].strftime('%Y-%m-%d')
            fl = f"Term {p['termNumber']}" if p.get('termNumber') else (p.get('feeName') or 'Custom')
            ws.append([p['receiptNumber'], p['rollNo'], p['studentName'], fl, p['amount'], p['paymentMode'], d])
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=fees_report.xlsx"})
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Receipt No', 'Roll No', 'Student Name', 'Fee Type', 'Amount', 'Mode', 'Date'])
    for p in payments:
        d = p['paymentDate'][:10] if isinstance(p['paymentDate'], str) else p['paymentDate'].strftime('%Y-%m-%d')
        fl = f"Term {p['termNumber']}" if p.get('termNumber') else (p.get('feeName') or 'Custom')
        writer.writerow([p['receiptNumber'], p['rollNo'], p['studentName'], fl, p['amount'], p['paymentMode'], d])
    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=fees_report.csv"})

@api_router.post("/fees/send-reminders")
async def send_fee_reminders():
    settings_doc = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    today = datetime.now().strftime('%Y-%m-%d')
    upcoming = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    fee_types = await db.fee_types.find({"dueDate": {"$ne": None, "$lte": upcoming}}, {"_id": 0}).to_list(500)
    sent_count = 0
    for ft in fee_types:
        query = {}
        if ft.get('applicableClass') and ft['applicableClass']: query['studentClass'] = ft['applicableClass']
        if ft.get('applicableSection') and ft['applicableSection']: query['section'] = ft['applicableSection']
        students = await db.students.find(query, {"_id": 0}).to_list(10000)
        for student in students:
            paid = await db.fee_payments.find_one({"studentId": student['id'], "feeTypeId": ft['id']}, {"_id": 0})
            if paid: continue
            message = f"Fee Reminder: {ft['feeName']} of Rs.{ft['amount']} is due on {ft['dueDate']} for {student['studentName']}."
            result = await send_whatsapp_message(student.get('mobile', ''), message, settings_doc)
            if result.get('success'): sent_count += 1
    return {"message": f"Reminders sent to {sent_count} parents", "feeTypesChecked": len(fee_types)}

# ==================== EXPENSE ROUTES ====================

@api_router.post("/expenses", response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    obj = Expense(**expense.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.expenses.insert_one(doc)
    return obj

@api_router.get("/expenses", response_model=List[Expense])
async def get_expenses(startDate: Optional[str] = None, endDate: Optional[str] = None):
    query = {}
    if startDate and endDate: query['date'] = {'$gte': startDate, '$lte': endDate}
    expenses = await db.expenses.find(query, {"_id": 0}).to_list(1000)
    for e in expenses:
        if isinstance(e.get('createdAt'), str): e['createdAt'] = datetime.fromisoformat(e['createdAt'])
    return expenses

# ==================== SETTINGS ROUTES ====================

@api_router.get("/settings/whatsapp")
async def get_whatsapp_settings():
    settings = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    if not settings: return {"apiUrl": "", "accessToken": ""}
    return settings

@api_router.put("/settings/whatsapp")
async def update_whatsapp_settings(settings: WhatsAppSettings):
    await db.settings.update_one({"type": "whatsapp"}, {"$set": {"apiUrl": settings.apiUrl, "accessToken": settings.accessToken}}, upsert=True)
    return {"message": "Settings updated"}

# ==================== FILE UPLOAD ====================

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    base64_content = base64.b64encode(content).decode('utf-8')
    return {"url": f"data:{file.content_type};base64,{base64_content}", "filename": file.filename}

# ==================== INVENTORY ROUTES ====================

@api_router.post("/inventory")
async def create_inventory_item(item: InventoryItemCreate):
    obj = InventoryItem(**item.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.inventory.insert_one(doc)
    return obj

@api_router.get("/inventory")
async def get_inventory(category: Optional[str] = None):
    query = {}
    if category: query['category'] = category
    return await db.inventory.find(query, {"_id": 0}).to_list(1000)

@api_router.put("/inventory/{item_id}")
async def update_inventory_item(item_id: str, data: InventoryItemCreate):
    result = await db.inventory.update_one({"id": item_id}, {"$set": data.model_dump()})
    if result.matched_count == 0: raise HTTPException(status_code=404, detail="Item not found")
    return await db.inventory.find_one({"id": item_id}, {"_id": 0})

@api_router.delete("/inventory/{item_id}")
async def delete_inventory_item(item_id: str):
    result = await db.inventory.delete_one({"id": item_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

@api_router.post("/inventory/issue")
async def issue_inventory(data: InventoryIssueCreate):
    item = await db.inventory.find_one({"id": data.itemId}, {"_id": 0})
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    if item['quantity'] < data.quantity: raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {item['quantity']}")
    student = await db.students.find_one({"rollNo": data.rollNo}, {"_id": 0})
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    # Deduct stock
    await db.inventory.update_one({"id": data.itemId}, {"$inc": {"quantity": -data.quantity}})
    issue = InventoryIssue(itemId=data.itemId, itemName=item['itemName'], studentId=student['id'],
                           rollNo=data.rollNo, studentName=student['studentName'], quantity=data.quantity, date=data.date)
    doc = issue.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.inventory_issues.insert_one(doc)
    return issue

@api_router.get("/inventory/issues")
async def get_inventory_issues(studentId: Optional[str] = None):
    query = {}
    if studentId: query['studentId'] = studentId
    return await db.inventory_issues.find(query, {"_id": 0}).to_list(1000)

# ==================== EVENT ROUTES ====================

@api_router.post("/events")
async def create_event(event: EventCreate):
    obj = Event(**event.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.events.insert_one(doc)
    return obj

@api_router.get("/events")
async def get_events(month: Optional[str] = None):
    query = {}
    if month: query['date'] = {'$regex': f'^{month}'}
    return await db.events.find(query, {"_id": 0}).to_list(1000)

@api_router.put("/events/{event_id}")
async def update_event(event_id: str, data: EventCreate):
    result = await db.events.update_one({"id": event_id}, {"$set": data.model_dump()})
    if result.matched_count == 0: raise HTTPException(status_code=404, detail="Event not found")
    return await db.events.find_one({"id": event_id}, {"_id": 0})

@api_router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    result = await db.events.delete_one({"id": event_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}

# ==================== HOMEWORK ROUTES ====================

@api_router.post("/homework")
async def create_homework(hw: HomeworkCreate):
    obj = Homework(**hw.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.homework.insert_one(doc)
    return obj

@api_router.get("/homework")
async def get_homework(studentClass: Optional[str] = None, section: Optional[str] = None):
    query = {}
    if studentClass: query['studentClass'] = studentClass
    if section: query['section'] = section
    return await db.homework.find(query, {"_id": 0}).to_list(1000)

@api_router.put("/homework/{hw_id}")
async def update_homework(hw_id: str, data: HomeworkCreate):
    result = await db.homework.update_one({"id": hw_id}, {"$set": data.model_dump()})
    if result.matched_count == 0: raise HTTPException(status_code=404, detail="Homework not found")
    return await db.homework.find_one({"id": hw_id}, {"_id": 0})

@api_router.delete("/homework/{hw_id}")
async def delete_homework(hw_id: str):
    result = await db.homework.delete_one({"id": hw_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Homework not found")
    return {"message": "Homework deleted"}

# ==================== STAFF ROUTES ====================

@api_router.post("/staff")
async def create_staff(data: StaffCreate):
    existing = await db.staff.find_one({"username": data.username}, {"_id": 0})
    if existing: raise HTTPException(status_code=400, detail="Username already exists")
    obj = Staff(**data.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.staff.insert_one(doc)
    return {k: v for k, v in obj.model_dump().items() if k != 'password'}

@api_router.get("/staff")
async def get_staff():
    staff = await db.staff.find({}, {"_id": 0}).to_list(500)
    return [{k: v for k, v in s.items() if k != 'password'} for s in staff]

@api_router.put("/staff/{staff_id}")
async def update_staff(staff_id: str, data: StaffUpdate):
    update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_dict: return await db.staff.find_one({"id": staff_id}, {"_id": 0, "password": 0})
    result = await db.staff.update_one({"id": staff_id}, {"$set": update_dict})
    if result.matched_count == 0: raise HTTPException(status_code=404, detail="Staff not found")
    updated = await db.staff.find_one({"id": staff_id}, {"_id": 0})
    return {k: v for k, v in updated.items() if k != 'password'}

@api_router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: str):
    result = await db.staff.delete_one({"id": staff_id})
    if result.deleted_count == 0: raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted"}

# ==================== STUDENT DETAIL ====================

@api_router.get("/students/{student_id}/detail")
async def get_student_detail(student_id: str):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    attendance = await db.attendance.find({"studentId": student_id}, {"_id": 0}).to_list(10000)
    total_days = len(attendance)
    present_days = sum(1 for a in attendance if a['status'] == 'present')
    absent_days = sum(1 for a in attendance if a['status'] == 'absent')
    payments = await db.fee_payments.find({"studentId": student_id}, {"_id": 0}).to_list(100)
    custom_fees = await db.fee_types.find({
        "$or": [
            {"applicableClass": student.get('studentClass', ''), "applicableSection": student.get('section', '')},
            {"applicableClass": student.get('studentClass', ''), "applicableSection": {"$in": [None, ""]}},
            {"applicableClass": {"$in": [None, ""]}, "applicableSection": {"$in": [None, ""]}},
        ]
    }, {"_id": 0}).to_list(500)
    paid_terms, paid_custom = {}, {}
    for p in payments:
        if p.get('termNumber'): k = f"term{p['termNumber']}"; paid_terms[k] = paid_terms.get(k, 0) + p['amount']
        if p.get('feeTypeId'): paid_custom[p['feeTypeId']] = paid_custom.get(p['feeTypeId'], 0) + p['amount']
    # Inventory issued
    inventory_issued = await db.inventory_issues.find({"studentId": student_id}, {"_id": 0}).to_list(500)
    return {
        "student": student, "attendance": attendance,
        "attendanceStats": {"totalDays": total_days, "presentDays": present_days, "absentDays": absent_days,
                            "percentage": round(present_days / total_days * 100, 1) if total_days > 0 else 0},
        "payments": payments, "paidTerms": paid_terms, "paidCustomFees": paid_custom, "customFees": custom_fees,
        "inventoryIssued": inventory_issued,
    }

# ==================== PARENT PORTAL ====================

@api_router.get("/parent/dashboard/{student_id}")
async def parent_dashboard(student_id: str):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    attendance = await db.attendance.find({"studentId": student_id}, {"_id": 0}).to_list(10000)
    total_days = len(attendance)
    present_days = sum(1 for a in attendance if a['status'] == 'present')
    payments = await db.fee_payments.find({"studentId": student_id}, {"_id": 0}).to_list(100)
    events = await db.events.find({}, {"_id": 0}).to_list(100)
    homework = await db.homework.find({"studentClass": student.get('studentClass', ''), "section": student.get('section', '')}, {"_id": 0}).to_list(100)
    return {
        "student": {k: v for k, v in student.items() if k != 'parentPassword'},
        "attendanceStats": {"totalDays": total_days, "presentDays": present_days, "percentage": round(present_days / total_days * 100, 1) if total_days > 0 else 0},
        "recentAttendance": attendance[-30:] if attendance else [],
        "payments": payments, "events": events, "homework": homework,
    }

# ==================== DASHBOARD STATS ====================

@api_router.get("/stats/dashboard")
async def get_dashboard_stats():
    total_students = await db.students.count_documents({})
    today = datetime.now().strftime('%Y-%m-%d')
    today_present = await db.attendance.count_documents({"date": today, "status": "present"})
    today_absent = await db.attendance.count_documents({"date": today, "status": "absent"})
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    fees_result = await db.fee_payments.aggregate(pipeline).to_list(1)
    total_fees = fees_result[0]['total'] if fees_result else 0
    students = await db.students.find({}, {"_id": 0, "feeTerm1": 1, "feeTerm2": 1, "feeTerm3": 1}).to_list(10000)
    total_expected = sum(s.get('feeTerm1', 0) + s.get('feeTerm2', 0) + s.get('feeTerm3', 0) for s in students)
    return {"totalStudents": total_students, "presentToday": today_present, "absentToday": today_absent,
            "totalFeesCollected": total_fees, "pendingFees": total_expected - total_fees}

@api_router.get("/")
async def root():
    return {"message": "SchoolPro API"}

app.include_router(api_router)

app.add_middleware(CORSMiddleware, allow_credentials=True,
                   allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
                   allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
