from app import CONFIG
from domain.provider import reviewer_provider
from support import get_api_response, oauth_validator

oauth_validator()
dict_response, json_response = get_api_response("https://www.goodreads.com/user/show/2738978.xml?key=OKwj2qRaOnsUBJqogIu8tw")
reviewer = reviewer_provider(dict_response=dict_response, CONFIG=CONFIG)