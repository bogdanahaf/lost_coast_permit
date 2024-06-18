import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os

# Define your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, params=params)
    print(f"Telegram response: {response.status_code} - {response.text}")

def scrape_availability(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Optional: Run Chrome in headless mode
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    try:
        print("HELLO")
        button1 = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'rec-select'))
        )
        print("Button1 found")
        button1.click()
        print("Button1 clicked")
        
        button2 = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="guest-counter-QuotaUsageByMember-popup"]/div/div[1]/div/div/div[1]/div[2]/div/div/button[2]'))
        )
        print("Button2 found")
        button2.click()
        print("Button2 clicked")

        buttons = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'rec-input-radio'))
        )
        if len(buttons) > 1:
            button3 = buttons[1]
            print("Button3 found")
            button3.click()
            print("Button3 clicked")
        else:
            print("Not enough elements found with the class 'rec-input-radio'")
            return

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="per-availability-main"]/div/div[5]/div[3]/div[2]/div[2]/div/div[2]/div/button/span/span'))
        )
        print("Availability information loaded")

        # availability_element = driver.find_element(By.XPATH, '//*[@id="per-availability-main"]/div/div[5]/div[3]/div[2]/div[2]/div/div[2]/div/button/span/span')
        availability_element = driver.find_element(By.XPATH, '//*[@id="pean')
        availability_text = availability_element.text.strip()
        print(f"Availability Information: {availability_text}")

        if availability_text != '0':  # Change this condition as per your requirement
            message = f"Availability found for {url}\nAvailability Information: {availability_text}"
            send_telegram_message(message)

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)
        send_telegram_message(error_message)

    finally:
        driver.quit()

def check_availability_for_dates(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y-%m-%d')
        url = f'https://www.recreation.gov/permits/72192/registration/detailed-availability?date={formatted_date}'
        print(f"Checking availability for {formatted_date}")
        scrape_availability(url)
        current_date += timedelta(days=1)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
start_date = datetime.strptime('2024-08-27', '%Y-%m-%d')
end_date = datetime.strptime('2024-08-30', '%Y-%m-%d')

check_availability_for_dates(start_date, end_date)
