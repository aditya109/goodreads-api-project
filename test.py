# Get a real consumer key & secret from: https://www.goodreads.com/api/keys
import requests
from rauth import OAuth1Service

CONSUMER_KEY = 'OKwj2qRaOnsUBJqogIu8tw'
CONSUMER_SECRET = 'SJaIMqMXnskoF7Tlabf63WkbaADRCWt0ZmeREIohow'

goodreads = OAuth1Service(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    name='goodreads',
    request_token_url='https://www.goodreads.com/oauth/request_token',
    authorize_url='https://www.goodreads.com/oauth/authorize',
    access_token_url='https://www.goodreads.com/oauth/access_token',
    base_url='https://www.goodreads.com/friend/user/80369?format=xml&key=OKwj2qRaOnsUBJqogIu8tw'
    )

# head_auth=True is important here; this doesn't work with oauth2 for some reason
request_token, request_token_secret = goodreads.get_request_token(header_auth=True)
authorize_url = goodreads.get_authorize_url(request_token)
print ('Visit this URL in your browser: ' + authorize_url)
accepted = 'n'
while accepted.lower() == 'n':
    # you need to access the authorize_link via a browser,
    # and proceed to manually authorize the consumer
    accepted = input('Have you authorized me? (y/n) ')
url = ("https://www.goodreads.com/friend/user/80369?format=xml&key=OKwj2qRaOnsUBJqogIu8tw")
response = requests.get(url)