"""Auth and Class/Section router."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
import uuid
import csv
import io
import base64
import logging
from openpyxl import Workbook

from db import db
from models import *
from services.whatsapp import *
from services.pdf import *

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== AUTH ROUTES ====================

@router.post("/auth/login")
async def login(data: LoginRequest):
    # Check super admin
    if data.username == "admin" and data.password == "12345678":
        return {"success": True, "user": {"name": "Super Admin", "username": "admin"}, "role": "super_admin"}
    # Check staff (teacher, office_staff, admin_role)
    staff = await db.staff.find_one({"username": data.username, "password": data.password}, {"_id": 0})
    if staff:
        return {"success": True, "user": {k: v for k, v in staff.items() if k != 'password'}, "role": staff['role']}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/auth/staff-login")
async def staff_login(data: LoginRequest):
    staff = await db.staff.find_one({"username": data.username, "password": data.password}, {"_id": 0})
    if not staff:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "user": {k: v for k, v in staff.items() if k != 'password'}, "role": staff['role']}

@router.post("/auth/parent-login")
async def parent_login(data: LoginRequest):
    student = await db.students.find_one({"parentUsername": data.username, "parentPassword": data.password}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "student": {k: v for k, v in student.items() if k != 'parentPassword'}, "role": "parent"}

# ==================== CLASS & SECTION ROUTES ====================

@router.post("/classes", response_model=ClassSection)
async def create_class_section(data: ClassSectionCreate):
    existing = await db.classes.find_one({"className": data.className}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Class already exists")
    obj = ClassSection(**data.model_dump())
    doc = obj.model_dump()
    doc['createdAt'] = doc['createdAt'].isoformat()
    await db.classes.insert_one(doc)
    return obj

@router.get("/classes")
async def get_classes():
    return await db.classes.find({}, {"_id": 0}).to_list(100)

@router.put("/classes/{class_id}")
async def update_class_section(class_id: str, data: ClassSectionCreate):
    result = await db.classes.update_one({"id": class_id}, {"$set": {"className": data.className, "sections": data.sections}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    return await db.classes.find_one({"id": class_id}, {"_id": 0})

@router.delete("/classes/{class_id}")
async def delete_class_section(class_id: str):
    result = await db.classes.delete_one({"id": class_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted"}

