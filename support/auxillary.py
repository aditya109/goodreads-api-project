try:
    import os
    import json
    import requests
    import platform
    import xmltodict
    import traceback
    import concurrent
    import collections
    import configparser
    from bs4 import BeautifulSoup
    from typing import List
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from rauth import OAuth1Service, OAuth1Session
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from concurrent.futures.thread import ThreadPoolExecutor
except Exception as e:
    print(e)


def response_to_json_dict(response):
    # initializing a dict for storing response
    dict_response = collections.defaultdict()
    # initializing an empty string
    json_response = ""
    # checking response status code
    if response.status_code == 200:

        # print(f"Response Status Code : {response.status_code} ✔️", end="\n\n")
        # decoding byte-xml response to `utf-8` string
        string_xml_response = response.content.decode("utf-8")
        # parsing `utf-8` to json
        json_response = json.dumps(xmltodict.parse(string_xml_response))
        # converting json to dict
        dict_response = json.loads(json_response)
    else:
        print(f"Response Status Code : {response.status_code} ❌", end="\n\n")

    return dict_response, json_response


def auth_config_reader():
    # Provides OAuth access tokens and access token secret
    config = configparser.ConfigParser()
    CONFIG = dict()

    config.read("auth.ini")
    CONFIG['ACCESS_TOKEN'] = config['SESSION']['access_token']
    CONFIG['ACCESS_TOKEN_SECRET'] = config['SESSION']['access_token_secret']
    return CONFIG


def config_reader():
    # reading the config files
    config = configparser.ConfigParser()
    CONFIG = dict()

    # for Aditya
    config.read("D:/Projects/config/config2.ini")

    # for Manel
    # config.read("./config.ini")

    CONFIG['CLIENT_KEY'] = config['credentials']['client_key']  # string
    CONFIG['CLIENT_SECRET'] = config['credentials']['client_secret']  # string
    CONFIG['EMAIL_ID'] = config['credentials']['email']
    CONFIG['PASSWORD'] = config['credentials']['password']

    CONFIG['ROOT_URL'] = config['nav-links']['root_url']  # string
    CONFIG['CHILD_URLS'] = config['nav-links']['child_urls'].split(',')  # string

    CONFIG['BOOK_INFO_ENDPOINT'] = config['api-route']['book_info_endpoint']
    CONFIG['REVIEWER_INFO_ENDPOINT'] = config['api-route']['reviewer_info_endpoint']
    CONFIG['FOLLOWING_INFO_ENDPOINT'] = config['api-route']['following_info_endpoint']
    CONFIG['FOLLOWERS_INFO_ENDPOINT'] = config['api-route']['followers_info_endpoint']

    CONFIG['FILETYPE'] = config['settings']['filetype']

    return CONFIG


def make_html_soup(html):
    # return BeautifulSoup object
    return BeautifulSoup(html, features='lxml')


def get_api_response(url):
    # requesting response from url
    response = requests.get(url)
    # converting response_xml to dict
    return response_to_json_dict(response)


def get_auth_api_response(url, field, value, page=1):
    key, secret, access_token, access_token_secret = config_reader()['CLIENT_KEY'], config_reader()['CLIENT_SECRET'], \
                                                     auth_config_reader()['ACCESS_TOKEN'], auth_config_reader()[
                                                         'ACCESS_TOKEN_SECRET']
    url = url.replace(field, value)
    print(url)
    new_session = OAuth1Session(
        consumer_key=key,
        consumer_secret=secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    params = {'key': key, 'page': page}
    response = new_session.get(url=url, params=params)
    return response_to_json_dict(response)

def element_grabber(driver, param, by_type="xpath"):
    #  Grabbing elements by either xpath or id using find_element() in driver for our Selenium
    element = None
    if by_type == "xpath":
        element = driver.find_element(By.XPATH, param)
    elif by_type == "ID":
        element = driver.find_element(By.ID, param)
    return element

def auto_url_authorization(url):
    CONFIG = config_reader()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver_path = f'./resources/{platform.system()}/chromedriver'
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path, service_log_path='NUL')
    driver.delete_all_cookies()
    driver.get(url)

    email_input_box = element_grabber(driver,
        "/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/fieldset/div[1]/input")
    # sending the email as input to the above field
    email_input_box.send_keys(CONFIG['EMAIL_ID'])
    print("🔱 Sending the EMAIL ID...")

    # grabbing the password field
    password_textbox = element_grabber(driver,
        "/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/fieldset/div[2]/input")
    # sending the password as input to the above field
    password_textbox.send_keys(CONFIG['PASSWORD'])
    print("🔑 Sending the Password... ")
    # grabbing sign in button
    sign_btn = element_grabber(driver,
        "/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/fieldset/div[5]/input")
    # submitting the login form
    sign_btn.click()
    current_url = driver.current_url
    if "oauth_token" in current_url:
        print("🧭 OAuth Token Found !")
    if "authorize=1" in current_url:
        print("🎉 OAuth Successful !")
        driver.quit()
        return 200

def oauth_validator():
    CONFIG = config_reader()
    key, secret = CONFIG['CLIENT_KEY'], CONFIG['CLIENT_SECRET']

    goodreads = OAuth1Service(
        consumer_key=key,
        consumer_secret=secret,
        name='goodreads',
        request_token_url='https://www.goodreads.com/oauth/request_token',
        authorize_url='https://www.goodreads.com/oauth/authorize',
        access_token_url='https://www.goodreads.com/oauth/access_token',
        base_url='https://www.goodreads.com/'
    )
    # head_auth=True is important here; this doesn't work with oauth2 for some reason
    request_token, request_token_secret = goodreads.get_request_token(header_auth=True)

    authorize_url = goodreads.get_authorize_url(request_token)
    print('✔️ Starting OAuth...')
    print('Visiting this URL in your browser: ' + authorize_url)
    response = auto_url_authorization(authorize_url)
    if response == 200:
        print("🆗 Application has been OAuth")

    session = goodreads.get_auth_session(request_token, request_token_secret)

    # these values are what you need to save for subsequent access.
    ACCESS_TOKEN = session.access_token
    ACCESS_TOKEN_SECRET = session.access_token_secret

    config = configparser.ConfigParser()

    config['SESSION'] = {
        'access_token': ACCESS_TOKEN,
        'access_token_secret': ACCESS_TOKEN_SECRET
    }

    with open('auth.ini', 'w') as configfile:
        config.write(configfile)


def clean_up(files):
    try:
        os.remove("auth.ini")
        for file in files:
            file.close()
    except FileNotFoundError as e:
        print("File Not Found : auth.ini")
    except Exception as E:
        print("Error in removing auth.ini. Kindly remove it manually !")
        traceback.print_exc()


def file_creator(filenames):
    files = []
    for filename in filenames:
        file = open(filename, "w",  encoding="utf-8" ,newline='')
        files.append(file)
    return files

def get_page_content_response(url):
    # requesting response from url
    response = requests.get(url)
    # converting response_xml to dict
    return make_html_soup(response.content.decode('utf-8', 'ignore'))

def perform_parallel_tasks(function, items) -> List:
    results = []
    # using multithreading concept to fasten the web pull
    with ThreadPoolExecutor(50) as executor:
        # executing GET request of link asynchronously
        futures = [executor.submit(function, item) for item in items]
        # pulling the results from the concurrent execution array `futures`
        for result in concurrent.futures.as_completed(futures):
            # this gives me a list of future object
            results.append(result)

    return results