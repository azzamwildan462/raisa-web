import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time
import random
import os

internet_state = 0
credentials_state = 0
error_str = ""

# Initialize lists to store usernames and passwords
users = []
passwords = []

used_username_to_be_logged_in = ""
used_password_to_be_logged_in = ""

def save_log():
    global internet_state
    global credentials_state
    global error_str

    # log to json with time, internet_state, credentials_state
    with open(os.environ.get('UI_ASSETS') + '/misc/get_internet_its_log.json', 'w') as file:
        file.write('{\n')
        file.write(f'  "time": "{time.strftime("%Y-%m-%d %H:%M:%S")}",\n')
        file.write(f'  "credential: "{used_username_to_be_logged_in} {used_password_to_be_logged_in},\n')
        file.write(f'  "internet_state": "{internet_state}",\n')
        file.write(f'  "credentials_state": "{credentials_state}"\n')
        file.write(f'  "error": "{error_str}"\n')
        file.write('}\n')

def check_internet_status():
    global internet_state
    global error_str

    try:
        response = requests.get("https://www.facebook.com")
        status_code = response.status_code

        if status_code != 200:
            internet_state = -4
            save_log()
    
    except requests.exceptions.RequestException as e:
        internet_state = -5
        error_str = e
        save_log()


def get_internet_access():
    global internet_state
    global error_str
    
    try: 
        print("Trying to get internet access")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.binary_location = "/usr/bin/google-chrome"
        driver = webdriver.Chrome(options=chrome_options)
        print("Driver is ready")
        driver.get("https://myits-app.its.ac.id/internet/index.php")
        driver.implicitly_wait(10)
        driver.get("https://myits-app.its.ac.id/internet/auth.php")
        driver.implicitly_wait(10)

        username_id = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'username')))
        username_id.send_keys(used_username_to_be_logged_in)

        continue_id = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'continue')))
        continue_id.click()

        password_id = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'password')))
        password_id.send_keys(used_password_to_be_logged_in)

        login_id = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'login')))
        login_id.click()

        driver.implicitly_wait(10)

        session_state_cookie_set = False
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'session_state':
                session_state_cookie_set = True
                break

        driver.get("https://my.its.ac.id")
        driver.implicitly_wait(10)

        # driver.save_screenshot('screenshot.png')

        driver.quit()
        if session_state_cookie_set:
            internet_state = 0
        else:
            internet_state = -3
        

    
    except Exception as e:
        error_str = e
        internet_state = -3




#====================================================================================================

# Open the file and read its contents
with open(os.environ.get('UI_ASSETS') + '/misc/get_internet_its_credentials.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        username, password = line.strip().split()

        # Append username and password to respective lists
        users.append(username)
        passwords.append(password)

if len(users) == 0:
    credentials_state = -1
    save_log()
    exit(1)

if len(users) == 1:
    used_username_to_be_logged_in = users[0]
    used_password_to_be_logged_in = passwords[0]
else:
    random_number = random.randint(0, len(users)-1)
    used_username_to_be_logged_in = users[random_number]
    used_password_to_be_logged_in = passwords[random_number]

credentials_state = 0

check_internet_status()
if internet_state > -4:
    print("Internet access is available, exiting...")
    internet_state = 0
    save_log()
    exit(0)

# Run the get_internet_access function
get_internet_access()

save_log()


