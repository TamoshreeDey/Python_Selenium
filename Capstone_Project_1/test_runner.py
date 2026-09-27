import json
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from config import BASE_URL, SCREENSHOT_DIR


# PAGE OBJECT MODEL (POM) CLASSES

class BasePage:
    """Base Page containing shared methods across pages."""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def capture_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(filepath)
        print(f"Screenshot saved: {filepath}")

    def handle_alerts(self):
        """Dismiss/Accept popups or JavaScript alerts if present."""
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert_text = alert.text
            print(f"Alert found: {alert_text}")
            alert.accept()
        except TimeoutException:
            pass  # No alert present


class LoginPage(BasePage):
    EMAIL_INPUT = (By.ID, "input-email")
    PASSWORD_INPUT = (By.ID, "input-password")
    LOGIN_BTN = (By.XPATH, "//input[@value='Login']")

    def login(self, email, password):
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)


class ProductPage(BasePage):
    SEARCH_INPUT = (By.NAME, "search")
    SEARCH_BTN = (By.XPATH, "//div[@id='search']//button")
    PRODUCT_LINK = (By.XPATH, "//div[@class='product-thumb']//h4/a")
    ADD_TO_CART_BTN = (By.ID, "button-cart")
    CART_ALERT = (By.CSS_SELECTOR, ".alert-success")
    SHOPPING_CART_LINK = (By.XPATH, "//a[title='Shopping Cart'] | //a[contains(@href, 'checkout/cart')]")

    def search_and_select_product(self, product_name):
        self.type_text(self.SEARCH_INPUT, product_name)
        self.click(self.SEARCH_BTN)
        self.click(self.PRODUCT_LINK)

    def add_to_cart(self):
        self.click(self.ADD_TO_CART_BTN)
        self.wait.until(EC.visibility_of_element_located(self.CART_ALERT))

    def navigate_to_cart(self):
        self.click(self.SHOPPING_CART_LINK)


class CartPage(BasePage):
    QTY_INPUT = (By.XPATH, "//input[contains(@name, 'quantity')]")
    UPDATE_BTN = (By.XPATH, "//button[@type='submit' and @data-original-title='Update']")
    REFRESH_SUCCESS_ALERT = (By.CSS_SELECTOR, ".alert-success")
    UNIT_PRICE = (By.XPATH, "//div[@class='table-responsive']//table/tbody/tr/td[5]")
    TOTAL_PRICE = (By.XPATH, "//div[@class='table-responsive']//table/tbody/tr/td[6]")
    PRODUCT_NAME = (By.XPATH, "//div[@class='table-responsive']//table/tbody/tr/td[2]/a")

    def update_quantity(self, qty):
        self.type_text(self.QTY_INPUT, qty)
        self.click(self.UPDATE_BTN)
        self.wait.until(EC.visibility_of_element_located(self.REFRESH_SUCCESS_ALERT))

    def get_cart_details(self):
        product_name = self.find(self.PRODUCT_NAME).text
        unit_price = self.find(self.UNIT_PRICE).text
        total_price = self.find(self.TOTAL_PRICE).text
        return product_name, unit_price, total_price



# TEST IMPLEMENTATION & FIXTURES

@pytest.fixture(scope="module")
def test_data():
    with open("data.json", "r") as file:
        return json.load(file)


@pytest.fixture
def driver():
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def test_ecommerce_end_to_end(driver, test_data):
    # 1. Launch Browser & Open Application
    driver.get(BASE_URL)
    base_page = BasePage(driver)
    base_page.handle_alerts()
    base_page.capture_screenshot("01_Launch_Page")

    # 2. Login to Application
    login_page = LoginPage(driver)
    login_page.login(test_data["login"]["email"], test_data["login"]["password"])
    base_page.capture_screenshot("02_Logged_In")

    # 3. Search and Select Product
    product_page = ProductPage(driver)
    product_page.search_and_select_product(test_data["search_product"])
    base_page.capture_screenshot("03_Product_Found")

    # 4. Add Product to Cart
    product_page.add_to_cart()
    base_page.capture_screenshot("04_Added_To_Cart")

    # 5. Navigate to Shopping Cart
    product_page.navigate_to_cart()
    base_page.capture_screenshot("05_Navigated_To_Cart")

    # 6. Update Quantity
    cart_page = CartPage(driver)
    cart_page.update_quantity(test_data["updated_quantity"])
    base_page.capture_screenshot("06_Quantity_Updated")

    # 7. Verify Cart Details
    product_name, unit_price, total_price = cart_page.get_cart_details()
    
    assert test_data["search_product"].lower() in product_name.lower(), f"Expected product {test_data['search_product']} not found."
    
    print("\n--- Cart Verification Passed ---")
    print(f"Product Name : {product_name}")
    print(f"Unit Price   : {unit_price}")
    print(f"Total Price  : {total_price}")
    
    base_page.capture_screenshot("07_Cart_Details_Verified")