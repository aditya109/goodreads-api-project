"""For running this script, please ensure that `sample` directory has `resources` directory container chromedriver
for your OS executable file, clone this repository for better usage.


"""

try:
    import json
    import re
    import pprint
    import xmltodict
    import requests
    import urllib
    import os
    import platform
    import time
    from backports import configparser
    from bs4 import BeautifulSoup
    from collections import defaultdict
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
except Exception as e:
    print(e)

# reading the config files
config = configparser.ConfigParser()

# for Aditya
# config.read("D:/Projects/config/config2.ini")

# for Manel
config.read("./config.ini")
# =======================================================
CLIENT_KEY = config['credentials']['client_key']  # string
CLIENT_SECRET = config['credentials']['client_secret']  # string
EMAIL_ID = config['credentials']['email_id']  # string
PASSWORD = config['credentials']['password']  # string
# =======================================================
CHROMEDRIVER = config['resources-path']['chromedriver']
GECKODRIVER = config['resources-path']['geckodriver']

# =======================================================
ROOT_URL = config['nav-links']['root_url']  # string
CHILD_URLS = config['nav-links']['child_urls'].split(',')  # string
# =======================================================
# identifying OS of the host
print(f"Accessing OS ... Found : {platform.system()}")

# adding options for headless browsing(headless meaning running in background)
chrome_options = Options()
chrome_options.add_argument("--headless")
# declaring path for webdriver
chrome_driver_path = f"./resources/{platform.system()}/chromedriver"
# initializing Chrome webdriver with options `headless` and executable_path `\path\to\chromedriver`
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path)
driver.delete_all_cookies()

# initializing a Pretty Printer
pp = pprint.PrettyPrinter(indent=2)


def element_grabber(param, by_type="xpath"):
    global driver
    element = None
    if by_type == "xpath":
        element = driver.find_element(By.XPATH, param)
    elif by_type == "id":
        element = driver.find_element(By.ID, param)
    return element


def response_to_json_dict(response):
    # initializing a dict for storing response
    dict_response = defaultdict()
    # initializing an empty string
    json_response = ""
    # checking response status code
    if response.status_code == 200:

        print(f"Response Status Code : {response.status_code} ✔️")
        # decoding byte-xml response to `utf-8` string
        string_xml_response = response.content.decode("utf-8")
        # parsing `utf-8` to json
        json_response = json.dumps(xmltodict.parse(string_xml_response))
        # converting json to dict
        dict_response = json.loads(json_response)
    else:
        print(f"Response Status Code : {response.status_code} ❌")

    return dict_response, json_response


def link_navigator():

    if os.name == "nt":
        _ = os.system('cls')

    global driver
    # opening the goodreads website using selenium framework
    driver.get(ROOT_URL)
    # logging into goodreads API as a developer
    try:

        # grabbing the email field
        email_input_box = element_grabber(
            "/html/body/div[2]/div[1]/div/div/div[1]/div/div/form/div[1]/input[1]")
        # sending the email as input to the above field
        email_input_box.send_keys(EMAIL_ID)

        # grabbing the password field
        password_textbox = element_grabber(
            "/html/body/div[2]/div[1]/div/div/div[1]/div/div/form/div[2]/div/input")
        # sending the password as input to the above field
        password_textbox.send_keys(PASSWORD)

        # grabbing sign in button
        sign_btn = element_grabber(
            "/html/body/div[2]/div[1]/div/div/div[1]/div/div/form/div[3]/input[1]")
        # submitting the login form
        sign_btn.click()

        for child_url in CHILD_URLS:
            # find number_of_books on the list
            html = driver.page_source
            soup = BeautifulSoup(html, features='lxml')
            for link in soup.find_all('a'):
                print(link.get('href'))


        # number_of_books = element_grabber().text
        # print("Number of Books : " + number_of_books)
        # retrieval_count = 0

    except Exception as exception:
        print(exception)
    finally:
        driver.quit()


# START HERE
if __name__ == "__main__":
    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')

    link_navigator()

    input("\n\n\nPress enter to exit 🚀...")

    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')
