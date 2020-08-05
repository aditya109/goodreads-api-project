try:
    import xmltodict
    import configparser
    import collections
    import json
except Exception as e:
    print(e)

def response_to_json_dict(response):
    # initializing a dict for storing response
    dict_response = collections.defaultdict()
    # initializing an empty string
    json_response = ""
    # checking response status code
    if response.status_code == 200:

        print(f"Response Status Code : {response.status_code} ✔️", end="\n\n")
        # decoding byte-xml response to `utf-8` string
        string_xml_response = response.content.decode("utf-8")
        # parsing `utf-8` to json
        json_response = json.dumps(xmltodict.parse(string_xml_response))
        # converting json to dict
        dict_response = json.loads(json_response)
    else:
        print(f"Response Status Code : {response.status_code} ❌", end="\n\n")

    return dict_response

def config_reader():
    # reading the config files
    config = configparser.ConfigParser()

    # for Aditya
    config.read("D:/Projects/config/config2.ini")

    # for Manel
    # config.read("./config.ini")

    CONFIG = dict()
    CONFIG['CLIENT_KEY'] = config['credentials']['client_key']  # string
    CONFIG['CLIENT_SECRET'] = config['credentials']['client_secret']  # string

    CONFIG['EMAIL_ID'] = config['credentials']['email_id']  # string
    CONFIG['PASSWORD'] = config['credentials']['password']  # string

    CONFIG['CHROMEDRIVER'] = config['resources-path']['chromedriver']
    CONFIG['GECKODRIVER'] = config['resources-path']['geckodriver']

    CONFIG['ROOT_URL'] = config['nav-links']['root_url']  # string
    CONFIG['CHILD_URLS'] = config['nav-links']['child_urls'].split(',')  # string

    CONFIG['BOOK_INFO_ENDPOINT'] = config['api-route']['book_info_endpoint']

    CONFIG['HOST_NAME'] = config['db-config']['host_name']
    CONFIG['DB'] = config['db-config']['db']
    CONFIG['PORT'] = config['db-config']['port']
    CONFIG['USERNAME'] = config['db-config']['username']
    CONFIG['PASSWORD'] = config['db-config']['password']

    return CONFIG