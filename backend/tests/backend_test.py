"""
Backend API tests for School Management System
Covers: Leave Requests, Bulk Concessions, Student Promotion (fee carryover),
Send Reminders endpoint, and regression checks (students, fees, attendance, homework).
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://academic-pro-6.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token(api_client):
    r = api_client.post(f"{API}/auth/login", json={"username": "admin", "password": "12345678"})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    data = r.json()
    # Backend returns {"success": true, "user": {...}, "role": "..."} with no token
    assert data.get("success") is True
    return data.get("role") or "super_admin"


@pytest.fixture(scope="session")
def test_student(api_client):
    """Create a dedicated test student to avoid polluting production data."""
    suffix = uuid.uuid4().hex[:6].upper()
    code = f"TSTLV{suffix}"
    payload = {
        "studentCode": code,
        "studentName": f"TEST_LeaveStudent_{suffix}",
        "studentClass": "TEST_CLASS_LV",
        "section": "A",
        "rollNo": f"R{suffix}",
        "mobile": "9999999999",
        "parentName": "TestParent",
        "fatherName": "TestFather",
        "motherName": "TestMother",
        "address": "TEST_address",
        "feeTerm1": 1000.0,
        "feeTerm2": 2000.0,
        "feeTerm3": 3000.0,
    }
    r = api_client.post(f"{API}/students", json=payload)
    assert r.status_code in (200, 201), f"Create student failed: {r.status_code} {r.text}"
    stu = r.json()
    yield stu
    # Cleanup
    try:
        api_client.delete(f"{API}/students/{stu['id']}")
    except Exception:
        pass


# ==================== Health & Auth ====================
class TestHealth:
    def test_login_admin(self, admin_token):
        assert admin_token is not None

    def test_login_invalid(self, api_client):
        r = api_client.post(f"{API}/auth/login", json={"username": "admin", "password": "wrong"})
        assert r.status_code in (400, 401, 403)


# ==================== Leave Requests ====================
class TestLeaveRequests:
    leave_id = None

    def test_create_leave_request(self, api_client, test_student):
        payload = {
            "studentId": test_student["id"],
            "studentCode": test_student["studentCode"],
            "studentName": test_student["studentName"],
            "fromDate": "2026-02-01",
            "toDate": "2026-02-03",
            "reason": "TEST_family_function",
        }
        r = api_client.post(f"{API}/leave-requests", json=payload)
        assert r.status_code in (200, 201), f"Create leave failed: {r.status_code} {r.text}"
        data = r.json()
        assert data["studentId"] == test_student["id"]
        assert data["status"] == "pending"
        assert data["reason"] == "TEST_family_function"
        assert "id" in data
        TestLeaveRequests.leave_id = data["id"]

    def test_get_pending_leaves(self, api_client):
        r = api_client.get(f"{API}/leave-requests", params={"status": "pending"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        ids = [x["id"] for x in data]
        assert TestLeaveRequests.leave_id in ids

    def test_filter_by_student(self, api_client, test_student):
        r = api_client.get(f"{API}/leave-requests", params={"studentId": test_student["id"]})
        assert r.status_code == 200
        data = r.json()
        assert all(x["studentId"] == test_student["id"] for x in data)
        assert len(data) >= 1

    def test_approve_leave(self, api_client):
        assert TestLeaveRequests.leave_id, "No leave id from creation step"
        r = api_client.post(
            f"{API}/leave-requests/{TestLeaveRequests.leave_id}/approve",
            json={"approvedBy": "TEST_admin"},
        )
        assert r.status_code == 200, r.text
        # Verify persistence
        g = api_client.get(f"{API}/leave-requests", params={"studentId": "__dummy__"})
        # Fetch all and find
        g2 = api_client.get(f"{API}/leave-requests")
        assert g2.status_code == 200
        found = next((x for x in g2.json() if x["id"] == TestLeaveRequests.leave_id), None)
        assert found is not None
        assert found["status"] == "approved"
        assert found.get("approvedBy") == "TEST_admin"

    def test_reject_leave(self, api_client, test_student):
        # Create another leave then reject it
        payload = {
            "studentId": test_student["id"],
            "studentCode": test_student["studentCode"],
            "studentName": test_student["studentName"],
            "fromDate": "2026-03-01",
            "toDate": "2026-03-02",
            "reason": "TEST_rejection_case",
        }
        c = api_client.post(f"{API}/leave-requests", json=payload)
        assert c.status_code in (200, 201)
        lid = c.json()["id"]
        r = api_client.post(f"{API}/leave-requests/{lid}/reject", json={"rejectedBy": "TEST_admin"})
        assert r.status_code == 200
        g = api_client.get(f"{API}/leave-requests")
        found = next((x for x in g.json() if x["id"] == lid), None)
        assert found and found["status"] == "rejected"

    def test_approve_nonexistent(self, api_client):
        r = api_client.post(f"{API}/leave-requests/nonexistent-id-xyz/approve", json={"approvedBy": "x"})
        assert r.status_code == 404


# ==================== Bulk Concessions ====================
class TestBulkConcessions:
    def test_bulk_concession_empty(self, api_client):
        r = api_client.post(f"{API}/concessions/bulk", json={
            "studentCodes": [],
            "concessionAmount": 100,
            "requestedBy": "TEST_admin",
        })
        assert r.status_code == 400

    def test_bulk_concession_create(self, api_client, test_student):
        payload = {
            "studentCodes": [test_student["studentCode"], "NONEXISTENT_CODE_XYZ"],
            "termNumber": 1,
            "concessionAmount": 250.0,
            "requestedBy": "TEST_admin",
        }
        r = api_client.post(f"{API}/concessions/bulk", json=payload)
        assert r.status_code in (200, 201), r.text
        data = r.json()
        assert data["created"] == 1
        assert test_student["studentCode"] in data["students"]
        assert len(data["errors"]) == 1
        # Verify the concession appears in list
        g = api_client.get(f"{API}/concessions", params={"status": "pending"})
        assert g.status_code == 200
        codes = [c.get("studentCode") for c in g.json()]
        assert test_student["studentCode"] in codes


# ==================== Promote Students (fee carryover) ====================
class TestPromoteFeeCarryover:
    def test_promote_carryover_to_term1(self, api_client):
        # Create a student in isolated class with known fees & one payment to create pending
        suffix = uuid.uuid4().hex[:6].upper()
        code = f"TSTPR{suffix}"
        payload = {
            "studentCode": code,
            "studentName": f"TEST_PromoteStudent_{suffix}",
            "studentClass": f"TEST_FROM_{suffix}",
            "section": "A",
            "rollNo": f"RP{suffix}",
            "mobile": "9888888888",
            "parentName": "TestParent",
            "fatherName": "TestFather",
            "motherName": "TestMother",
            "address": "TEST_address",
            "feeTerm1": 1000.0,
            "feeTerm2": 2000.0,
            "feeTerm3": 3000.0,
        }
        cr = api_client.post(f"{API}/students", json=payload)
        assert cr.status_code in (200, 201), cr.text
        stu = cr.json()
        try:
            # Pay 400 in term 1 (so term1 pending = 600)
            pay = {
                "studentId": stu["id"],
                "studentCode": code,
                "rollNo": stu.get("rollNo", f"RP{suffix}"),
                "studentName": stu["studentName"],
                "termNumber": 1,
                "amount": 400.0,
                "paymentMode": "cash",
                "collectedBy": "TEST_admin",
            }
            pr = api_client.post(f"{API}/fees/payment", json=pay)
            assert pr.status_code in (200, 201), pr.text

            # Promote
            from_class = payload["studentClass"]
            to_class = f"TEST_TO_{suffix}"
            pm = api_client.post(
                f"{API}/students/promote",
                json={"fromClass": from_class, "toClass": to_class},
            )
            assert pm.status_code == 200, pm.text
            assert "Promoted" in pm.json().get("message", "")

            # Verify student state post-promotion
            g = api_client.get(f"{API}/students", params={"limit": 50, "studentClass": to_class})
            assert g.status_code == 200
            # Fallback to fetch by id directly via list with search
            sg = api_client.get(f"{API}/students", params={"limit": 1000})
            assert sg.status_code == 200
            all_students = sg.json().get("students", [])
            found = next((s for s in all_students if s["id"] == stu["id"]), None)
            assert found is not None, "Student not found post-promotion"
            assert found["studentClass"] == to_class
            # Carryover: pending1=600, pending2=2000, pending3=3000 -> total 5600 in new Term1
            assert found["feeTerm1"] == 5600.0, f"Expected 5600 in new term1, got {found['feeTerm1']}"
            # Term2 and Term3 remain as old term2/term3 (fresh year)
            assert found["feeTerm2"] == 2000.0
            assert found["feeTerm3"] == 3000.0
            # previousYearDues info present
            pyd = found.get("previousYearDues")
            assert pyd and pyd.get("totalDues") == 5600.0
            assert pyd.get("fromClass") == from_class
        finally:
            try:
                api_client.delete(f"{API}/students/{stu['id']}")
            except Exception:
                pass

    def test_promote_no_students(self, api_client):
        r = api_client.post(f"{API}/students/promote", json={
            "fromClass": f"NONEXISTENT_{uuid.uuid4().hex[:6]}", "toClass": "X"
        })
        assert r.status_code == 404


# ==================== Send Reminders (regression) ====================
class TestSendReminders:
    def test_send_reminders_endpoint(self, api_client):
        # Route is POST /api/fees/send-reminders (task mentions GET but server.py defines POST)
        r = api_client.post(f"{API}/fees/send-reminders")
        assert r.status_code == 200, f"Send reminders failed: {r.status_code} {r.text}"
        data = r.json()
        assert "message" in data
        assert "feeTypesChecked" in data


# ==================== Regression Tests ====================
class TestRegression:
    def test_students_list(self, api_client):
        r = api_client.get(f"{API}/students", params={"limit": 5})
        assert r.status_code == 200
        data = r.json()
        assert "students" in data and "total" in data

    def test_fee_types_list(self, api_client):
        r = api_client.get(f"{API}/fee-types")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_attendance_get(self, api_client):
        r = api_client.get(f"{API}/attendance", params={"date": "2026-01-01"})
        assert r.status_code == 200

    def test_homework_list(self, api_client):
        r = api_client.get(f"{API}/homework")
        assert r.status_code == 200

    def test_expenses_list(self, api_client):
        r = api_client.get(f"{API}/expenses")
        assert r.status_code == 200

    def test_concessions_list(self, api_client):
        r = api_client.get(f"{API}/concessions")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_staff_list(self, api_client):
        r = api_client.get(f"{API}/staff")
        assert r.status_code == 200
