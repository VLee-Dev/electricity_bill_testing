# Test Plan - Hệ thống tính tiền điện

## 1. Tổng quan

### 1.1. Mục đích
Test toàn bộ chức năng của hệ thống quản lý hóa đơn tiền điện, đảm bảo:
- Các chức năng hoạt động đúng theo yêu cầu
- Tính toán tiền điện chính xác theo biểu giá bậc thang
- Xác thực và phân quyền hoạt động đúng
- Hiệu năng đáp ứng yêu cầu

### 1.2. Phạm vi
- **API Backend**: Tất cả endpoints
- **Frontend**: Giao diện admin và customer
- **Database**: Tính toàn vẹn dữ liệu
- **Security**: Authentication, authorization, input validation

### 1.3. Môi trường test
- **Dev**: Máy local developer
- **Staging**: Server staging trước khi deploy production
- **Production**: Smoke test sau deploy

---

## 2. Test Levels

### 2.1. Unit Tests
**Mục tiêu**: Test từng function/method riêng lẻ

**Phạm vi**:
- Security functions (hash, verify password, JWT)
- Billing calculation logic
- Business rules validation

**Tools**: pytest

**Coverage target**: ≥ 80%

### 2.2. Integration Tests
**Mục tiêu**: Test tích hợp giữa các components

**Phạm vi**:
- API endpoints với database
- Authentication flow
- CRUD operations
- Business workflows

**Tools**: pytest + TestClient (FastAPI)

### 2.3. End-to-End Tests
**Mục tiêu**: Test user workflows từ đầu đến cuối

**Scenarios**:
1. Admin đăng ký hộ mới → nhập chỉ số → tính hóa đơn
2. Customer đăng nhập → xem hóa đơn → thanh toán
3. Admin xem báo cáo doanh thu

**Tools**: Selenium WebDriver

### 2.4. Performance Tests
**Mục tiêu**: Đảm bảo hệ thống đáp ứng yêu cầu hiệu năng

**Scenarios**:
- Load test: 100 concurrent users
- Stress test: Tìm giới hạn hệ thống
- Spike test: Tăng đột ngột traffic

**Tools**: JMeter

**KPIs**:
- Response time (P95) < 500ms
- Throughput > 100 req/s
- Error rate < 1%

---

## 3. Test Scope

### 3.1. Functional Testing

#### FUNC-01: Đăng ký hộ sử dụng điện
- ✅ Tạo household hợp lệ
- ✅ Tự động tạo customer account
- ❌ Trùng customer_code
- ❌ Trùng meter_number
- ❌ Trùng email
- ❌ Missing required fields

#### FUNC-02: Cập nhật chỉ số điện
- ✅ Nhập chỉ số mới hợp lệ
- ✅ Tự động tính consumption
- ✅ Lấy chỉ số cũ từ kỳ trước
- ❌ Chỉ số mới < chỉ số cũ
- ❌ Trùng period cho cùng household

#### FUNC-03: Tính tiền điện
- ✅ Tính đúng theo biểu giá bậc thang (6 bậc)
- ✅ Tính VAT 8%
- ✅ Lưu chi tiết từng bậc
- ✅ Set due_date = issued_date + 15 days
- ❌ Meter reading đã có invoice

#### FUNC-04: Xác thực Admin
- ✅ Login bằng username/password
- ✅ Trả về JWT token
- ❌ Sai credentials

#### FUNC-05: Xác thực Customer
- ✅ Login bằng customer_code/password
- ✅ Đổi mật khẩu
- ✅ Must change password flag
- ❌ Sai credentials

#### FUNC-06: Theo dõi hộ sử dụng điện
- ✅ List households
- ✅ Search by customer_code, name, phone
- ✅ Filter by status

#### FUNC-09: Customer xem hóa đơn
- ✅ List invoices của chính mình
- ✅ Chi tiết invoice + tier breakdown
- ❌ Không xem được invoice của người khác

#### FUNC-10: Thanh toán nhanh
- ✅ Thanh toán mô phỏng
- ✅ Cập nhật status = paid
- ✅ Tạo payment record
- ❌ Thanh toán invoice đã paid

### 3.2. Security Testing
- SQL Injection
- XSS attacks
- JWT token manipulation
- Authorization bypass
- Brute force login

### 3.3. Usability Testing
- Giao diện dễ sử dụng
- Error messages rõ ràng
- Responsive design

---

## 4. Test Deliverables

### 4.1. Test Cases
- Detailed test cases (Excel/Markdown)
- Expected vs Actual results
- Pass/Fail status

### 4.2. Test Reports
- Test execution summary
- Bug report
- Coverage report
- Performance test results

### 4.3. Test Automation
- Unit test suite (pytest)
- Integration test suite
- E2E test scripts (Selenium)
- Performance test plan (JMeter)

---

## 5. Test Schedule

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Unit Tests | Week 1 | 80% coverage |
| Integration Tests | Week 2 | API test suite |
| E2E Tests | Week 3 | Selenium scripts |
| Performance Tests | Week 4 | JMeter results |
| Regression Tests | Ongoing | Automated CI/CD |

---

## 6. Entry & Exit Criteria

### 6.1. Entry Criteria
- ✅ Code implementation complete
- ✅ API documentation available
- ✅ Test environment ready
- ✅ Test data prepared

### 6.2. Exit Criteria
- ✅ All critical test cases passed
- ✅ No high-severity bugs
- ✅ Test coverage ≥ 80%
- ✅ Performance KPIs met
- ✅ Test report approved

---

## 7. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|----------|
| Test environment không ổn định | High | Setup Docker containers |
| Thiếu test data | Medium | Tạo seed scripts |
| Thay đổi requirements | High | Agile testing approach |
| Time constraint | Medium | Prioritize critical tests |

---

## 8. Approvals

- **Test Lead**: _________________
- **Project Manager**: _________________
- **Product Owner**: _________________
