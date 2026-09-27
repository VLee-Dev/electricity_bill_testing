from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestAdminLogin:
    """
    E2E test for admin login workflow
    """

    def setup_method(self):
        """Setup browser before each test"""
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.base_url = "http://localhost:8000"

    def teardown_method(self):
        """Close browser after each test"""
        self.driver.quit()

    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        driver = self.driver
        driver.get(f"{self.base_url}/frontend/admin/login.html")

        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        # Enter credentials
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")

        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        login_button.click()

        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard.html")
        )

        # Verify redirect
        assert "dashboard" in driver.current_url

        # Verify token stored in localStorage
        token = driver.execute_script("return localStorage.getItem('token');")
        assert token is not None

    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        driver = self.driver
        driver.get(f"{self.base_url}/frontend/admin/login.html")

        # Enter invalid credentials
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginBtn")

        username_field.send_keys("admin")
        password_field.send_keys("wrongpassword")
        login_button.click()

        # Wait for error message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )

        error_msg = driver.find_element(By.CLASS_NAME, "error-message")
        assert "không đúng" in error_msg.text.lower()


class TestHouseholdRegistration:
    """
    E2E test for household registration workflow
    """

    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.base_url = "http://localhost:8000"

    def teardown_method(self):
        self.driver.quit()

    def test_register_household_success(self):
        """Test registering a new household"""
        driver = self.driver

        # Login as admin first
        self._login_as_admin(driver)

        # Navigate to household registration
        driver.get(f"{self.base_url}/frontend/admin/households-register.html")

        # Fill form
        driver.find_element(By.ID, "customerCode").send_keys("KH999")
        driver.find_element(By.ID, "fullName").send_keys("Test User E2E")
        driver.find_element(By.ID, "address").send_keys("Test Address 123")
        driver.find_element(By.ID, "phone").send_keys("0909999999")
        driver.find_element(By.ID, "email").send_keys("test999@example.com")
        driver.find_element(By.ID, "meterNumber").send_keys("MT999")
        driver.find_element(By.ID, "initialPassword").send_keys("password123")

        # Submit
        driver.find_element(By.ID, "submitBtn").click()

        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )

        success_msg = driver.find_element(By.CLASS_NAME, "success-message")
        assert "thành công" in success_msg.text.lower()

    def _login_as_admin(self, driver):
        """Helper method to login as admin"""
        driver.get(f"{self.base_url}/frontend/admin/login.html")
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.ID, "loginBtn").click()
        time.sleep(2)  # Wait for login to complete


class TestCustomerInvoicePayment:
    """
    E2E test for customer viewing and paying invoices
    """

    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.base_url = "http://localhost:8000"

    def teardown_method(self):
        self.driver.quit()

    def test_customer_view_and_pay_invoice(self):
        """Test customer viewing invoices and making payment"""
        driver = self.driver

        # Login as customer
        driver.get(f"{self.base_url}/frontend/customer/login.html")
        driver.find_element(By.ID, "customerCode").send_keys("KH001")
        driver.find_element(By.ID, "password").send_keys("123456")
        driver.find_element(By.ID, "loginBtn").click()

        # Wait for redirect
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard.html")
        )

        # Navigate to invoices
        driver.find_element(By.LINK_TEXT, "Hóa đơn của tôi").click()

        # Wait for invoice list
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "invoice-item"))
        )

        # Click first unpaid invoice
        unpaid_invoice = driver.find_element(By.CSS_SELECTOR, ".invoice-item.unpaid")
        unpaid_invoice.click()

        # Wait for invoice detail page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "payBtn"))
        )

        # Click pay button
        driver.find_element(By.ID, "payBtn").click()

        # Confirm payment
        WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        alert = driver.switch_to.alert
        alert.accept()

        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )

        # Verify invoice status changed to paid
        status = driver.find_element(By.CLASS_NAME, "invoice-status")
        assert "paid" in status.text.lower()


if __name__ == "__main__":
    # Run with: python -m pytest qa/selenium/test_e2e.py
    pass
