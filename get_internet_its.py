import asyncio
from pyppeteer import launch
import time
import random
import os

internet_state = 0
credentials_state = 0

# Initialize lists to store usernames and passwords
users = []
passwords = []

used_username_to_be_logged_in = ""
used_password_to_be_logged_in = ""

def save_log():
    global internet_state
    global credentials_state

    # log to json with time, internet_state, credentials_state
    with open(os.environ.get('UI_ASSETS') + '/misc/get_internet_its_log.json', 'w') as file:
        file.write('{\n')
        file.write(f'  "time": "{time.strftime("%Y-%m-%d %H:%M:%S")}",\n')
        file.write(f'  "internet_state": "{internet_state}",\n')
        file.write(f'  "credentials_state": "{credentials_state}"\n')
        file.write('}\n')

async def check_internet_status():
    global internet_state

    browser = await launch(headless=True,executablePath='/usr/bin/google-chrome')
    page = await browser.newPage()

    # Navigate to youtube.com 
    try:
        # Wait for navigation with a timeout of 10 seconds
        response = await asyncio.wait_for(page.goto('https://youtube.com'), timeout=10)

        if response.status != 200:
            internet_state = -4
            save_log()
            exit(1)

    except asyncio.TimeoutError:
        internet_state = -5
        save_log()
        exit(1)

async def get_internet_access():
    global internet_state

    browser = await launch(headless=True,executablePath='/usr/bin/google-chrome')
    page = await browser.newPage()

    # Navigate to the login page
    try:
        # Wait for navigation with a timeout of 10 seconds
        response = await asyncio.wait_for(page.goto('https://myits-app.its.ac.id/internet/auth.php'), timeout=10)

        if response.status != 200:
            internet_state = -2
            save_log()
            exit(1)

    except asyncio.TimeoutError:
        internet_state = -1
        save_log()
        exit(1)

    # Check if #username is exist 
    username_exists = await page.querySelector("#username")

    if not username_exists:
        internet_state = -2
        save_log()
        exit(1)

    await page.type("#username", users[0])
    await page.click("#continue")
    time.sleep(1)
    await page.type("#password", passwords[0])
    time.sleep(1)
    await page.click("#login")

    # Wait for the page to load
    try:
        await asyncio.wait_for(page.waitForNavigation(), timeout=19)
    except asyncio.TimeoutError:
        internet_state = -1
        save_log()
        exit(1)

    # Get cookies
    cookies = await page.cookies()

    # Check if "session_state" is set in any cookie
    session_state_exists = any(cookie['name'] == 'session_state' for cookie in cookies)

    await page.goto("https://my.its.ac.id")

    # Close the browser
    await browser.close()

    if session_state_exists:
        internet_state = 0
    else:
        internet_state = -3

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

asyncio.get_event_loop().run_until_complete(check_internet_status())
if internet_state > -4:
    internet_state = 0
    save_log()
    exit(0)

# Run the get_internet_access function
asyncio.get_event_loop().run_until_complete(get_internet_access())

save_log()


