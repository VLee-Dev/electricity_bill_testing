# ⚡ Hệ thống tính tiền điện (Electricity Bill Management)

Hệ thống quản lý hóa đơn tiền điện cho hộ gia đình: đăng ký hộ, cập nhật chỉ số điện hàng kỳ, **tính tiền tự động theo biểu giá bậc thang 6 mức**, thanh toán trực tuyến (mô phỏng).

## 🚀 Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 + PostgreSQL
- **Frontend**: HTML/CSS/JavaScript (vanilla, không framework)
- **Auth**: JWT Bearer
- **Migration**: Alembic
- **Test**: pytest + httpx (TestClient)

## 📂 Cấu trúc dự án

```
electricity_bill_testing/
├── backend/                     # FastAPI app
│   ├── app/
│   │   ├── features/            # Feature-based modules
│   │   │   ├── admin_auth/      # Đăng nhập admin
│   │   │   ├── customer_auth/   # Đăng nhập customer (bằng customer_code)
│   │   │   ├── households/      # CRUD hộ sử dụng điện
│   │   │   ├── meter_readings_new/  # Chỉ số điện theo kỳ
│   │   │   ├── billing_new/     # Tính hóa đơn (logic gộp)
│   │   │   ├── customer_invoices/   # Customer xem & thanh toán
│   │   │   ├── price_tiers/     # Bảng giá bậc thang
│   │   │   └── email_service.py
│   │   ├── models/              # SQLAlchemy ORM (admins, households, customers, meter_readings, invoices, price_tiers, invoice_tier_details, payments, email_logs, system_config)
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── config.py            # Settings (env)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── security.py          # bcrypt hash + JWT
│   │   └── dependencies.py      # Auth dependencies (current_user, admin_user)
│   ├── alembic/                 # Migrations
│   ├── scripts/                 # create_database.py, reset_db_seed.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── static/
│       ├── index.html           # Trang chủ landing
│       ├── css/style.css
│       ├── js/api.js            # Helper: toast(), confirm(), prompt()
│       ├── js/appbar.js         # Mount appbar component
│       ├── components/appbar.html
│       └── pages/
│           ├── admin/           # 9 trang (dashboard, households, household_detail, household_register, meter_readings, reading_form, invoices, invoice_detail, price_tiers)
│           ├── customer/        # 4 trang (dashboard, invoices, invoice_detail, price_tiers)
│           └── auth/            # admin_login, customer_login
├── tests/
│   ├── unit/                    # Logic thuần (billing, security)
│   ├── integration/             # API end-to-end qua TestClient
│   └── conftest.py              # Fixtures (db, client, admin)
├── docs/                        # Tài liệu chi tiết (API_ROUTES, TEST_PLAN, TEST_CASES)
├── qa/                          # Selenium E2E + JMeter load test
└── README.md
```

## 🔧 Setup khi clone về

### Yêu cầu
- Python 3.10+
- PostgreSQL 14+
- Node không cần (frontend là HTML thuần)

### Bước 1 — Cài đặt Python dependencies

```bash
# Tạo venv (khuyến nghị)
python -m venv .venv
.venv\Scripts\activate           # Windows

cd backend
pip install -r requirements.txt
```

### Bước 2 — Tạo database PostgreSQL

```bash
# Tạo DB rỗng (chạy 1 lần)
python scripts/create_database.py
```

Hoặc dùng psql:
```sql
CREATE DATABASE electricity_billing_test;
```

### Bước 3 — Cấu hình `.env`

Sao chép `backend/.env.example` thành `backend/.env` rồi chỉnh:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/electricity_billing_test
JWT_SECRET_KEY=replace-with-a-local-secret
JWT_EXPIRE_MINUTES=1440
EMAIL_MODE=console                # console (in ra terminal) | smtp (gửi Gmail thật)
```

### Bước 4 — Seed dữ liệu mẫu

```bash
cd backend
python scripts/reset_db_seed.py
```

Lệnh này **drop tất cả bảng, tạo lại schema, seed**: 1 admin + 6 bậc giá EVN + 2 hộ mẫu + 1 chỉ số + 1 hóa đơn.

Tài khoản mặc định:

| Role | Tài khoản | Mật khẩu |
|---|---|---|
| Admin | `admin` | `admin123` |
| Customer | `KH001` | `123456` |
| Customer | `KH002` | `123456` |

### Bước 5 — Chạy server

```bash
cd backend
uvicorn app.main:app --reload
```

- Trang chủ: http://localhost:8000/
- Swagger docs: http://localhost:8000/docs
- Đăng nhập admin: http://localhost:8000/auth/admin_login.html
- Đăng nhập customer: http://localhost:8000/auth/customer_login.html

## 🧪 Chạy test

```bash
# Từ thư mục backend/ (đã activate venv)
pytest                              # Tất cả tests
pytest tests/unit                   # Chỉ unit tests
pytest tests/integration            # Chỉ integration tests
pytest -v                           # Verbose
pytest --cov=app --cov-report=html  # Coverage report
```

Tests dùng **SQLite in-memory** (xem `tests/conftest.py`) → không đụng PostgreSQL.

### 📋 Test case hiện có (26/26 PASS) ✅

| File | Số test | Test case (mỗi test ứng với 1 chức năng) |
|---|:---:|---|
| `tests/unit/test_billing_calculation.py` | 5 | Logic tính tiền điện 6 bậc (bậc 1, 2, 3, 4, 6) + VAT 8% |
| `tests/unit/test_security.py` | 5 | bcrypt hash/verify + JWT create/decode (valid + invalid) |
| `tests/integration/test_admin_auth.py` | 5 | Admin login thành công / sai mật khẩu (401 `INVALID_CREDENTIALS`) / `/me` có/không token |
| `tests/integration/test_households.py` | 8 | Tạo hộ (201) / trùng mã KH (409 `CUSTOMER_CODE_EXISTS`) / list / search / PUT update (200) / trùng email (409 `EMAIL_EXISTS`) / DELETE soft (200 inactive) / DELETE idempotent |
| `tests/integration/test_meter_readings_delete.py` | 3 | DELETE chỉ số (200) / chặn khi có hóa đơn (409 `READING_HAS_INVOICE`) / not found (404) |

**Các module chưa có test (TODO):**
- ⏳ Customer auth (login, /me, change-password)
- ⏳ Meter readings POST + PUT (chỉ mới có DELETE)
- ⏳ Billing API (calculate, list, detail)
- ⏳ Customer invoices API (list, detail, pay)
- ⏳ Price tiers API (list, update)
- ⏳ Selenium E2E (đã có file `qa/selenium/test_e2e.py` nhưng URL đang sai, chưa chạy được)
- ⏳ JMeter load test (đã có file `qa/jmeter/load_test.jmx` nhưng chưa chạy)

## 🧠 Logic nghiệp vụ cơ bản

### 1. Tính tiền điện theo bậc thang (logic GỘP — không cộng dồn)

Xác định bậc mà `consumption = new_reading - old_reading` rơi vào dựa trên `[kwh_from, kwh_to]`:

| Bậc | Khoảng (kWh) | Đơn giá (đ/kWh) |
|---:|---:|---:|
| 1 | 0 – 50 | 1,984 |
| 2 | 51 – 100 | 2,050 |
| 3 | 101 – 200 | 2,380 |
| 4 | 201 – 300 | 2,998 |
| 5 | 301 – 400 | 3,350 |
| 6 | ≥ 401 | 3,460 |

**Quy tắc gộp:** Toàn bộ `consumption` được nhân với đơn giá của bậc đó (1 dòng `tier_details` duy nhất).

```
Ví dụ: 300 kWh rơi vào bậc 4 → subtotal = 300 × 2998 = 899,400 đ
Ví dụ: 200 kWh rơi vào bậc 3 → subtotal = 200 × 2380 = 476,000 đ
```

`vat_amount = round(subtotal × 0.08)`, `total_amount = subtotal + vat_amount`.
- `vat_rate` mặc định `0.08` (lưu ở `system_config.key='vat_rate'`).
- Hạn thanh toán mặc định 15 ngày (`system_config.key='invoice_due_days'`).

### 2. Vòng đời chỉ số & hóa đơn

1. Admin nhập chỉ số mới `POST /api/v1/admin/meter-readings` → tạo `MeterReading`.
2. Admin sửa chỉ số `PUT /api/v1/admin/meter-readings/{id}` → chỉ khi **CHƯA có** hóa đơn (trả 409 nếu đã có).
3. Admin tính hóa đơn `POST /api/v1/admin/invoices/calculate` → tạo `Invoice` + `InvoiceTierDetail` + `EmailLog`.
4. Sau khi tính → **KHÔNG thể sửa** chỉ số và **KHÔNG thể tính lại** cho cùng `meter_reading_id`.

### 3. Ràng buộc dữ liệu

- Mỗi hộ chỉ có **1 chỉ số cho 1 kỳ** (`UNIQUE(household_id, period)`).
- Mỗi `Household` ↔ 1 `Customer` (1-1, dùng chung ID).
- `customer_code`, `meter_number`, `email`, `phone` đều UNIQUE trong bảng `households`.
- Mỗi `tier_no` chỉ giữ **1 bản ghi active** (UPDATE trực tiếp khi admin sửa, không tạo bản ghi mới).

## 📡 API Endpoints

Tất cả routes có prefix `/api/v1`. Xem Swagger UI đầy đủ tại `/docs` sau khi chạy server.

| Nhóm | Endpoint | Mô tả |
|---|---|---|
| Admin auth | `POST /admin/auth/login` | Đăng nhập admin |
| Admin auth | `GET  /admin/auth/me` | Thông tin admin hiện tại |
| Customer auth | `POST /customer/auth/login` | Đăng nhập customer (bằng `customer_code`) |
| Customer auth | `GET  /customer/auth/me` | Thông tin customer |
| Customer auth | `GET  /customer/auth/me/household` | Thông tin household |
| Customer auth | `POST /customer/auth/change-password` | Đổi mật khẩu |
| Households | `POST /admin/households` | Đăng ký hộ mới |
| Households | `GET  /admin/households` | Danh sách hộ (search, filter) |
| Households | `GET  /admin/households/{id}` | Chi tiết 1 hộ |
| Meter readings | `POST /admin/meter-readings` | Cập nhật chỉ số điện |
| Meter readings | `GET  /admin/meter-readings` | Danh sách chỉ số (`has_invoice`) |
| Meter readings | `PUT  /admin/meter-readings/{id}` | Sửa chỉ số (khi chưa có hóa đơn) |
| Billing | `POST /admin/invoices/calculate` | Tính hóa đơn từ `meter_reading_id` |
| Billing | `GET  /admin/invoices` | Danh sách hóa đơn |
| Billing | `GET  /admin/invoices/{id}` | Chi tiết hóa đơn |
| Price tiers | `GET  /price-tiers/admin/all` | 6 bậc giá hiện hành (admin) |
| Price tiers | `PUT  /price-tiers/admin/{id}` | Cập nhật 1 bậc giá (UPDATE trực tiếp) |
| Price tiers | `GET  /price-tiers/active` | Bảng giá hiện hành (customer) |
| Customer invoices | `GET  /customer/invoices` | Hóa đơn của tôi |
| Customer invoices | `GET  /customer/invoices/{id}` | Chi tiết hóa đơn |
| Customer invoices | `POST /customer/invoices/{id}/pay` | Thanh toán (mô phỏng) |

## 📚 Tài liệu liên quan

- `docs/API_ROUTES.md` — Danh sách API chi tiết
- `docs/TEST_PLAN.md` — Kế hoạch test
- `docs/TEST_CASES.md` — Test cases
- `qa/selenium/test_e2e.py` — E2E browser tests
- `qa/jmeter/load_test.jmx` — Load test script

# Kiểm thử phần YC6,7,8:

**BƯỚC 1 – CẬP NHẬT CODE MỚI NHẤT**

Mở VS Code, mở thư mục dự án `electricity_bill_testing`, sau đó mở Terminal (PowerShell).
Chạy:

git status
git branch --show-current

Nếu đang ở nhánh `main` và hiện `working tree clean`, chạy tiếp:

git pull --ff-only origin main
git log -1 --oneline

Commit hiện tạii cần có:

`4aa35bc kiemthu: dat 100 phan tram do bao phu ma nguon`

Nếu đang có file sửa chưa commit hoặc ở nhánh khác, gửi kết quả trước, đừng pull vội.

**BƯỚC 2 – KÍCH HOẠT MÔI TRƯỜNG PYTHON**

Tại thư mục gốc dự án, chạy:

.\.venv\Scripts\Activate.ps1
python --version
python -m pytest --version

**BƯỚC 3 – KIỂM TRA YC6: UNIT TEST VÀ COVERAGE**

Chạy:

python -m pytest tests\unit tests\integration -q --cov=backend/app --cov-report=term-missing


Kết quả hiện tại trên máy mình:

- 162 test PASS
- 0 FAIL
- Code Coverage 100%
- 1.059 statements, 0 missed


**BƯỚC 4 – KIỂM TRA YC7: SELENIUM E2E**

Trước khi chạy phải đảm bảo đã cài selennium webdriver đã được cài dặt, backend hoạt động, Chrome/WebDriver dùng được và kết nối tới database kiểm thử riêng. Selenium có thể thêm hoặc sửa dữ liệu, nên không chạy trên database đang chứa dữ liệu quan trọng.

Hướng dẫn cài đặt:

Mở PowerShell trong thư mục gốc dự án:

.\.venv\Scripts\Activate.ps1
python -m pip show selenium

Nếu hiện thông tin phiên bản Selenium thì đã cài.

Nếu báo không tìm thấy, chạy:

python -m pip install -U selenium

Lưu ý: Máy cần cài Google Chrome. Selenium phiên bản 4.6 trở lên hỗ trợ Selenium Manager, có thể tự động quản lý ChromeDriver tương thích mà không cần tải thủ công.

Khi môi trường đã sẵn sàng, chạy:

$env:E2E_ADMIN_PASSWORD="admin123"
python -m pytest qa\selenium\test_e2e.py -q --tb=short

Kết quả hiện tại trên máy mình: `14 passed`.

**BƯỚC 5 – KIỂM TRA YC8: Jmeter**

5.1. Cài Java và JMeter
Kiểm tra Java:

java -version

Nếu chưa có Java, tải JDK

**Cài Apache JMeter 5.6.3:**

1. Tải `apache-jmeter-5.6.3.zip` tại https://archive.apache.org/dist/jmeter/binaries/
2. Giải nén vào `D:\JMeter`.
3. Mở JMeter bằng PowerShell:

& "D:\JMeter\apache-jmeter-5.6.3\bin\jmeter.bat"

JMeter 5.6.3 hỗ trợ Java 8 trở lên.

5.2. Kiểm tra kịch bản

Tại thư mục gốc dự án, chạy:

Get-ChildItem .\qa\jmeter -Filter *.jmx

Hai kịch bản cần có:
- `qa\jmeter\load_test.jmx` – 5 users.
- `qa\jmeter\load_test_50users.jmx` – 50 users.

5.3. Chuẩn bị backend
- Cài đặt và chạy backend, PostgreSQL theo hướng dẫn dự án.
- Sử dụng database kiểm thử riêng.
- Kiểm tra API tại `http://127.0.0.1:8000/docs` nếu backend chạy ở cổng 8000.
- Kiểm tra URL, tài khoản và dữ liệu request trong JMeter.
**Không chạy kiểm thử trên database chứa dữ liệu quan trọng.**
5.4. Thực hiện kiểm thử
Trong JMeter:
1. Chọn File → Open → mở `load_test.jmx`.
2. Kiểm tra Thread Group có **5 users** và cấu hình API chính xác.
3. Nhấn Start, chờ hoàn thành và xem kết quả.
4. Mở `load_test_50users.jmx`.
5. Kiểm tra Thread Group có 50 users, sau đó chạy tương tự.

Theo dõi chỉ số: Samples, Average, Error %, Throughput và 95th Percentile.

### 5.6. Kiểm tra kết quả

Chạy PowerShell:

Get-ChildItem results -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -eq ".jtl" } |
    Select-Object -ExpandProperty FullName

**Kết quả tham chiếu đã thực hiện:**

Kịch bản 5 users:
Tổng số request: 15.
Số request thành công: 15/15 (100%).
Tỷ lệ lỗi: 0%.
Thời gian phản hồi trung bình: 163,4 ms.

Kịch bản 50 users:
Tổng số request: 150.
Số request thành công: 150/150 (100%).
Tỷ lệ lỗi: 0%.
Thời gian phản hồi trung bình: 128,99 ms.

Các file kết quả tham chiếu:
results\load_test_5users.jtl
results\load_test_50users.jtl
Các báo cáo HTML:
results\jmeter_report_5users\index.html
results\jmeter_report_50users\index.html
```
**Lưu ý:** Thư mục `results/` có thể không được đồng bộ qua GitHub. Cần chạy lại hoặc nhận báo cáo từ mình.