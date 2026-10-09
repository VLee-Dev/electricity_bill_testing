
import os
from html.parser import HTMLParser
from urllib.request import urlopen

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.getenv(
    "E2E_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

ADMIN_USERNAME = os.getenv("E2E_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD", "")


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1366,768")

    browser = webdriver.Chrome(options=options)

    try:
        yield browser
    finally:
        browser.quit()


# ============================================
# HELPER FUNCTIONS
# ============================================

def open_admin_login(driver):
    driver.get(f"{BASE_URL}/auth/admin_login.html")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "username")
        )
    )


def submit_admin_login(driver, username, password):
    driver.find_element(
        By.ID, "username"
    ).send_keys(username)

    driver.find_element(
        By.ID, "password"
    ).send_keys(password)

    driver.find_element(
        By.CSS_SELECTOR,
        '#login-form button[type="submit"]'
    ).click()


def get_registration_html():
    with urlopen(
        f"{BASE_URL}/admin/household_register.html",
        timeout=10
    ) as response:
        assert response.status == 200
        return response.read().decode("utf-8")


class InputParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            self.inputs.append(dict(attrs))


# ============================================
# ADMIN LOGIN TESTS
# ============================================

class TestAdminLogin:

    def test_admin_login_page_loads(self, driver):
        """TC01 - Trang đăng nhập Admin hiển thị."""

        open_admin_login(driver)

        assert "Đăng nhập" in driver.title

        assert driver.find_element(
            By.ID, "login-form"
        ).is_displayed()

        assert driver.find_element(
            By.ID, "username"
        ).is_displayed()

        assert driver.find_element(
            By.ID, "password"
        ).is_displayed()

    def test_admin_login_success(self, driver):
        """TC02 - Đăng nhập Admin thành công."""

        if not ADMIN_PASSWORD:
            pytest.skip(
                "Chưa cấu hình E2E_ADMIN_PASSWORD."
            )

        open_admin_login(driver)

        submit_admin_login(
            driver,
            ADMIN_USERNAME,
            ADMIN_PASSWORD
        )

        WebDriverWait(driver, 15).until(
            EC.url_contains("/admin/dashboard.html")
        )

        assert "/admin/dashboard.html" in driver.current_url

    def test_admin_login_invalid_password(self, driver):
        """TC03 - Sai mật khẩu hiển thị lỗi."""

        open_admin_login(driver)

        submit_admin_login(
            driver,
            ADMIN_USERNAME,
            "invalid_password_e2e_987654"
        )

        error = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.ID, "error-message")
            )
        )

        assert error.text.strip()
        assert "/admin/dashboard.html" not in driver.current_url

    def test_admin_login_empty_username(self, driver):
        """TC04 - Không cho gửi form thiếu username."""

        open_admin_login(driver)

        driver.find_element(
            By.ID, "password"
        ).send_keys("password123")

        driver.find_element(
            By.CSS_SELECTOR,
            '#login-form button[type="submit"]'
        ).click()

        username = driver.find_element(
            By.ID, "username"
        )

        assert not username.get_property("validity")["valid"]
        assert "/admin/dashboard.html" not in driver.current_url

    def test_admin_login_empty_password(self, driver):
        """TC05 - Không cho gửi form thiếu password."""

        open_admin_login(driver)

        driver.find_element(
            By.ID, "username"
        ).send_keys(ADMIN_USERNAME)

        driver.find_element(
            By.CSS_SELECTOR,
            '#login-form button[type="submit"]'
        ).click()

        password = driver.find_element(
            By.ID, "password"
        )

        assert not password.get_property("validity")["valid"]
        assert "/admin/dashboard.html" not in driver.current_url

    def test_admin_login_password_masked(self, driver):
        """TC06 - Mật khẩu được che khi nhập."""

        open_admin_login(driver)

        password = driver.find_element(
            By.ID, "password"
        )

        assert password.get_attribute("type") == "password"

    def test_admin_login_invalid_username(self, driver):
        """TC07 - Tài khoản không tồn tại bị từ chối."""

        open_admin_login(driver)

        submit_admin_login(
            driver,
            "nonexistent_admin_e2e_987654",
            "invalid_password_e2e_987654"
        )

        error = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.ID, "error-message")
            )
        )

        assert error.text.strip()
        assert "/admin/dashboard.html" not in driver.current_url


# ============================================
# HOUSEHOLD REGISTRATION TESTS
# ============================================

class TestHouseholdRegistration:

    def test_registration_requires_login(self, driver):
        """TC08 - Chưa đăng nhập không được vào trang đăng ký."""

        # Truy cập trang chủ để sử dụng localStorage
        driver.get(f"{BASE_URL}/")

        # Xóa trạng thái đăng nhập
        driver.execute_script("""
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_type');
        """)

        # Thử truy cập trang đăng ký hộ dân
        driver.get(
            f"{BASE_URL}/admin/household_register.html"
        )

        # Theo api.js, khi không có token và user_type,
        # hệ thống chuyển về trang chủ.
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.rstrip("/") == BASE_URL
        )

        assert driver.current_url.rstrip("/") == BASE_URL

        assert (
            "/admin/household_register.html"
            not in driver.current_url
        )

    def test_registration_form_fields(self):
        """TC09 - Kiểm tra các trường trong HTML đăng ký."""

        html = get_registration_html()

        required_ids = [
            "register-form",
            "customer-code",
            "full-name",
            "address",
            "phone",
            "email",
            "meter-number",
            "initial-password",
        ]

        for element_id in required_ids:
            assert f'id="{element_id}"' in html

    def test_registration_password_minlength(self):
        """TC10 - Mật khẩu khởi tạo tối thiểu 6 ký tự."""

        html = get_registration_html()

        parser = InputParser()
        parser.feed(html)

        password_fields = [
            attrs
            for attrs in parser.inputs
            if attrs.get("id") == "initial-password"
        ]

        assert len(password_fields) == 1
        assert password_fields[0].get("type") == "password"
        assert password_fields[0].get("minlength") == "6"

from uuid import uuid4


def login_as_admin(driver):
    """Đăng nhập Admin bằng giao diện."""

    if not ADMIN_PASSWORD:
        pytest.skip("Chưa cấu hình E2E_ADMIN_PASSWORD.")

    open_admin_login(driver)
    submit_admin_login(
        driver,
        ADMIN_USERNAME,
        ADMIN_PASSWORD
    )

    WebDriverWait(driver, 15).until(
        EC.url_contains("/admin/dashboard.html")
    )


def open_registration_as_admin(driver):
    """Đăng nhập và mở trang đăng ký hộ dân."""

    login_as_admin(driver)

    driver.get(
        f"{BASE_URL}/admin/household_register.html"
    )

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "register-form")
        )
    )


def fill_household_form(driver, data):
    """Điền đầy đủ thông tin hộ dân."""

    field_mapping = {
        "customer-code": "customer_code",
        "full-name": "full_name",
        "address": "address",
        "phone": "phone",
        "email": "email",
        "meter-number": "meter_number",
        "initial-password": "initial_password",
    }

    for element_id, data_key in field_mapping.items():
        element = driver.find_element(By.ID, element_id)
        element.clear()
        element.send_keys(data[data_key])


def make_household_data():
    """Sinh dữ liệu riêng để tránh trùng giữa các lần chạy."""

    unique = uuid4().hex[:12]

    return {
        "customer_code": f"E2E{unique}",
        "full_name": "Khach hang Selenium",
        "address": "123 Duong Kiem Thu",
        "phone": "0912345678",
        "email": f"e2e{unique}@example.com",
        "meter_number": f"MT{unique}",
        "initial_password": "Test123456",
    }


def submit_household_form(driver):
    driver.find_element(
        By.CSS_SELECTOR,
        '#register-form button[type="submit"]'
    ).click()


class TestHouseholdRegistrationE2E:

    def test_register_household_success(self, driver):
        """TC11 - Admin đăng ký hộ dân thành công."""

        open_registration_as_admin(driver)

        data = make_household_data()
        fill_household_form(driver, data)
        submit_household_form(driver)

        success = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.ID, "success-message")
            )
        )

        assert data["customer_code"] in success.text

        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/households.html")
        )

    def test_register_missing_required_field(self, driver):
        """TC12 - Không cho đăng ký thiếu thông tin."""

        open_registration_as_admin(driver)

        data = make_household_data()
        fill_household_form(driver, data)

        name_field = driver.find_element(
            By.ID, "full-name"
        )
        name_field.clear()

        submit_household_form(driver)

        assert not name_field.get_property(
            "validity"
        )["valid"]

        assert (
            "/admin/household_register.html"
            in driver.current_url
        )

    def test_register_short_password(self, driver):
        """TC13 - Không cho đăng ký mật khẩu dưới 6 ký tự."""

        open_registration_as_admin(driver)

        data = make_household_data()
        data["initial_password"] = "123"

        fill_household_form(driver, data)
        submit_household_form(driver)

        password = driver.find_element(
            By.ID, "initial-password"
        )

        assert not password.get_property(
            "validity"
        )["valid"]

        assert (
            "/admin/household_register.html"
            in driver.current_url
        )

    def test_register_duplicate_customer_code(self, driver):
        """TC14 - Không cho đăng ký trùng mã khách hàng."""

        open_registration_as_admin(driver)

        data = make_household_data()
        fill_household_form(driver, data)
        submit_household_form(driver)

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.ID, "success-message")
            )
        )

        driver.get(
            f"{BASE_URL}/admin/household_register.html"
        )

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "register-form")
            )
        )

        duplicate_data = make_household_data()
        duplicate_data["customer_code"] = data["customer_code"]

        fill_household_form(driver, duplicate_data)
        submit_household_form(driver)

        error = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.ID, "error-message")
            )
        )

        assert "Mã khách hàng đã tồn tại" in error.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
