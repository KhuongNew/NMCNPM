# pytest -v test_login.py
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Cấu hình ----------
LOGIN_HTML = Path(r"D:\hoc\NMCNPM\lab03-testing-login\Login\Login.html").resolve().as_uri()
HEADLESS = False

def setup_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return drv

def open_login(drv):
    drv.get(LOGIN_HTML)
    WebDriverWait(drv, 5).until(EC.presence_of_element_located((By.ID, "loginForm")))

def submit_form(drv):
    # Ưu tiên click nút, nếu không có thì submit form
    btns = drv.find_elements(By.CSS_SELECTOR, "#btnLogin, [data-testid='btn-login'], button[type='submit']")
    if btns:
        btns[0].click()
    else:
        drv.find_element(By.ID, "loginForm").submit()

def read_alert_or_status(drv):
    # 1) alert()
    try:
        alert = WebDriverWait(drv, 2).until(EC.alert_is_present())
        txt = alert.text
        alert.accept()
        return txt
    except Exception:
        pass
    # 2) #status / data-testid=notice nếu có
    for css in ("#status", "[data-testid='notice']", ".status"):
        els = drv.find_elements(By.CSS_SELECTOR, css)
        if els:
            return els[0].text
    return ""

# ---------- TESTS (đúng yêu cầu đề) ----------

def test_login_success():
    d = setup_driver()
    try:
        open_login(d)
        d.find_element(By.CSS_SELECTOR, "#email, #username, [data-testid='input-username']").send_keys("user@example.com")
        d.find_element(By.CSS_SELECTOR, "#password, [data-testid='input-password']").send_keys("secret123")
        submit_form(d)
        msg = read_alert_or_status(d).lower()
        assert "đăng nhập thành công" in msg or "success" in msg
    finally:
        d.quit()

def test_login_wrong_password():
    d = setup_driver()
    try:
        open_login(d)
        d.find_element(By.CSS_SELECTOR, "#email, #username, [data-testid='input-username']").send_keys("user@example.com")
        d.find_element(By.CSS_SELECTOR, "#password, [data-testid='input-password']").send_keys("wrong")
        submit_form(d)
        msg = read_alert_or_status(d).lower()
        assert "invalid" in msg or "fail" in msg or "sai" in msg
    finally:
        d.quit()

def test_empty_fields_show_errors():
    d = setup_driver()
    try:
        open_login(d)
        submit_form(d)
        # Lỗi phải hiện cho cả email và password
        err_email = d.find_element(By.CSS_SELECTOR, "#err-email, #err-username, [data-testid='err-username']")
        err_pw    = d.find_element(By.CSS_SELECTOR, "#err-password, [data-testid='err-password']")
        # kiểm tra hiển thị (display:block) hoặc có text
        disp_email = err_email.value_of_css_property("display")
        disp_pw    = err_pw.value_of_css_property("display")
        assert disp_email == "block" or err_email.text.strip() != ""
        assert disp_pw == "block" or err_pw.text.strip() != ""
    finally:
        d.quit()

def test_forgot_password_link():
    d = setup_driver()
    try:
        open_login(d)
        forgot = d.find_element(By.CSS_SELECTOR, "a.hint[href*='Forgot'], a[href*='Forgot']")
        assert forgot.get_attribute("href").lower().endswith("forgot.html")
    finally:
        d.quit()

def test_signup_link():
    d = setup_driver()
    try:
        open_login(d)
        signup = d.find_element(By.CSS_SELECTOR, "a[href*='Signup'], a[href*='sign']")
        assert signup.get_attribute("href").lower().endswith("signup.html")
    finally:
        d.quit()

@pytest.mark.parametrize("css, keyword", [
    ("#gg, [data-testid='btn-google']", "google"),
    ("#fb, [data-testid='btn-facebook']", "facebook"),
    ("#tw, [data-testid='btn-twitter']", "twitter"),
])
def test_social_buttons_clickable(css, keyword):
    d = setup_driver()
    try:
        open_login(d)
        btns = d.find_elements(By.CSS_SELECTOR, css)
        if not btns:
            pytest.skip(f"Không tìm thấy nút {keyword}")
        btns[0].click()
        msg = read_alert_or_status(d).lower()
        assert keyword in msg
    finally:
        d.quit()
