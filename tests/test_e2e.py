import os
import time
import allure
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

API_URL = os.getenv("API_URL", "http://backend:8000")
FRONT_URL = os.getenv("FRONT_URL", "http://frontend:80")
SELENIUM_URL = os.getenv("SELENIUM_URL", "http://selenium-chrome:4444/wd/hub")
MAILPIT_URL = os.getenv("MAILPIT_URL", "http://mailpit:8025")


@allure.feature("API Тесты")
def test_api_initial_seed_data():
    resp = requests.get(f"{API_URL}/api/appointments")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


@allure.feature("Интеграция с заглушками и почтой")
def test_create_appointment_and_check_mailpit():
    payload = {
        "client_name": "Иван Тестов",
        "email": "ivan.qa@example.test",
        "slot_time": "2026-11-28 15:00"
    }
    resp = requests.post(f"{API_URL}/api/appointments", json=payload)
    assert resp.status_code == 201

    # Проверяем в API Mailpit, что письмо реально перехвачено
    time.sleep(1)
    mails = requests.get(f"{MAILPIT_URL}/api/v1/messages").json()
    assert any("ivan.qa@example.test" in str(m) for m in mails.get("messages", []))


@allure.feature("UI Тесты (Selenium Chrome)")
def test_ui_booking_page_loads():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
    try:
        driver.get(FRONT_URL)
        title = driver.find_element(By.TAG_NAME, "h2").text
        assert "Сервис записи на приём" in title
    finally:
        driver.quit()
