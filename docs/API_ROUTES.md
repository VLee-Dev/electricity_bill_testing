# API Routes Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
Tất cả các endpoint (trừ login) yêu cầu JWT token trong header:
```
Authorization: Bearer <token>
```

---

## 1. Admin Authentication

### 1.1. Admin Login
```http
POST /admin/auth/login
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 1.2. Get Admin Info
```http
GET /admin/auth/me
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "admin-00000...",
  "username": "admin",
  "full_name": "Quản trị viên"
}
```

---

## 2. Customer Authentication

### 2.1. Customer Login
```http
POST /customer/auth/login
```

**Request Body:**
```json
{
  "customer_code": "KH001",
  "password": "123456"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 2.2. Get Customer Info
```http
GET /customer/auth/me
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "cust-uuid",
  "household_id": "household-uuid",
  "must_change_password": false
}
```

### 2.3. Get Customer Household
```http
GET /customer/auth/me/household
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "household-uuid",
  "customer_code": "KH001",
  "full_name": "Nguyễn Văn A",
  "address": "123 Đường ABC, Quận 1, TP.HCM",
  "phone": "0901234567",
  "email": "nva@example.com",
  "meter_number": "MT001",
  "status": "active"
}
```

### 2.4. Change Password
```http
POST /customer/auth/change-password
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "123456",
  "new_password": "newpass123"
}
```

**Response:** `204 No Content`

---

## 3. Admin - Households Management

### 3.1. Register New Household (FUNC-01)
```http
POST /admin/households
Authorization: Bearer <admin-token>
```

**Request Body:**
```json
{
  "customer_code": "KH001",
  "full_name": "Nguyễn Văn A",
  "address": "123 Đường ABC, Quận 1, TP.HCM",
  "phone": "0901234567",
  "email": "nva@example.com",
  "meter_number": "MT001",
  "initial_password": "123456"
}
```

**Response:** `201 Created`
```json
{
  "id": "household-uuid",
  "customer_code": "KH001",
  "full_name": "Nguyễn Văn A",
  "address": "123 Đường ABC, Quận 1, TP.HCM",
  "phone": "0901234567",
  "email": "nva@example.com",
  "meter_number": "MT001",
  "registered_at": "2026-09-25T10:00:00Z",
  "status": "active"
}
```

### 3.2. List Households (FUNC-06)
```http
GET /admin/households?search=KH001&status=active
Authorization: Bearer <admin-token>
```

**Query Parameters:**
- `search` (optional): Tìm kiếm theo mã KH, tên, SĐT
- `status` (optional): Lọc theo trạng thái (active/inactive)

**Response:** `200 OK`
```json
[
  {
    "id": "household-uuid",
    "customer_code": "KH001",
    "full_name": "Nguyễn Văn A",
    "phone": "0901234567",
    "email": "nva@example.com",
    "meter_number": "MT001",
    "status": "active"
  }
]
```

### 3.3. Get Household Detail
```http
GET /admin/households/{household_id}
Authorization: Bearer <admin-token>
```

**Response:** `200 OK`
```json
{
  "id": "household-uuid",
  "customer_code": "KH001",
  "full_name": "Nguyễn Văn A",
  "address": "123 Đường ABC, Quận 1, TP.HCM",
  "phone": "0901234567",
  "email": "nva@example.com",
  "meter_number": "MT001",
  "registered_at": "2026-09-25T10:00:00Z",
  "status": "active"
}
```

---

## 4. Admin - Meter Readings

### 4.1. Add Meter Reading (FUNC-02)
```http
POST /admin/meter-readings
Authorization: Bearer <admin-token>
```

**Request Body:**
```json
{
  "household_id": "household-uuid",
  "period": "2026-09",
  "new_reading": 350
}
```

**Response:** `201 Created`
```json
{
  "id": "reading-uuid",
  "household_id": "household-uuid",
  "period": "2026-09",
  "old_reading": 250,
  "new_reading": 350,
  "consumption": 100,
  "recorded_at": "2026-09-25T10:00:00Z"
}
```

### 4.2. List Meter Readings
```http
GET /admin/meter-readings?household_id=xxx&period=2026-09
Authorization: Bearer <admin-token>
```

**Query Parameters:**
- `household_id` (optional): Lọc theo hộ
- `period` (optional): Lọc theo kỳ (YYYY-MM)

**Response:** `200 OK`
```json
[
  {
    "id": "reading-uuid",
    "household_id": "household-uuid",
    "period": "2026-09",
    "old_reading": 250,
    "new_reading": 350,
    "consumption": 100,
    "recorded_at": "2026-09-25T10:00:00Z"
  }
]
```

---

## 5. Admin - Billing

### 5.1. Calculate Invoice (FUNC-03)
```http
POST /admin/invoices/calculate
Authorization: Bearer <admin-token>
```

**Request Body:**
```json
{
  "meter_reading_id": "reading-uuid"
}
```

**Response:** `201 Created`
```json
{
  "id": "invoice-uuid",
  "household_id": "household-uuid",
  "meter_reading_id": "reading-uuid",
  "subtotal": 195400,
  "vat_amount": 15632,
  "total_amount": 211032,
  "status": "unpaid",
  "issued_at": "2026-09-25T10:00:00Z",
  "due_date": "2026-10-10",
  "tier_details": [
    {"tier_no": 1, "kwh_applied": 50, "unit_price": 1678, "amount": 83900},
    {"tier_no": 2, "kwh_applied": 50, "unit_price": 1734, "amount": 86700},
    {"tier_no": 3, "kwh_applied": 0, "unit_price": 2014, "amount": 0}
  ]
}
```

### 5.2. List Invoices
```http
GET /admin/invoices?household_id=xxx&status=unpaid
Authorization: Bearer <admin-token>
```

**Query Parameters:**
- `household_id` (optional): Lọc theo hộ
- `status` (optional): Lọc theo trạng thái (paid/unpaid)

**Response:** `200 OK`
```json
[
  {
    "id": "invoice-uuid",
    "household_id": "household-uuid",
    "subtotal": 195400,
    "vat_amount": 15632,
    "total_amount": 211032,
    "status": "unpaid",
    "issued_at": "2026-09-25T10:00:00Z",
    "due_date": "2026-10-10"
  }
]
```

### 5.3. Get Invoice Detail
```http
GET /admin/invoices/{invoice_id}
Authorization: Bearer <admin-token>
```

**Response:** `200 OK` (Same as 5.1)

---

## 6. Customer - Invoices

### 6.1. List My Invoices (FUNC-09)
```http
GET /customer/invoices
Authorization: Bearer <customer-token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "invoice-uuid",
    "subtotal": 195400,
    "vat_amount": 15632,
    "total_amount": 211032,
    "status": "unpaid",
    "issued_at": "2026-09-25T10:00:00Z",
    "due_date": "2026-10-10"
  }
]
```

### 6.2. Get My Invoice Detail (FUNC-09)
```http
GET /customer/invoices/{invoice_id}
Authorization: Bearer <customer-token>
```

**Response:** `200 OK`
```json
{
  "id": "invoice-uuid",
  "household_id": "household-uuid",
  "meter_reading_id": "reading-uuid",
  "subtotal": 195400,
  "vat_amount": 15632,
  "total_amount": 211032,
  "status": "unpaid",
  "issued_at": "2026-09-25T10:00:00Z",
  "due_date": "2026-10-10",
  "tier_details": [...]
}
```

### 6.3. Pay Invoice (FUNC-10)
```http
POST /customer/invoices/{invoice_id}/pay
Authorization: Bearer <customer-token>
```

**Request Body:** `{}` (empty)

**Response:** `201 Created`
```json
{
  "id": "payment-uuid",
  "invoice_id": "invoice-uuid",
  "amount": 211032,
  "method": "online_simulated",
  "paid_at": "2026-09-25T10:05:00Z"
}
```

---

## Error Response Format

```json
{
  "error_code": "CUSTOMER_CODE_EXISTS",
  "message": "Mã khách hàng đã tồn tại.",
  "details": null
}
```

### Common Error Codes:
- `INVALID_CREDENTIALS` - Sai username/password
- `CUSTOMER_CODE_EXISTS` - Mã khách hàng đã tồn tại
- `METER_NUMBER_EXISTS` - Số công tơ đã tồn tại
- `EMAIL_EXISTS` - Email đã tồn tại
- `DUPLICATE_PERIOD` - Hộ đã có chỉ số cho kỳ này
- `INVOICE_EXISTS` - Chỉ số đã có hóa đơn
- `INVOICE_ALREADY_PAID` - Hóa đơn đã thanh toán
- `VALIDATION_ERROR` - Dữ liệu không hợp lệ
