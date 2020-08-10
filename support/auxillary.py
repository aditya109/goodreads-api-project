try:
    import xmltodict
    import configparser
    import collections
    import json
    import os
    import traceback
    import requests
    from bs4 import BeautifulSoup
    from rauth import OAuth1Service, OAuth1Session
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


def get_auth_api_response(url, field, value, page):
    key, secret, access_token, access_token_secret = config_reader()['CLIENT_KEY'], config_reader()['CLIENT_SECRET'], \
                                                     auth_config_reader()['ACCESS_TOKEN'], auth_config_reader()[
                                                         'ACCESS_TOKEN_SECRET']
    url = url.replace(field, value)
    # print(f"Request sent 📨 👉 URL : {url}")
    new_session = OAuth1Session(
        consumer_key=key,
        consumer_secret=secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    params = {'key': key, 'page': page}
    response = new_session.get(url=url, params=params)
    return response_to_json_dict(response)


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
    print('Visit this URL in your browser: ' + authorize_url)
    accepted = 'n'
    while accepted.lower() == 'n':
        # you need to access the authorize_link via a browser,
        # and proceed to manually authorize the consumer
        accepted = input('Have you authorized me? (y/n) ')

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

