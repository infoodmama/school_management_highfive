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
        """Test Students CRUD operations"""
        print("\n👥 Testing Students Management...")
        
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
        
        # Create a new student
        student_data = {
            "studentName": "Test Student",
            "rollNo": "TEST001",
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
        success, created_student = self.run_test("Create Student", "POST", "students", 200, student_data)
        
        if success and created_student:
            student_id = created_student.get('id')
            
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
            
            # Delete the student
            self.run_test("Delete Student", "DELETE", f"students/{student_id}", 200)
        
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
        """Test Fees operations"""
        print("\n💳 Testing Fees Management...")
        
        # Test day sheet
        today = datetime.now().strftime('%Y-%m-%d')
        self.run_test("Get Day Sheet", "GET", "fees/day-sheet", 200, params={"date": today})
        
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
        
        # Test updating WhatsApp settings
        whatsapp_data = {
            "apiUrl": "https://test-api.example.com",
            "accessToken": "test-token"
        }
        self.run_test("Update WhatsApp Settings", "PUT", "settings/whatsapp", 200, whatsapp_data)
        
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
        """Test Inventory Issue operations"""
        print("\n📤 Testing Inventory Issue to Students...")
        
        # First create a class and student for testing
        class_data = {
            "className": "TestClass5",
            "sections": ["A"]
        }
        success, created_class = self.run_test("Create Class for Inventory Issue", "POST", "classes", 200, class_data)
        
        if not success:
            return False
        
        student_data = {
            "studentName": "Test Student Issue",
            "rollNo": "ISSUE001",
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
        success, created_student = self.run_test("Create Student for Inventory Issue", "POST", "students", 200, student_data)
        
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
        success, created_item = self.run_test("Create Inventory Item for Issue", "POST", "inventory", 200, inventory_data)
        
        if success and created_item:
            item_id = created_item.get('id')
            
            # Issue inventory to student
            issue_data = {
                "itemId": item_id,
                "rollNo": "ISSUE001",
                "quantity": 2,
                "date": "2024-01-20"
            }
            success, issued = self.run_test("Issue Inventory to Student", "POST", "inventory/issue", 200, issue_data)
            
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