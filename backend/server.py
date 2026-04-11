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
from datetime import datetime, timezone, date
import httpx
import csv
import io
from openpyxl import Workbook
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Logging
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

class AttendanceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    studentId: str
    rollNo: str
    studentName: str
    studentClass: str
    section: str
    date: str
    status: str  # present, absent, holiday, undefined
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
    termNumber: Optional[int] = None  # 1, 2, or 3 (for term fees)
    feeTypeId: Optional[str] = None  # for custom fees
    feeName: Optional[str] = None
    amount: float
    paymentMode: str  # upi or cash
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
    classes = await db.classes.find({}, {"_id": 0}).to_list(100)
    return classes

@api_router.put("/classes/{class_id}")
async def update_class_section(class_id: str, data: ClassSectionCreate):
    result = await db.classes.update_one(
        {"id": class_id},
        {"$set": {"className": data.className, "sections": data.sections}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    updated = await db.classes.find_one({"id": class_id}, {"_id": 0})
    return updated

@api_router.delete("/classes/{class_id}")
async def delete_class_section(class_id: str):
    result = await db.classes.delete_one({"id": class_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}

# ==================== FEE TYPES ROUTES ====================

@api_router.post("/fee-types", response_model=FeeType)
async def create_fee_type(data: FeeTypeCreate):
    obj = FeeType(**data.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.fee_types.insert_one(doc)
    return obj

@api_router.get("/fee-types")
async def get_fee_types(applicableClass: Optional[str] = None, applicableSection: Optional[str] = None):
    query = {}
    if applicableClass:
        query['$or'] = [
            {'applicableClass': applicableClass},
            {'applicableClass': None},
            {'applicableClass': ''},
        ]
    if applicableSection:
        if '$or' in query:
            query['$and'] = [
                {'$or': query.pop('$or')},
                {'$or': [
                    {'applicableSection': applicableSection},
                    {'applicableSection': None},
                    {'applicableSection': ''},
                ]}
            ]
    fee_types = await db.fee_types.find(query, {"_id": 0}).to_list(500)
    return fee_types

@api_router.put("/fee-types/{fee_type_id}")
async def update_fee_type(fee_type_id: str, data: FeeTypeCreate):
    update_dict = data.model_dump()
    result = await db.fee_types.update_one({"id": fee_type_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Fee type not found")
    updated = await db.fee_types.find_one({"id": fee_type_id}, {"_id": 0})
    return updated

@api_router.delete("/fee-types/{fee_type_id}")
async def delete_fee_type(fee_type_id: str):
    result = await db.fee_types.delete_one({"id": fee_type_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fee type not found")
    return {"message": "Fee type deleted successfully"}

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
    # Test the connection first
    try:
        test_client = AsyncIOMotorClient(data.mongoUrl, serverSelectionTimeoutMS=5000)
        test_db = test_client[data.dbName]
        await test_db.command('ping')
        test_client.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not connect to database: {str(e)}")

    await db.settings.update_one(
        {"type": "database"},
        {"$set": {"mongoUrl": data.mongoUrl, "dbName": data.dbName}},
        upsert=True
    )

    # Update global db connection
    client.close()
    client = AsyncIOMotorClient(data.mongoUrl)
    db = client[data.dbName]

    return {"message": "Database settings updated and connected successfully"}

# ==================== WHATSAPP SERVICE ====================

async def send_whatsapp_message(mobile: str, message: str, settings: Dict = None):
    """Send WhatsApp message using custom API"""
    try:
        if not settings or not settings.get('apiUrl') or not settings.get('accessToken'):
            logger.warning("WhatsApp settings not configured")
            return {"success": False, "message": "WhatsApp not configured"}
        
        headers = {
            "Authorization": f"Bearer {settings['accessToken']}",
            "Content-Type": "application/json"
        }
        
        # Adjust based on actual API requirements
        # This is a simplified version - actual template structure may vary
        payload = {
            "to": mobile,
            "recipient_type": "individual",
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(settings['apiUrl'], headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            logger.info(f"WhatsApp message sent to {mobile}")
            return {"success": True, "data": response.json()}
    except Exception as e:
        logger.error(f"Failed to send WhatsApp: {str(e)}")
        return {"success": False, "message": str(e)}

# ==================== STUDENT ROUTES ====================

@api_router.post("/students", response_model=Student)
async def create_student(student: StudentCreate):
    # Check if roll number already exists
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
        
        added = 0
        errors = []
        
        for row in csv_reader:
            try:
                student_data = StudentCreate(
                    studentName=row['Student Name'].strip(),
                    rollNo=row['Roll No'].strip(),
                    studentClass=row['Class'].strip(),
                    section=row['Section'].strip(),
                    fatherName=row['Father Name'].strip(),
                    motherName=row['Mother Name'].strip(),
                    mobile=row['Mobile Number'].strip(),
                    address=row['Address'].strip(),
                    feeTerm1=float(row['Fee Term1']),
                    feeTerm2=float(row['Fee Term2']),
                    feeTerm3=float(row['Fee Term3'])
                )
                
                # Check if roll number exists
                existing = await db.students.find_one({"rollNo": student_data.rollNo}, {"_id": 0})
                if existing:
                    errors.append(f"Roll {student_data.rollNo} already exists")
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
    writer.writerow(['Student Name', 'Roll No', 'Class', 'Section', 'Father Name', 'Mother Name', 'Mobile Number', 'Address', 'Fee Term1', 'Fee Term2', 'Fee Term3'])
    writer.writerow(['John Doe', '101', '1', 'A', 'Robert Doe', 'Jane Doe', '9876543210', '123 Main St', '5000', '5000', '5000'])
    writer.writerow(['Alice Smith', '102', '1', 'A', 'Michael Smith', 'Sarah Smith', '9876543211', '456 Oak Ave', '5000', '5000', '5000'])
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sample_students.csv"}
    )

@api_router.get("/students", response_model=List[Student])
async def get_students(studentClass: Optional[str] = None, section: Optional[str] = None, search: Optional[str] = None):
    query = {}
    if studentClass:
        query['studentClass'] = studentClass
    if section:
        query['section'] = section
    if search:
        query['$or'] = [
            {'studentName': {'$regex': search, '$options': 'i'}},
            {'rollNo': {'$regex': search, '$options': 'i'}}
        ]
    
    students = await db.students.find(query, {"_id": 0}).to_list(1000)
    for s in students:
        if isinstance(s.get('createdAt'), str):
            s['createdAt'] = datetime.fromisoformat(s['createdAt'])
    return students

@api_router.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, update_data: StudentUpdate):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_dict:
        await db.students.update_one({"id": student_id}, {"$set": update_dict})
    
    updated = await db.students.find_one({"id": student_id}, {"_id": 0})
    if isinstance(updated.get('createdAt'), str):
        updated['createdAt'] = datetime.fromisoformat(updated['createdAt'])
    return Student(**updated)

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await db.students.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

@api_router.post("/students/promote")
async def promote_students(request: PromoteRequest):
    students = await db.students.find({"studentClass": request.fromClass}, {"_id": 0}).to_list(1000)
    if not students:
        raise HTTPException(status_code=404, detail="No students found in this class")
    
    result = await db.students.update_many(
        {"studentClass": request.fromClass},
        {"$set": {"studentClass": request.toClass}}
    )
    
    return {"message": f"Promoted {result.modified_count} students from {request.fromClass} to {request.toClass}"}

# ==================== ATTENDANCE ROUTES ====================

@api_router.post("/attendance")
async def mark_attendance(data: AttendanceSubmit):
    try:
        # Delete existing attendance for this class, section, and date
        await db.attendance.delete_many({
            "studentClass": data.studentClass,
            "section": data.section,
            "date": data.date
        })
        
        # Insert new records
        records_to_insert = []
        for record in data.records:
            att_record = AttendanceRecord(
                studentId=record['studentId'],
                rollNo=record['rollNo'],
                studentName=record['studentName'],
                studentClass=data.studentClass,
                section=data.section,
                date=data.date,
                status=record['status']
            )
            doc = att_record.model_dump()
            doc['createdAt'] = doc['createdAt'].isoformat()
            records_to_insert.append(doc)
        
        if records_to_insert:
            await db.attendance.insert_many(records_to_insert)
        
        return {"message": f"Attendance marked for {len(records_to_insert)} students"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/attendance")
async def get_attendance(
    studentClass: Optional[str] = None,
    section: Optional[str] = None,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None
):
    query = {}
    if studentClass:
        query['studentClass'] = studentClass
    if section:
        query['section'] = section
    if startDate and endDate:
        query['date'] = {'$gte': startDate, '$lte': endDate}
    elif startDate:
        query['date'] = startDate
    
    records = await db.attendance.find(query, {"_id": 0}).to_list(10000)
    return records

@api_router.get("/attendance/export")
async def export_attendance(
    studentClass: str,
    section: str,
    startDate: str,
    endDate: str,
    format: str = 'csv'
):
    records = await db.attendance.find({
        "studentClass": studentClass,
        "section": section,
        "date": {'$gte': startDate, '$lte': endDate}
    }, {"_id": 0}).to_list(10000)
    
    if format == 'xlsx':
        # Excel export
        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance"
        ws.append(['Roll No', 'Student Name', 'Date', 'Status'])
        
        for record in records:
            ws.append([record['rollNo'], record['studentName'], record['date'], record['status']])
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=attendance_{studentClass}_{section}.xlsx"}
        )
    else:
        # CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Roll No', 'Student Name', 'Date', 'Status'])
        
        for record in records:
            writer.writerow([record['rollNo'], record['studentName'], record['date'], record['status']])
        
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=attendance_{studentClass}_{section}.csv"}
        )

@api_router.post("/attendance/send-alerts")
async def send_attendance_alerts(data: Dict):
    """Send WhatsApp alerts for absent students"""
    absent_records = data.get('absentRecords', [])
    
    # Get WhatsApp settings
    settings_doc = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    
    sent_count = 0
    for record in absent_records:
        message = f"Dear Parent, {record['studentName']} (Roll: {record['rollNo']}) was absent on {record['date']} in Class {record['studentClass']}-{record['section']}."
        result = await send_whatsapp_message(record.get('mobile', ''), message, settings_doc)
        if result.get('success'):
            sent_count += 1
    
    return {"message": f"Alerts sent to {sent_count} parents"}

# ==================== FEE ROUTES ====================

@api_router.get("/fees/student/{roll_no}")
async def get_student_fees(roll_no: str):
    student = await db.students.find_one({"rollNo": roll_no}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get payment history
    payments = await db.fee_payments.find({"rollNo": roll_no}, {"_id": 0}).to_list(100)
    
    # Calculate paid terms
    paid_terms = {}
    paid_custom_fees = {}
    for payment in payments:
        if payment.get('termNumber'):
            term_key = f"term{payment['termNumber']}"
            if term_key not in paid_terms:
                paid_terms[term_key] = 0
            paid_terms[term_key] += payment['amount']
        if payment.get('feeTypeId'):
            fid = payment['feeTypeId']
            if fid not in paid_custom_fees:
                paid_custom_fees[fid] = 0
            paid_custom_fees[fid] += payment['amount']
    
    # Get custom fee types applicable to this student
    student_class = student.get('studentClass', '')
    student_section = student.get('section', '')
    custom_fees = await db.fee_types.find({
        "$or": [
            {"applicableClass": student_class, "applicableSection": student_section},
            {"applicableClass": student_class, "applicableSection": {"$in": [None, ""]}},
            {"applicableClass": {"$in": [None, ""]}, "applicableSection": {"$in": [None, ""]}},
        ]
    }, {"_id": 0}).to_list(500)
    
    return {
        "student": student,
        "payments": payments,
        "paidTerms": paid_terms,
        "paidCustomFees": paid_custom_fees,
        "customFees": custom_fees
    }

@api_router.post("/fees/payment")
async def create_fee_payment(payment: FeePaymentCreate):
    receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    payment_obj = FeePayment(
        **payment.model_dump(),
        receiptNumber=receipt_number
    )
    doc = payment_obj.model_dump()
    doc['paymentDate'] = doc['paymentDate'].isoformat()
    await db.fee_payments.insert_one(doc)
    
    # Send WhatsApp receipt
    settings_doc = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    student = await db.students.find_one({"rollNo": payment.rollNo}, {"_id": 0})
    
    if student:
        fee_label = f"Term: {payment.termNumber}" if payment.termNumber else f"Fee: {payment.feeName or 'Custom'}"
        message = f"Payment Receipt\nStudent: {payment.studentName}\nAmount: ₹{payment.amount}\n{fee_label}\nMode: {payment.paymentMode}\nReceipt: {receipt_number}\nDate: {datetime.now().strftime('%Y-%m-%d')}"
        await send_whatsapp_message(student.get('mobile', ''), message, settings_doc)
    
    return payment_obj

@api_router.get("/fees/day-sheet")
async def get_day_sheet(date: Optional[str] = None):
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    start_date = datetime.fromisoformat(f"{date}T00:00:00")
    end_date = datetime.fromisoformat(f"{date}T23:59:59")
    
    payments = await db.fee_payments.find({
        "paymentDate": {
            "$gte": start_date.isoformat(),
            "$lte": end_date.isoformat()
        }
    }, {"_id": 0}).to_list(1000)
    
    total = sum(p['amount'] for p in payments)
    upi_total = sum(p['amount'] for p in payments if p['paymentMode'] == 'upi')
    cash_total = sum(p['amount'] for p in payments if p['paymentMode'] == 'cash')
    
    return {
        "date": date,
        "payments": payments,
        "total": total,
        "upiTotal": upi_total,
        "cashTotal": cash_total,
        "count": len(payments)
    }

@api_router.get("/fees/export")
async def export_fees(startDate: str, endDate: str, format: str = 'csv'):
    start = datetime.fromisoformat(f"{startDate}T00:00:00")
    end = datetime.fromisoformat(f"{endDate}T23:59:59")
    
    payments = await db.fee_payments.find({
        "paymentDate": {
            "$gte": start.isoformat(),
            "$lte": end.isoformat()
        }
    }, {"_id": 0}).to_list(10000)
    
    if format == 'xlsx':
        wb = Workbook()
        ws = wb.active
        ws.title = "Fees"
        ws.append(['Receipt No', 'Roll No', 'Student Name', 'Fee Type', 'Amount', 'Mode', 'Date'])
        
        for p in payments:
            date_str = p['paymentDate'][:10] if isinstance(p['paymentDate'], str) else p['paymentDate'].strftime('%Y-%m-%d')
            fee_label = f"Term {p['termNumber']}" if p.get('termNumber') else (p.get('feeName') or 'Custom')
            ws.append([p['receiptNumber'], p['rollNo'], p['studentName'], fee_label, p['amount'], p['paymentMode'], date_str])
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=fees_report.xlsx"}
        )
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Receipt No', 'Roll No', 'Student Name', 'Fee Type', 'Amount', 'Mode', 'Date'])
        
        for p in payments:
            date_str = p['paymentDate'][:10] if isinstance(p['paymentDate'], str) else p['paymentDate'].strftime('%Y-%m-%d')
            fee_label = f"Term {p['termNumber']}" if p.get('termNumber') else (p.get('feeName') or 'Custom')
            writer.writerow([p['receiptNumber'], p['rollNo'], p['studentName'], fee_label, p['amount'], p['paymentMode'], date_str])
        
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=fees_report.csv"}
        )

# ==================== EXPENSE ROUTES ====================

@api_router.post("/expenses", response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    expense_obj = Expense(**expense.model_dump())
    doc = expense_obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.expenses.insert_one(doc)
    return expense_obj

@api_router.get("/expenses", response_model=List[Expense])
async def get_expenses(startDate: Optional[str] = None, endDate: Optional[str] = None):
    query = {}
    if startDate and endDate:
        query['date'] = {'$gte': startDate, '$lte': endDate}
    
    expenses = await db.expenses.find(query, {"_id": 0}).to_list(1000)
    for e in expenses:
        if isinstance(e.get('createdAt'), str):
            e['createdAt'] = datetime.fromisoformat(e['createdAt'])
    return expenses

# ==================== SETTINGS ROUTES ====================

@api_router.get("/settings/whatsapp")
async def get_whatsapp_settings():
    settings = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    if not settings:
        return {"apiUrl": "", "accessToken": ""}
    return settings

@api_router.put("/settings/whatsapp")
async def update_whatsapp_settings(settings: WhatsAppSettings):
    await db.settings.update_one(
        {"type": "whatsapp"},
        {"$set": {"apiUrl": settings.apiUrl, "accessToken": settings.accessToken}},
        upsert=True
    )
    return {"message": "Settings updated successfully"}

# ==================== FILE UPLOAD ====================

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        base64_content = base64.b64encode(content).decode('utf-8')
        file_url = f"data:{file.content_type};base64,{base64_content}"
        return {"url": file_url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== DASHBOARD STATS ====================

@api_router.get("/stats/dashboard")
async def get_dashboard_stats():
    total_students = await db.students.count_documents({})
    
    # Today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    today_present = await db.attendance.count_documents({"date": today, "status": "present"})
    today_absent = await db.attendance.count_documents({"date": today, "status": "absent"})
    
    # Total fees collected
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    fees_result = await db.fee_payments.aggregate(pipeline).to_list(1)
    total_fees = fees_result[0]['total'] if fees_result else 0
    
    # Pending fees (students with unpaid terms)
    students = await db.students.find({}, {"_id": 0}).to_list(10000)
    total_expected = sum(s['feeTerm1'] + s['feeTerm2'] + s['feeTerm3'] for s in students)
    pending_fees = total_expected - total_fees
    
    return {
        "totalStudents": total_students,
        "presentToday": today_present,
        "absentToday": today_absent,
        "totalFeesCollected": total_fees,
        "pendingFees": pending_fees
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
