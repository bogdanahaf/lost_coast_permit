from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

def scrape_availability(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Optional: Run Chrome in headless mode
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    try:
        # Example: Click on buttons to load availability information
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

        # Find the second element with the class name 'rec-input-radio'
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

        # Wait for the availability information to load after button clicks
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="per-availability-main"]/div/div[5]/div[3]/div[2]/div[2]/div/div[2]/div/button/span/span'))
        )
        print("Availability information loaded")

        # Extract and print availability information
        availability_element = driver.find_element(By.XPATH, '//*[@id="per-availability-main"]/div/div[5]/div[3]/div[2]/div[2]/div/div[2]/div/button/span/span')
        availability_text = availability_element.text.strip()
        print(f"Availability Information: {availability_text}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

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

# Example usage
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
start_date = datetime.strptime('2024-08-20', '%Y-%m-%d')
end_date = datetime.strptime('2024-08-23', '%Y-%m-%d')

check_availability_for_dates(start_date, end_date)
