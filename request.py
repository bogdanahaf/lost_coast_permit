import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from pytz import timezone
import os

# Define your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
LA_TIMEZONE = timezone('America/Los_Angeles')

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, params=params)
    print(f"Telegram response: {response.status_code} - {response.text}")
    if response.status_code == 200:
        return response.json()['result']['message_id']
    return None

def edit_telegram_message(message, message_id):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText'
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'message_id': message_id,
        'text': message
    }
    response = requests.post(url, params=params)
    print(f"Telegram edit response: {response.status_code} - {response.text}")

def pin_telegram_message(message_id):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/pinChatMessage'
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'message_id': message_id,
        'disable_notification': True
    }
    response = requests.post(url, params=params)
    print(f"Telegram pin response: {response.status_code} - {response.text}")

def get_pinned_message():
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChat'
    params = {'chat_id': TELEGRAM_CHAT_ID}
    response = requests.get(url, params=params)
    print(f"Telegram getChat response: {response.status_code} - {response.text}")
    if response.status_code == 200:
        data = response.json()
        if 'pinned_message' in data['result']:
            return data['result']['pinned_message']['message_id']
    return None

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

        availability_element = driver.find_element(By.XPATH, '//*[@id="per-availability-main"]/div/div[5]/div[3]/div[2]/div[2]/div/div[2]/div/button/span/span')
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
start_date = datetime.strptime('2024-08-20', '%Y-%m-%d')
end_date = datetime.strptime('2024-08-23', '%Y-%m-%d')

# Get the pinned message ID
pinned_message_id = get_pinned_message()
current_time = datetime.now(LA_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
message = f"Edited: {current_time}"

# Edit the pinned message or send a new one and pin it
if pinned_message_id:
    edit_telegram_message(message, pinned_message_id)
else:
    new_message_id = send_telegram_message(message)
    if new_message_id:
        pin_telegram_message(new_message_id)

check_availability_for_dates(start_date, end_date)
