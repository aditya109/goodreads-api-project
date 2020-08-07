from rauth import OAuth1Session

from support.helper import config_reader, oauth_validator, response_to_json_dict, auth_config_reader, \
    get_auth_api_response

CONFIG=config_reader()
key=CONFIG['CLIENT_KEY']
secret=CONFIG['CLIENT_SECRET']
url=CONFIG['FOLLOWING_INFO_ENDPOINT']

CONFIG=auth_config_reader()
access_token=CONFIG['ACCESS_TOKEN']
access_token_secret = CONFIG['ACCESS_TOKEN_SECRET']

oauth_validator()
url = url.replace('USERID', '1022982')
print(url)
new_session = OAuth1Session(
    consumer_key = key,
    consumer_secret = secret,
    access_token = access_token,
    access_token_secret = access_token_secret,
)
data = {'key':'OKwj2qRaOnsUBJqogIu8tw'}
response = new_session.get(url=url, params=data)
dict_response, json_response = response_to_json_dict(response)
print(dict_response)

# https://www.goodreads.com/user/show/1022982.xml?key=OKwj2qRaOnsUBJqogIu8tw
