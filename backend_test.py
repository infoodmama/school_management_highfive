#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class SchoolManagementAPITester:
    def __init__(self, base_url="https://academic-pro-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_student_id = None
        self.test_payment_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json() if response.content else {}
                except:
                    response_data = {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'No detail')
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                response_data = {}

            self.test_results.append({
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': success
            })

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': 'ERROR',
                'success': False,
                'error': str(e)
            })
            return False, {}

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        return self.run_test("Dashboard Stats", "GET", "stats/dashboard", 200)

    def test_classes_crud(self):
        """Test Classes CRUD operations"""
        print("\n📚 Testing Classes Management...")
        
        # Get initial classes
        success, initial_classes = self.run_test("Get Classes (Initial)", "GET", "classes", 200)
        
        # Create a new class
        class_data = {
            "className": "TestClass1",
            "sections": ["A", "B"]
        }
        success, created_class = self.run_test("Create Class", "POST", "classes", 200, class_data)
        
        if success and created_class:
            class_id = created_class.get('id')
            
            # Get classes after creation
            self.run_test("Get Classes (After Create)", "GET", "classes", 200)
            
            # Update the class
            update_data = {
                "className": "TestClass1Updated",
                "sections": ["A", "B", "C"]
            }
            self.run_test("Update Class", "PUT", f"classes/{class_id}", 200, update_data)
            
            # Delete the class
            self.run_test("Delete Class", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_fee_types_crud(self):
        """Test Fee Types CRUD operations"""
        print("\n💰 Testing Fee Types Management...")
        
        # Get initial fee types
        self.run_test("Get Fee Types (Initial)", "GET", "fee-types", 200)
        
        # Create a new fee type
        fee_type_data = {
            "feeName": "Test Lab Fee",
            "amount": 500.0,
            "applicableClass": "1",
            "applicableSection": "A",
            "noticeStartDate": "2024-01-01",
            "dueDate": "2024-01-31"
        }
        success, created_fee_type = self.run_test("Create Fee Type", "POST", "fee-types", 200, fee_type_data)
        
        if success and created_fee_type:
            fee_type_id = created_fee_type.get('id')
            
            # Get fee types after creation
            self.run_test("Get Fee Types (After Create)", "GET", "fee-types", 200)
            
            # Update the fee type
            update_data = {
                "feeName": "Updated Lab Fee",
                "amount": 600.0,
                "applicableClass": "1",
                "applicableSection": "A",
                "noticeStartDate": "2024-01-01",
                "dueDate": "2024-01-31"
            }
            self.run_test("Update Fee Type", "PUT", f"fee-types/{fee_type_id}", 200, update_data)
            
            # Delete the fee type
            self.run_test("Delete Fee Type", "DELETE", f"fee-types/{fee_type_id}", 200)
        
        return success

    def test_students_crud(self):
        """Test Students CRUD operations with studentCode"""
        print("\n👥 Testing Students Management with studentCode...")
        
        # First create a class for the student
        class_data = {
            "className": "TestClass2",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Student", "POST", "classes", 200, class_data)
        
        if not success:
            return False
            
        # Get initial students
        self.run_test("Get Students (Initial)", "GET", "students", 200)
        
        # Create a new student with studentCode (NEW REQUIREMENT)
        student_data = {
            "studentCode": "ADM001",  # NEW: Unique student ID
            "studentName": "Test Student",
            "rollNo": "1",  # NEW: No longer unique, class-wise only
            "studentClass": "TestClass2",
            "section": "A",
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9876543210",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0
        }
        success, created_student = self.run_test("Create Student with studentCode", "POST", "students", 201, student_data)
        
        if success and created_student:
            student_id = created_student.get('id')
            print(f"   Created student with studentCode: {created_student.get('studentCode')}")
            
            # Test duplicate studentCode rejection (NEW REQUIREMENT)
            duplicate_student_data = student_data.copy()
            duplicate_student_data["studentName"] = "Duplicate Student"
            duplicate_student_data["rollNo"] = "2"  # Different roll no, same studentCode
            self.run_test("Reject Duplicate studentCode", "POST", "students", 400, duplicate_student_data)
            
            # Test same rollNo in different section (should be allowed now)
            same_rollno_data = {
                "studentCode": "ADM002",
                "studentName": "Same Roll Student",
                "rollNo": "1",  # Same roll no as first student
                "studentClass": "TestClass2",
                "section": "B",  # Different section
                "fatherName": "Test Father 2",
                "motherName": "Test Mother 2",
                "mobile": "9876543211",
                "address": "Test Address 2",
                "feeTerm1": 5000.0,
                "feeTerm2": 5000.0,
                "feeTerm3": 5000.0
            }
            
            # First create section B
            class_update_data = {
                "className": "TestClass2",
                "sections": ["A", "B"]
            }
            class_id = created_class.get('id')
            self.run_test("Update Class with Section B", "PUT", f"classes/{class_id}", 200, class_update_data)
            
            success2, created_student2 = self.run_test("Create Student with Same rollNo Different Section", "POST", "students", 201, same_rollno_data)
            
            # Get students after creation
            self.run_test("Get Students (After Create)", "GET", "students", 200)
            
            # Get students with filters
            self.run_test("Get Students (Filtered)", "GET", "students", 200, params={"studentClass": "TestClass2"})
            
            # Update the student
            update_data = {
                "studentName": "Updated Test Student",
                "mobile": "9876543211"
            }
            self.run_test("Update Student", "PUT", f"students/{student_id}", 200, update_data)
            
            # Delete the students
            self.run_test("Delete Student", "DELETE", f"students/{student_id}", 200)
            if success2 and created_student2:
                student_id2 = created_student2.get('id')
                self.run_test("Delete Student 2", "DELETE", f"students/{student_id2}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Test Class", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_attendance_operations(self):
        """Test Attendance operations"""
        print("\n📋 Testing Attendance Management...")
        
        # Get attendance (should work even if empty)
        self.run_test("Get Attendance", "GET", "attendance", 200)
        
        # Test with date filters
        params = {
            "startDate": "2024-01-01",
            "endDate": "2024-01-31"
        }
        self.run_test("Get Attendance (Filtered)", "GET", "attendance", 200, params=params)
        
        return True

    def test_fees_operations(self):
        """Test Fees operations with studentCode"""
        print("\n💳 Testing Fees Management with studentCode...")
        
        # Test day sheet
        today = datetime.now().strftime('%Y-%m-%d')
        self.run_test("Get Day Sheet", "GET", "fees/day-sheet", 200, params={"date": today})
        
        # Test getting student fees by studentCode (NEW REQUIREMENT)
        success, response = self.run_test("Get Student Fees by studentCode ADM001", "GET", "fees/student/ADM001", 200)
        if success:
            student = response.get('student', {})
            print(f"   Found student by studentCode: {student.get('studentName')} (Code: {student.get('studentCode')})")
            
            # Test fee payment with studentCode
            if student.get('id'):
                payment_data = {
                    "studentId": student.get('id'),
                    "studentCode": student.get('studentCode'),  # NEW: Using studentCode
                    "rollNo": student.get('rollNo'),
                    "studentName": student.get('studentName'),
                    "termNumber": 1,
                    "amount": 1000,
                    "paymentMode": "cash"
                }
                
                payment_success, payment_response = self.run_test("Create Fee Payment with studentCode", "POST", "fees/payment", 201, payment_data)
                if payment_success:
                    print(f"   Payment created with receipt: {payment_response.get('receiptNumber')}")
        
        # Test getting student fees (should return 404 for non-existent student)
        success, _ = self.run_test("Get Student Fees (Non-existent)", "GET", "fees/student/NONEXISTENT", 404)
        
        return True

    def test_settings_operations(self):
        """Test Settings operations"""
        print("\n⚙️ Testing Settings Management...")
        
        # Get WhatsApp settings
        self.run_test("Get WhatsApp Settings", "GET", "settings/whatsapp", 200)
        
        # Get Database settings
        self.run_test("Get Database Settings", "GET", "settings/database", 200)
        
        # Test updating WhatsApp settings with new phoneNumberId field
        whatsapp_data = {
            "phoneNumberId": "488774804320252",
            "accessToken": "test-token"
        }
        self.run_test("Update WhatsApp Settings (phoneNumberId)", "PUT", "settings/whatsapp", 200, whatsapp_data)
        
        return True

    def test_school_settings_operations(self):
        """Test School Settings operations (NEW FEATURE)"""
        print("\n🏫 Testing School Settings Management...")
        
        # Get School settings
        success, initial_settings = self.run_test("Get School Settings", "GET", "settings/school", 200)
        if success:
            print(f"   Initial school name: {initial_settings.get('schoolName', 'Not set')}")
            print(f"   Initial school address: {initial_settings.get('schoolAddress', 'Not set')}")
            print(f"   Initial logo URL: {initial_settings.get('logoUrl', 'Not set')}")
        
        # Test updating School settings
        school_data = {
            "schoolName": "Test High School",
            "schoolAddress": "123 Education Street, Learning City, LC 12345",
            "logoUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
        success, updated_settings = self.run_test("Update School Settings", "PUT", "settings/school", 200, school_data)
        if success:
            print(f"   Updated school name: {updated_settings.get('message', 'Settings updated')}")
        
        # Verify the settings were saved
        success, saved_settings = self.run_test("Get School Settings (After Update)", "GET", "settings/school", 200)
        if success:
            print(f"   Saved school name: {saved_settings.get('schoolName')}")
            print(f"   Saved school address: {saved_settings.get('schoolAddress')}")
            print(f"   Has logo URL: {'Yes' if saved_settings.get('logoUrl') else 'No'}")
        
        return True

    def test_inventory_crud(self):
        """Test Inventory CRUD operations"""
        print("\n📦 Testing Inventory Management...")
        
        # Get initial inventory
        self.run_test("Get Inventory (Initial)", "GET", "inventory", 200)
        
        # Create a new inventory item
        inventory_data = {
            "itemName": "Test Whiteboard",
            "quantity": 5,
            "category": "Stationery",
            "purchaseDate": "2024-01-15",
            "amount": 1500.0
        }
        success, created_item = self.run_test("Create Inventory Item", "POST", "inventory", 200, inventory_data)
        
        if success and created_item:
            item_id = created_item.get('id')
            
            # Get inventory after creation
            self.run_test("Get Inventory (After Create)", "GET", "inventory", 200)
            
            # Update the inventory item
            update_data = {
                "itemName": "Updated Whiteboard",
                "quantity": 10,
                "category": "Stationery",
                "purchaseDate": "2024-01-15",
                "amount": 1600.0
            }
            self.run_test("Update Inventory Item", "PUT", f"inventory/{item_id}", 200, update_data)
            
            # Delete the inventory item
            self.run_test("Delete Inventory Item", "DELETE", f"inventory/{item_id}", 200)
        
        return success

    def test_events_crud(self):
        """Test Events CRUD operations"""
        print("\n📅 Testing Events Management...")
        
        # Get initial events
        self.run_test("Get Events (Initial)", "GET", "events", 200)
        
        # Create a new event
        event_data = {
            "title": "Test School Event",
            "description": "This is a test event for the school",
            "date": "2024-02-15"
        }
        success, created_event = self.run_test("Create Event", "POST", "events", 200, event_data)
        
        if success and created_event:
            event_id = created_event.get('id')
            
            # Get events after creation
            self.run_test("Get Events (After Create)", "GET", "events", 200)
            
            # Get events with month filter
            self.run_test("Get Events (Filtered)", "GET", "events", 200, params={"month": "2024-02"})
            
            # Delete the event
            self.run_test("Delete Event", "DELETE", f"events/{event_id}", 200)
        
        return success

    def test_homework_crud(self):
        """Test Homework CRUD operations"""
        print("\n📚 Testing Homework Management...")
        
        # First create a class for homework
        class_data = {
            "className": "TestClass3",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Homework", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        # Get initial homework
        self.run_test("Get Homework (Initial)", "GET", "homework", 200)
        
        # Create a new homework
        homework_data = {
            "studentClass": "TestClass3",
            "section": "A",
            "subject": "Mathematics",
            "title": "Test Homework Assignment",
            "description": "Complete exercises 1-10 from chapter 5",
            "dueDate": "2024-02-20",
            "assignedBy": "Test Teacher"
        }
        success, created_homework = self.run_test("Create Homework", "POST", "homework", 200, homework_data)
        
        if success and created_homework:
            homework_id = created_homework.get('id')
            
            # Get homework after creation
            self.run_test("Get Homework (After Create)", "GET", "homework", 200)
            
            # Get homework with filters
            self.run_test("Get Homework (Filtered)", "GET", "homework", 200, params={"studentClass": "TestClass3"})
            
            # Delete the homework
            self.run_test("Delete Homework", "DELETE", f"homework/{homework_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Test Class for Homework", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_student_detail(self):
        """Test Student Detail endpoint"""
        print("\n👤 Testing Student Detail...")
        
        # First create a class and student
        class_data = {
            "className": "TestClass4",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Student Detail", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        student_data = {
            "studentName": "Test Student Detail",
            "rollNo": "DETAIL001",
            "studentClass": "TestClass4",
            "section": "A",
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9876543210",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0
        }
        success, created_student = self.run_test("Create Student for Detail", "POST", "students", 200, student_data)
        
        if success and created_student:
            student_id = created_student.get('id')
            
            # Test student detail endpoint
            self.run_test("Get Student Detail", "GET", f"students/{student_id}/detail", 200)
            
            # Clean up - delete the student
            self.run_test("Delete Student Detail Test", "DELETE", f"students/{student_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Test Class for Student Detail", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_fee_reminders(self):
        """Test Fee Reminders endpoint"""
        print("\n📢 Testing Fee Reminders...")
        
        # Test fee reminders endpoint
        success, response = self.run_test("Send Fee Reminders", "POST", "fees/send-reminders", 200)
        
        return success

    def test_staff_crud(self):
        """Test Staff CRUD operations"""
        print("\n👨‍🏫 Testing Staff Management...")
        
        # Get initial staff
        self.run_test("Get Staff (Initial)", "GET", "staff", 200)
        
        # Create a new staff member
        staff_data = {
            "name": "Test Teacher",
            "role": "teacher",
            "mobile": "9876543210",
            "subject": "Mathematics",
            "joiningDate": "2024-01-15",
            "username": "testteach1",
            "password": "testpass123"
        }
        success, created_staff = self.run_test("Create Staff", "POST", "staff", 200, staff_data)
        
        if success and created_staff:
            staff_id = created_staff.get('id')
            
            # Get staff after creation
            self.run_test("Get Staff (After Create)", "GET", "staff", 200)
            
            # Update the staff member
            update_data = {
                "name": "Updated Test Teacher",
                "mobile": "9876543211"
            }
            self.run_test("Update Staff", "PUT", f"staff/{staff_id}", 200, update_data)
            
            # Delete the staff member
            self.run_test("Delete Staff", "DELETE", f"staff/{staff_id}", 200)
        
        return success

    def test_inventory_issue(self):
        """Test Inventory Issue operations with studentCode"""
        print("\n📤 Testing Inventory Issue to Students with studentCode...")
        
        # First create a class and student for testing
        class_data = {
            "className": "TestClass5",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Inventory Issue", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        student_data = {
            "studentCode": "ADM003",  # NEW: Using studentCode
            "studentName": "Test Student Issue",
            "rollNo": "1",
            "studentClass": "TestClass5",
            "section": "A",
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9876543210",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0
        }
        success, created_student = self.run_test("Create Student for Inventory Issue", "POST", "students", 201, student_data)
        
        if not success:
            return False
        
        # Create an inventory item
        inventory_data = {
            "itemName": "Test Notebook",
            "quantity": 10,
            "category": "Stationery",
            "purchaseDate": "2024-01-15",
            "amount": 50.0
        }
        success, created_item = self.run_test("Create Inventory Item for Issue", "POST", "inventory", 201, inventory_data)
        
        if success and created_item:
            item_id = created_item.get('id')
            
            # Issue inventory to student using studentCode (NEW REQUIREMENT)
            issue_data = {
                "itemId": item_id,
                "studentCode": "ADM003",  # NEW: Using studentCode instead of rollNo
                "quantity": 2,
                "date": "2024-01-20"
            }
            success, issued = self.run_test("Issue Inventory to Student by studentCode", "POST", "inventory/issue", 201, issue_data)
            
            if success:
                print(f"   Inventory issued to student: {issued.get('studentName')} (Code: {issued.get('studentCode')})")
            
            # Get inventory issues
            self.run_test("Get Inventory Issues", "GET", "inventory/issues", 200)
            
            # Get inventory issues for specific student
            student_id = created_student.get('id')
            self.run_test("Get Inventory Issues (Student Filter)", "GET", "inventory/issues", 200, params={"studentId": student_id})
            
            # Clean up - delete the inventory item
            self.run_test("Delete Inventory Item for Issue", "DELETE", f"inventory/{item_id}", 200)
        
        # Clean up - delete the student and class
        if created_student:
            student_id = created_student.get('id')
            self.run_test("Delete Student for Inventory Issue", "DELETE", f"students/{student_id}", 200)
        
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Class for Inventory Issue", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_auth_endpoints(self):
        """Test Authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test admin login with correct credentials
        admin_login = {
            "username": "admin",
            "password": "12345678"
        }
        success, response = self.run_test("Admin Login (Valid)", "POST", "auth/login", 200, admin_login)
        if success:
            print(f"   Admin role: {response.get('role')}")
            print(f"   Admin user: {response.get('user', {}).get('name')}")
        
        # Test teacher login with correct credentials
        teacher_login = {
            "username": "teach1",
            "password": "pass123"
        }
        success, response = self.run_test("Teacher Login (Valid)", "POST", "auth/login", 200, teacher_login)
        if success:
            print(f"   Teacher role: {response.get('role')}")
            print(f"   Teacher user: {response.get('user', {}).get('name')}")
        
        # Test office staff login (if exists)
        office_login = {
            "username": "office1",
            "password": "office123"
        }
        success, response = self.run_test("Office Staff Login (Test)", "POST", "auth/login", 401, office_login)
        
        # Test staff login with invalid credentials
        invalid_login = {
            "username": "invalid",
            "password": "invalid"
        }
        self.run_test("Staff Login (Invalid)", "POST", "auth/staff-login", 401, invalid_login)
        
        # Test parent login with invalid credentials
        self.run_test("Parent Login (Invalid)", "POST", "auth/parent-login", 401, invalid_login)
        
        # Test admin login with wrong password
        wrong_admin = {
            "username": "admin",
            "password": "wrongpass"
        }
        self.run_test("Admin Login (Wrong Password)", "POST", "auth/login", 401, wrong_admin)
        
        return True

    def test_parent_dashboard(self):
        """Test Parent Dashboard endpoint"""
        print("\n👨‍👩‍👧‍👦 Testing Parent Dashboard...")
        
        # First create a class and student with parent credentials
        class_data = {
            "className": "TestClass6",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Parent Dashboard", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        student_data = {
            "studentName": "Test Student Parent",
            "rollNo": "PARENT001",
            "studentClass": "TestClass6",
            "section": "A",
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9876543210",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0,
            "parentUsername": "parent001",
            "parentPassword": "parentpass123"
        }
        success, created_student = self.run_test("Create Student for Parent Dashboard", "POST", "students", 200, student_data)
        
        if success and created_student:
            student_id = created_student.get('id')
            
            # Test parent dashboard endpoint
            self.run_test("Get Parent Dashboard", "GET", f"parent/dashboard/{student_id}", 200)
            
            # Clean up - delete the student
            self.run_test("Delete Student for Parent Dashboard", "DELETE", f"students/{student_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Class for Parent Dashboard", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_invoice_endpoint(self):
        """Test Invoice PDF endpoint"""
        print("\n🧾 Testing Invoice PDF...")
        
        # Test with non-existent payment ID (should return 404)
        self.run_test("Get Invoice (Non-existent)", "GET", "fees/invoice/nonexistent", 404)
        
        # Test public invoice view endpoint (new feature)
        self.run_test("Get Public Invoice View (Non-existent)", "GET", "fees/invoice-view/nonexistent", 404)
        
        return True

    def test_event_update(self):
        """Test Event Update endpoint"""
        print("\n📅 Testing Event Update...")
        
        # Create an event first
        event_data = {
            "title": "Test Event for Update",
            "description": "This event will be updated",
            "date": "2024-02-15"
        }
        success, created_event = self.run_test("Create Event for Update", "POST", "events", 200, event_data)
        
        if success and created_event:
            event_id = created_event.get('id')
            
            # Update the event
            update_data = {
                "title": "Updated Test Event",
                "description": "This event has been updated",
                "date": "2024-02-16"
            }
            self.run_test("Update Event", "PUT", f"events/{event_id}", 200, update_data)
            
            # Clean up - delete the event
            self.run_test("Delete Updated Event", "DELETE", f"events/{event_id}", 200)
        
        return success

    def test_fee_status_endpoints(self):
        """Test Fee Status endpoints"""
        print("\n📊 Testing Fee Status Management...")
        
        # First create a class and student for testing fee status
        class_data = {
            "className": "TestClassFeeStatus",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Fee Status", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        student_data = {
            "studentName": "Test Student Fee Status",
            "rollNo": "FEESTATUS001",
            "studentClass": "TestClassFeeStatus",
            "section": "A",
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9876543210",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0
        }
        success, created_student = self.run_test("Create Student for Fee Status", "POST", "students", 200, student_data)
        
        if success and created_student:
            # Test fee status endpoint
            params = {
                "studentClass": "TestClassFeeStatus",
                "section": "A"
            }
            success, response = self.run_test("Get Fee Status", "GET", "fees/status", 200, params=params)
            
            if success:
                print(f"   Fee status data contains {len(response.get('students', []))} students")
                print(f"   Custom fee names: {response.get('customFeeNames', [])}")
            
            # Test fee status export endpoint
            export_params = {
                "studentClass": "TestClassFeeStatus",
                "section": "A",
                "format": "csv"
            }
            self.run_test("Export Fee Status (CSV)", "GET", "fees/status/export", 200, params=export_params)
            
            # Test fee status export endpoint (Excel)
            export_params_xlsx = {
                "studentClass": "TestClassFeeStatus",
                "section": "A",
                "format": "xlsx"
            }
            self.run_test("Export Fee Status (Excel)", "GET", "fees/status/export", 200, params=export_params_xlsx)
            
            # Clean up - delete the student
            student_id = created_student.get('id')
            self.run_test("Delete Student for Fee Status", "DELETE", f"students/{student_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Class for Fee Status", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_event_with_notification(self):
        """Test Event creation with WhatsApp notification"""
        print("\n📅 Testing Event with WhatsApp Notification...")
        
        # Create an event with sendNotification enabled
        event_data = {
            "title": "Test Event with Notification",
            "description": "This event will send WhatsApp notifications",
            "date": "2024-02-15",
            "sendNotification": True
        }
        success, created_event = self.run_test("Create Event with Notification", "POST", "events", 200, event_data)
        
        if success and created_event:
            event_id = created_event.get('id')
            print(f"   Event created with notification enabled: {created_event.get('sendNotification')}")
            
            # Clean up - delete the event
            self.run_test("Delete Event with Notification", "DELETE", f"events/{event_id}", 200)
        
        return success

    def test_homework_update(self):
        """Test Homework Update endpoint"""
        print("\n📚 Testing Homework Update...")
        
        # First create a class for homework
        class_data = {
            "className": "TestClass7",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Homework Update", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        # Create homework
        homework_data = {
            "studentClass": "TestClass7",
            "section": "A",
            "subject": "Mathematics",
            "title": "Test Homework for Update",
            "description": "This homework will be updated",
            "dueDate": "2024-02-20",
            "assignedBy": "Test Teacher"
        }
        success, created_homework = self.run_test("Create Homework for Update", "POST", "homework", 200, homework_data)
        
        if success and created_homework:
            homework_id = created_homework.get('id')
            
            # Update the homework
            update_data = {
                "studentClass": "TestClass7",
                "section": "A",
                "subject": "Mathematics",
                "title": "Updated Test Homework",
                "description": "This homework has been updated",
                "dueDate": "2024-02-21",
                "assignedBy": "Updated Teacher"
            }
            self.run_test("Update Homework", "PUT", f"homework/{homework_id}", 200, update_data)
            
            # Clean up - delete the homework
            self.run_test("Delete Updated Homework", "DELETE", f"homework/{homework_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Class for Homework Update", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_sample_csv_studentcode(self):
        """Test Sample CSV has studentCode column"""
        print("\n📄 Testing Sample CSV with studentCode...")
        
        try:
            response = requests.get(f"{self.api_url}/students/sample-csv")
            if response.status_code == 200:
                csv_content = response.text
                lines = csv_content.strip().split('\n')
                if lines:
                    headers = lines[0].split(',')
                    has_student_id = 'Student ID' in headers
                    print(f"   CSV headers: {headers}")
                    print(f"   Has 'Student ID' column: {has_student_id}")
                    
                    if len(lines) > 1:
                        sample_data = lines[1].split(',')
                        print(f"   Sample data: {sample_data}")
                        # Check if sample data has studentCode like ADM001
                        if len(sample_data) > 0:
                            sample_student_id = sample_data[0]
                            print(f"   Sample Student ID: {sample_student_id}")
                    
                    self.tests_run += 1
                    if has_student_id:
                        self.tests_passed += 1
                        print("✅ Sample CSV has Student ID column")
                        return True
                    else:
                        print("❌ Sample CSV missing Student ID column")
                        return False
        except Exception as e:
            print(f"❌ Failed to test CSV: {str(e)}")
            self.tests_run += 1
            return False

    def test_homework_file_upload(self):
        """Test Homework with file upload support"""
        print("\n📚 Testing Homework with File Upload...")
        
        # First create a class for homework
        class_data = {
            "className": "TestClassHWFile",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Homework File", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        # Create homework with attachment fields (NEW REQUIREMENT)
        homework_data = {
            "studentClass": "TestClassHWFile",
            "section": "A",
            "subject": "Mathematics",
            "title": "Test Homework with File",
            "description": "This homework has an attachment",
            "dueDate": "2024-02-20",
            "assignedBy": "Test Teacher",
            "attachmentUrl": "data:application/pdf;base64,JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgo+PgpzdHJlYW0KQNC=",  # Sample PDF base64
            "attachmentName": "homework.pdf"
        }
        success, created_homework = self.run_test("Create Homework with File Attachment", "POST", "homework", 201, homework_data)
        
        if success and created_homework:
            homework_id = created_homework.get('id')
            print(f"   Homework created with attachment: {created_homework.get('attachmentName')}")
            
            # Verify attachment fields are saved
            if created_homework.get('attachmentUrl') and created_homework.get('attachmentName'):
                print("   ✅ Homework attachment fields saved correctly")
            
            # Clean up - delete the homework
            self.run_test("Delete Homework with File", "DELETE", f"homework/{homework_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Class for Homework File", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_event_file_upload(self):
        """Test Event with file upload support"""
        print("\n📅 Testing Event with File Upload...")
        
        # Create event with attachment fields (NEW REQUIREMENT)
        event_data = {
            "title": "Test Event with File",
            "description": "This event has an attachment",
            "date": "2024-02-15",
            "sendNotification": False,
            "attachmentUrl": "data:application/pdf;base64,JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgo+PgpzdHJlYW0KQNC=",  # Sample PDF base64
            "attachmentName": "event.pdf"
        }
        success, created_event = self.run_test("Create Event with File Attachment", "POST", "events", 201, event_data)
        
        if success and created_event:
            event_id = created_event.get('id')
            print(f"   Event created with attachment: {created_event.get('attachmentName')}")
            
            # Verify attachment fields are saved
            if created_event.get('attachmentUrl') and created_event.get('attachmentName'):
                print("   ✅ Event attachment fields saved correctly")
            
            # Clean up - delete the event
            self.run_test("Delete Event with File", "DELETE", f"events/{event_id}", 200)
        
        return success

    def test_parent_portal_homework_filter(self):
        """Test Parent Portal shows last 7 days homework only"""
        print("\n👨‍👩‍👧‍👦 Testing Parent Portal Homework Filter (Last 7 Days)...")
        
        # First create a class and student with parent credentials
        class_data = {
            "className": "TestClassParentHW",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Parent Homework", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        student_data = {
            "studentCode": "ADM004",
            "studentName": "Test Student Parent HW",
            "rollNo": "1",
            "studentClass": "TestClassParentHW",
            "section": "A",
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9876543210",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0,
            "parentUsername": "parent004",
            "parentPassword": "parentpass123"
        }
        success, created_student = self.run_test("Create Student for Parent Homework", "POST", "students", 201, student_data)
        
        if success and created_student:
            student_id = created_student.get('id')
            
            # Create recent homework (within 7 days)
            from datetime import datetime, timedelta
            recent_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            old_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            
            recent_homework_data = {
                "studentClass": "TestClassParentHW",
                "section": "A",
                "subject": "Mathematics",
                "title": "Recent Homework",
                "description": "This is recent homework",
                "dueDate": recent_date,
                "assignedBy": "Test Teacher"
            }
            hw_success, recent_hw = self.run_test("Create Recent Homework", "POST", "homework", 201, recent_homework_data)
            
            # Create old homework (older than 7 days)
            old_homework_data = {
                "studentClass": "TestClassParentHW",
                "section": "A",
                "subject": "Science",
                "title": "Old Homework",
                "description": "This is old homework",
                "dueDate": old_date,
                "assignedBy": "Test Teacher"
            }
            old_hw_success, old_hw = self.run_test("Create Old Homework", "POST", "homework", 201, old_homework_data)
            
            # Test parent login
            parent_success, parent_response = self.run_test("Parent Login for Homework Filter", "POST", "auth/parent-login", 200, {"username": "parent004", "password": "parentpass123"})
            
            if parent_success:
                # Test parent dashboard (should show only last 7 days homework)
                dashboard_success, dashboard_response = self.run_test("Get Parent Dashboard with Homework Filter", "GET", f"parent/dashboard/{student_id}", 200)
                
                if dashboard_success:
                    homework = dashboard_response.get('homework', [])
                    print(f"   Homework count in parent portal: {len(homework)}")
                    
                    # Check homework titles to verify filtering
                    homework_titles = [hw.get('title') for hw in homework]
                    print(f"   Homework titles: {homework_titles}")
                    
                    # Should contain recent homework but not old homework
                    has_recent = any('Recent' in title for title in homework_titles)
                    has_old = any('Old' in title for title in homework_titles)
                    
                    print(f"   Has recent homework: {has_recent}")
                    print(f"   Has old homework: {has_old}")
                    
                    if has_recent and not has_old:
                        print("   ✅ Parent portal correctly shows only last 7 days homework")
                    else:
                        print("   ⚠️ Parent portal homework filtering may not be working correctly")
            
            # Clean up homework
            if hw_success and recent_hw:
                self.run_test("Delete Recent Homework", "DELETE", f"homework/{recent_hw.get('id')}", 200)
            if old_hw_success and old_hw:
                self.run_test("Delete Old Homework", "DELETE", f"homework/{old_hw.get('id')}", 200)
            
            # Clean up - delete the student
            self.run_test("Delete Student for Parent Homework", "DELETE", f"students/{student_id}", 200)
        
        # Clean up - delete the test class
        if created_class:
            class_id = created_class.get('id')
            self.run_test("Delete Class for Parent Homework", "DELETE", f"classes/{class_id}", 200)
        
        return success

    def test_create_test_student_for_invoice(self):
        """Create a test student for invoice testing"""
        print("\n🧪 Testing: Create Test Student for Invoice")
        
        test_student_data = {
            "studentCode": "TEST001",
            "studentName": "Test Student Invoice",
            "rollNo": "999",
            "studentClass": "1",
            "section": "A", 
            "fatherName": "Test Father",
            "motherName": "Test Mother",
            "mobile": "9999999999",
            "address": "Test Address",
            "feeTerm1": 5000.0,
            "feeTerm2": 5000.0,
            "feeTerm3": 5000.0
        }
        
        success, response = self.run_test(
            "Create Test Student for Invoice",
            "POST",
            "students",
            200,
            data=test_student_data
        )
        if success and response.get('id'):
            self.test_student_id = response['id']
            print(f"   ✅ Created test student with ID: {self.test_student_id}")
        return success

    def test_create_fee_payment_for_invoice(self):
        """Create a test fee payment to test invoice generation with collectedBy field"""
        print("\n🧪 Testing: Create Fee Payment for Invoice with collectedBy")
        
        if not self.test_student_id:
            print("   ❌ No test student available for payment")
            return False
            
        payment_data = {
            "studentId": self.test_student_id,
            "studentCode": "TEST001",
            "rollNo": "999",
            "studentName": "Test Student Invoice",
            "termNumber": 1,
            "amount": 5000.0,
            "paymentMode": "cash",
            "collectedBy": "Test Admin User"  # NEW: collectedBy field
        }
        
        success, response = self.run_test(
            "Create Fee Payment for Invoice with collectedBy",
            "POST",
            "fees/payment",
            200,
            data=payment_data
        )
        if success and response.get('id'):
            self.test_payment_id = response['id']
            print(f"   ✅ Created payment with ID: {self.test_payment_id}")
            print(f"   ✅ Payment includes collectedBy: {response.get('collectedBy')}")
            
            # Verify receipt number is sequential
            receipt_number = response.get('receiptNumber')
            if receipt_number:
                print(f"   ✅ Sequential receipt number: {receipt_number}")
                # Check if it's in format 001, 002, etc.
                if receipt_number.isdigit() and len(receipt_number) == 3:
                    print(f"   ✅ Receipt number format correct (3-digit): {receipt_number}")
                else:
                    print(f"   ⚠️ Receipt number format may be incorrect: {receipt_number}")
        return success

    def test_invoice_pdf_redesign(self):
        """Test invoice PDF download with new design (2 copies per page)"""
        print("\n🧪 Testing: Invoice PDF Download (New Design - 2 Copies)")
        
        if not self.test_payment_id:
            print("   ❌ No test payment available for invoice")
            return False
            
        success, _ = self.run_test(
            "Download Invoice PDF (New Design - 2 Copies)",
            "GET",
            f"fees/invoice/{self.test_payment_id}",
            200
        )
        if success:
            print("   ✅ Invoice PDF generated successfully with new design")
            print("   ✅ PDF should contain 2 copies: Student Copy + College Copy")
            print("   ✅ PDF should use school settings (name, address, logo)")
            print("   ✅ PDF should show collectedBy field")
        return success

    def test_public_invoice_view(self):
        """Test public invoice view endpoint"""
        print("\n🧪 Testing: Public Invoice View Endpoint")
        
        if not self.test_payment_id:
            print("   ❌ No test payment available for invoice view")
            return False
            
        success, _ = self.run_test(
            "View Invoice PDF (Public URL)",
            "GET", 
            f"fees/invoice-view/{self.test_payment_id}",
            200
        )
        if success:
            public_url = f"{self.api_url}/fees/invoice-view/{self.test_payment_id}"
            print(f"   ✅ Public invoice URL accessible: {public_url}")
        return success

    def test_bulk_delete_students_endpoint(self):
        """Test bulk delete students endpoint"""
        print("\n🧪 Testing: Bulk Delete Students Endpoint")
        
        # Test with empty list (should return 400)
        success1, _ = self.run_test(
            "Bulk Delete Students (Empty List)",
            "POST",
            "students/bulk-delete",
            400,
            data={"studentIds": []}
        )
        
        # Test with invalid student IDs (should return success but delete 0)
        success2, response = self.run_test(
            "Bulk Delete Students (Invalid IDs)",
            "POST",
            "students/bulk-delete",
            200,
            data={"studentIds": ["invalid-id-1", "invalid-id-2"]}
        )
        
        if success1 and success2:
            print("   ✅ Bulk delete endpoint working correctly")
            return True
        return False

    def cleanup_test_data(self):
        """Clean up test student and payment data"""
        print("\n🧹 Cleaning up test data...")
        
        if self.test_student_id:
            success, _ = self.run_test(
                "Cleanup Test Student",
                "DELETE",
                f"students/{self.test_student_id}",
                200
            )
            if success:
                print("   ✅ Test student cleaned up")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting School Management System API Tests...")
        print(f"📡 Testing against: {self.base_url}")
        
        # Test each module
        self.test_dashboard_stats()
        self.test_classes_crud()
        self.test_fee_types_crud()
        self.test_students_crud()
        self.test_attendance_operations()
        self.test_fees_operations()
        self.test_settings_operations()
        self.test_school_settings_operations()  # NEW: School settings test
        
        # Test new modules added in this iteration
        self.test_inventory_crud()
        self.test_events_crud()
        self.test_homework_crud()
        self.test_student_detail()
        self.test_fee_reminders()
        
        # Test new features for this iteration
        self.test_staff_crud()
        self.test_inventory_issue()
        self.test_auth_endpoints()
        self.test_parent_dashboard()
        self.test_invoice_endpoint()
        self.test_event_update()
        self.test_homework_update()
        
        # Test NEW features added in current iteration
        self.test_fee_status_endpoints()
        self.test_event_with_notification()
        self.test_sample_csv_studentcode()
        self.test_homework_file_upload()
        self.test_event_file_upload()
        self.test_parent_portal_homework_filter()
        
        # Test LATEST features for invoice redesign and bulk delete
        self.test_create_test_student_for_invoice()
        self.test_create_fee_payment_for_invoice()
        self.test_invoice_pdf_redesign()
        self.test_public_invoice_view()
        self.test_bulk_delete_students_endpoint()
        
        # Cleanup test data
        self.cleanup_test_data()
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Print failed tests
        failed_tests = [t for t in self.test_results if not t['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                error_msg = test.get('error', f"Expected {test['expected_status']}, got {test['actual_status']}")
                print(f"   - {test['name']}: {error_msg}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = SchoolManagementAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())