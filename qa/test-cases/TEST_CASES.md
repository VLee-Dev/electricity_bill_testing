# Test Cases - Hệ thống tính tiền điện

## TC-001: Admin Login - Valid Credentials

**Priority**: High  
**Module**: Admin Authentication  
**Precondition**: Admin account exists (username: admin, password: admin123)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open admin login page | Login form displayed |
| 2 | Enter username "admin" | Username field populated |
| 3 | Enter password "admin123" | Password masked |
| 4 | Click "Đăng nhập" | Redirect to admin dashboard, JWT token stored |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  
**Tested By**: _____ **Date**: _____

---

## TC-002: Admin Login - Invalid Credentials

**Priority**: High  
**Module**: Admin Authentication  
**Precondition**: None

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open admin login page | Login form displayed |
| 2 | Enter username "admin" | Username field populated |
| 3 | Enter password "wrongpass" | Password masked |
| 4 | Click "Đăng nhập" | Error: "Tên đăng nhập hoặc mật khẩu không đúng" |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-003: Register Household - Valid Data

**Priority**: High  
**Module**: Household Management (FUNC-01)  
**Precondition**: Logged in as Admin

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to "Đăng ký hộ mới" | Registration form displayed |
| 2 | Enter customer_code "KH001" | Field populated |
| 3 | Enter full_name "Nguyễn Văn A" | Field populated |
| 4 | Enter address "123 Test St" | Field populated |
| 5 | Enter phone "0901234567" | Field populated |
| 6 | Enter email "test@example.com" | Field populated |
| 7 | Enter meter_number "MT001" | Field populated |
| 8 | Enter initial_password "123456" | Password masked |
| 9 | Click "Đăng ký" | Success message, household created, customer account auto-created |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-004: Register Household - Duplicate Customer Code

**Priority**: High  
**Module**: Household Management (FUNC-01)  
**Precondition**: Household with customer_code "KH001" exists

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to "Đăng ký hộ mới" | Registration form displayed |
| 2 | Enter customer_code "KH001" | Field populated |
| 3 | Fill other valid data | Fields populated |
| 4 | Click "Đăng ký" | Error: "Mã khách hàng đã tồn tại" (error_code: CUSTOMER_CODE_EXISTS) |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-005: Add Meter Reading - Valid Data

**Priority**: High  
**Module**: Meter Readings (FUNC-02)  
**Precondition**: Logged in as Admin, household KH001 exists with old_reading=100

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to "Nhập chỉ số" | Form displayed |
| 2 | Select household "KH001" | Household selected |
| 3 | Enter period "2026-09" | Period populated |
| 4 | Enter new_reading "250" | Reading populated |
| 5 | Click "Lưu" | Success message, consumption auto-calculated = 150 kWh |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-006: Add Meter Reading - Invalid (New < Old)

**Priority**: High  
**Module**: Meter Readings (FUNC-02)  
**Precondition**: Household with old_reading=200

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to "Nhập chỉ số" | Form displayed |
| 2 | Select household | Household selected |
| 3 | Enter period "2026-09" | Period populated |
| 4 | Enter new_reading "150" | Reading populated |
| 5 | Click "Lưu" | Error: "Chỉ số mới không được nhỏ hơn chỉ số cũ" |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-007: Calculate Invoice - Tier 1 Only (≤50 kWh)

**Priority**: High  
**Module**: Billing (FUNC-03)  
**Precondition**: Meter reading exists with consumption=50 kWh

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to meter readings list | List displayed |
| 2 | Click "Tính hóa đơn" for reading | Processing |
| 3 | View invoice details | Subtotal = 50×1678 = 83,900 VNĐ<br>VAT = 6,712 VNĐ<br>Total = 90,612 VNĐ<br>1 tier detail shown |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-008: Calculate Invoice - Multiple Tiers (150 kWh)

**Priority**: High  
**Module**: Billing (FUNC-03)  
**Precondition**: Meter reading with consumption=150 kWh

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Tính hóa đơn" | Processing |
| 2 | View invoice details | Tier 1: 50×1678 = 83,900<br>Tier 2: 50×1734 = 86,700<br>Tier 3: 50×2014 = 100,700<br>Subtotal = 271,300<br>VAT = 21,704<br>Total = 293,004<br>3 tier details |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-009: Customer Login - Valid Customer Code

**Priority**: High  
**Module**: Customer Authentication (FUNC-05)  
**Precondition**: Customer account exists (customer_code: KH001, password: 123456)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open customer login page | Login form displayed |
| 2 | Enter customer_code "KH001" | Field populated |
| 3 | Enter password "123456" | Password masked |
| 4 | Click "Đăng nhập" | Redirect to customer dashboard, JWT token stored |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-010: Customer View Invoices - Own Only

**Priority**: High  
**Module**: Customer Invoices (FUNC-09)  
**Precondition**: Logged in as customer KH001, invoices exist

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to "Hóa đơn của tôi" | Invoice list displayed |
| 2 | Verify displayed invoices | Only KH001's invoices shown, no other customers' |
| 3 | Click on invoice | Detail page with tier breakdown shown |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-011: Customer Pay Invoice - Simulated Payment

**Priority**: High  
**Module**: Customer Payment (FUNC-10)  
**Precondition**: Logged in as customer, unpaid invoice exists

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to invoice detail | Detail displayed, status="unpaid" |
| 2 | Click "Thanh toán" | Confirmation dialog |
| 3 | Confirm payment | Success message, status changed to "paid", payment record created |
| 4 | Try to pay again | Error: "Hóa đơn đã được thanh toán" |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-012: Customer Change Password

**Priority**: Medium  
**Module**: Customer Authentication (FUNC-05)  
**Precondition**: Logged in as customer

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to "Đổi mật khẩu" | Form displayed |
| 2 | Enter current_password "123456" | Field populated |
| 3 | Enter new_password "newpass123" | Password masked |
| 4 | Click "Đổi mật khẩu" | Success message, must_change_password = false |
| 5 | Logout and login with new password | Login successful |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-013: Search Households

**Priority**: Medium  
**Module**: Household Management (FUNC-06)  
**Precondition**: Multiple households exist

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to households list | All households displayed |
| 2 | Enter search "KH001" | Only matching household shown |
| 3 | Clear search, filter by status "inactive" | Only inactive households shown |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-014: Authorization - Customer Cannot Access Admin Endpoints

**Priority**: High  
**Module**: Security  
**Precondition**: Logged in as customer

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Try to access /api/admin/households | Error 403 Forbidden |
| 2 | Try to access /api/admin/invoices/calculate | Error 403 Forbidden |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  

---

## TC-015: Authorization - Admin Cannot Pay Invoices

**Priority**: Medium  
**Module**: Security  
**Precondition**: Logged in as admin

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Try to POST /api/customer/invoices/{id}/pay | Error 403 Forbidden (only customer can pay) |

**Actual Result**: _____  
**Status**: ☐ Pass ☐ Fail  
