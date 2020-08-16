try:
    import os
    import csv
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


def auth_config_reader():
    """
    Provides OAuth access tokens and access token secret
    :return:
    """
    config = configparser.ConfigParser()
    CONFIG = dict()

    config.read("auth.ini")
    CONFIG['ACCESS_TOKEN'] = config['SESSION']['access_token']
    CONFIG['ACCESS_TOKEN_SECRET'] = config['SESSION']['access_token_secret']
    return CONFIG


def auto_url_authorization(url):
    """
    automates the OAUTH procedure
    :param url: str
    :return: str
    """
    CONFIG = config_reader()
    # intializing Options of Selenium
    chrome_options = Options()
    # running webdriver in headless mode for authorization automation purposes
    chrome_options.add_argument("--headless")
    # locating webdriver on OS path
    chrome_driver_path = f'./resources/{platform.system()}/chromedriver'
    # initialzing the webdriver
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path, service_log_path='NUL')
    # deleting all cookies
    driver.delete_all_cookies()
    # getting the Auth URL
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
        # Once OAuth is successful, quiting Selenium driver to optimize CPU usage
        driver.quit()
        return 200


def clean_up(files):
    """
    Cleans up redundant files in the respository
    :param files: List
    :return:
    """
    try:
        os.remove("auth.ini")
        for file in files:
            file.close()
    except FileNotFoundError as fileE:
        print("File Not Found : auth.ini")
        print(fileE)
    except Exception as E:
        print("Error in removing auth.ini. Kindly remove it manually !")
        print(E)
        traceback.print_exc()


def config_reader():
    # reading the config files
    config = configparser.ConfigParser()
    CONFIG = dict()

    # for Aditya
    config.read("D:/Projects/config/config2.ini")

    # for Manel
    # config.read("./config.ini")

    CONFIG['CLIENT_KEY'] = config['credentials']['client_key']  # str
    CONFIG['CLIENT_SECRET'] = config['credentials']['client_secret']  # str
    CONFIG['EMAIL_ID'] = config['credentials']['email']
    CONFIG['PASSWORD'] = config['credentials']['password']

    CONFIG['ROOT_URL'] = config['nav-links']['root_url']  # str
    CONFIG['CHILD_URLS'] = config['nav-links']['child_urls'].split(',')  # str

    CONFIG['BOOK_INFO_ENDPOINT'] = config['api-route']['book_info_endpoint']
    CONFIG['REVIEWER_INFO_ENDPOINT'] = config['api-route']['reviewer_info_endpoint']
    CONFIG['FOLLOWING_INFO_ENDPOINT'] = config['api-route']['following_info_endpoint']
    CONFIG['FOLLOWERS_INFO_ENDPOINT'] = config['api-route']['followers_info_endpoint']

    CONFIG['FILETYPE'] = config['settings']['filetype']

    return CONFIG


def element_grabber(driver, param, by_type="xpath"):
    #  Grabbing elements by either xpath or Id using find_element() in driver for our Selenium
    element = None
    if by_type == "xpath":
        element = driver.find_element(By.XPATH, param)
    elif by_type == "ID":
        element = driver.find_element(By.ID, param)
    return element


def file_creator(filenames):
    """
    Creates files according to the names gives
    :param filenames: List
    :return:
    """
    files = []
    for filename in filenames:
        file = open(filename, "w", encoding="utf-8", newline='')
        files.append(file)
    return files


def get_api_response(url):
    # requesting response from url
    response = requests.get(url)
    # converting response_xml to dict
    return response_to_json_dict(response)


def get_auth_api_response(url, field, value, page=1):
    """

    :param url: strin
    :param field: str
    :param value: str
    :param page: int
    :return: tuple
    """
    key, secret, access_token, access_token_secret = config_reader()['CLIENT_KEY'], \
                                                     config_reader()['CLIENT_SECRET'], \
                                                     auth_config_reader()['ACCESS_TOKEN'], \
                                                     auth_config_reader()['ACCESS_TOKEN_SECRET']
    url = url.replace(field, value)
    print(f"URL ==> {url}")
    new_session = OAuth1Session(
        consumer_key=key,
        consumer_secret=secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    params = {'key': key, 'page': page}
    response = new_session.get(url=url, params=params)
    return tuple(response_to_json_dict(response))


def get_page_content_response(url):
    # requesting response from url
    response = requests.get(url)
    # converting response_xml to dict
    return make_html_soup(response.content.decode('utf-8', 'ignore'))


def make_html_soup(html):
    # return BeautifulSoup object
    return BeautifulSoup(html, features='lxml')


def oauth_validator():
    """
    Performs OAuth Validation for the project
    :return:
    """
    CONFIG = config_reader()
    key, secret = CONFIG['CLIENT_KEY'], CONFIG['CLIENT_SECRET']

    #  initialising OAuth Service
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

    # initiate GET response for auth URL
    authorize_url = goodreads.get_authorize_url(request_token)
    print('✔️ Starting OAuth...')
    print('Visiting this URL in your browser: ' + authorize_url)
    response = auto_url_authorization(authorize_url)
    if response == 200:
        print("🆗 GoodreadsAPI Project has been authorized with OAuth")

    session = goodreads.get_auth_session(request_token, request_token_secret)

    # these values are what you need to save for subsequent access.
    ACCESS_TOKEN = session.access_token
    ACCESS_TOKEN_SECRET = session.access_token_secret

    config = configparser.ConfigParser()

    config['SESSION'] = {
        'access_token': ACCESS_TOKEN,
        'access_token_secret': ACCESS_TOKEN_SECRET
    }

    # writes OAuth tokens to a config file
    with open('auth.ini', 'w') as configfile:
        config.write(configfile)


def perform_parallel_tasks(function, items) -> List:
    # performs parallel tasks with tool(`function`) on list(`items`)
    results = []
    # using multithreading concept to fasten the web pull
    with ThreadPoolExecutor(50) as executor:
        # executing GET request of link asynchronously
        futures = []
        for item in items:
            if isinstance(item, list):
                futures.append(executor.submit(function, *item))
            else:
                futures.append(executor.submit(function, item))
        # pulling the results from the concurrent execution array `futures`
        for result in concurrent.futures.as_completed(futures):
            # this gives me a list of future object
            results.append(result)

    return results


def response_to_json_dict(response):
    """
    converts response object to JSON type
    """
    # initializing a dict for storing response
    dict_response = collections.defaultdict()
    # initializing an empty str
    json_response = ""
    # checking response status code
    if response.status_code == 200:

        # print(f"Response Status Code : {response.status_code} ✔️", end="\n\n")
        # decoding byte-xml response to `utf-8` str
        str_xml_response = response.content.decode("utf-8")
        # parsing `utf-8` to json
        json_response = json.dumps(xmltodict.parse(str_xml_response))
        # converting json to dict
        dict_response = json.loads(json_response)
    else:
        print(f"Response Status Code : {response.status_code} ❌", end="\n\n")

    return dict_response, json_response


# OK
def write_book_object_to_file(file, book=None, mode="normal"):
    """
    writes book object to book file
    """
    CONFIG = config_reader()
    extension = CONFIG['FILETYPE']

    if extension == "json":
        json_obj = json.dumps(book.__dict__)
        json.dump(json_obj, file)
    elif extension == "csv":
        writer = csv.writer(file, delimiter=',', quotechar='"')
        if mode == "init":
            writer.writerow(
                ["book_name", "Id", "authors", "isbn", "isbn13", "publication_date", "best_book_id", "reviews_count",
                 "ratings_sum", "ratings_count", "text_reviews_count", "average_ratings"])
        else:
            writer.writerow([
                book.book_name,
                book.id,
                book.authors,
                book.isbn,
                book.isbn13,
                book.publication_date,
                book.best_book_id,
                book.reviews_count,
                book.ratings_sum,
                book.ratings_count,
                book.text_reviews_count,
                book.average_ratings
            ])

        file.flush()


# OK
def write_review_object_to_file(file, review=None, mode="normal"):
    """
    writes review object to review file
    """
    CONFIG = config_reader()
    extension = CONFIG['FILETYPE']

    if extension == "json":
        json_obj = json.dumps(review.__dict__)
        json.dump(json_obj, file)
    elif extension == "csv":
        writer = csv.writer(file, delimiter=',', quotechar='"')
        if mode == "init":
            writer.writerow(
                ["review_id", "reviewer_id", "rating", "likes", "review", "book_id"])
        else:
            writer.writerow([
                review.review_id,
                review.reviewer_id,
                review.rating,
                review.likes,
                review.review,
                review.book_id
            ])

    file.flush()


# OK
def write_reviewer_object_to_file(file, reviewer=None, mode="normal"):
    """
    writes reviewer object to reviewer file
    """
    CONFIG = config_reader()
    extension = CONFIG['FILETYPE']

    if extension == "json":
        json_obj = json.dumps(reviewer.__dict__)
        json.dump(json_obj, file)
    elif extension == "csv":
        writer = csv.writer(file, delimiter=',', quotechar='"')
        if mode == "init":
            writer.writerow(
                ["reviewer_name", "reviewer_id", "shelves", "number_of_reviews", "friends_count", "following",
                 "followers"])
        else:
            shelves = []
            for shelf in reviewer.shelves:
                s = [shelf.get_shelf_id(), shelf.get_shelf_name(), shelf.get_book_count()]
                shelves.append(s)
            writer.writerow([
                reviewer.reviewer_name,
                reviewer.reviewer_id,
                shelves,
                reviewer.number_of_reviews,
                reviewer.friends_count,
                reviewer.following,
                reviewer.followers

            ])

        file.flush()
