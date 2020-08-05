import json

from bs4 import BeautifulSoup

from domain.book import BookBuilder

try:
    import requests
    from helper import config_reader, response_to_json_dict
except Exception as e:
    print(e)


def book_provider(book_id):
    CONFIG = config_reader()

    url = CONFIG['BOOK_INFO_ENDPOINT'].replace("ID", book_id).replace("DEVELOPER_KEY", CONFIG['CLIENT_KEY'])

    response = requests.get(url)

    print("Request sent 📨")
    dict_response = response_to_json_dict(response)

    # using Builder to initialize Book object
    book = BookBuilder.initialize()

    # initializing Book Title
    book_title = dict_response['GoodreadsResponse']['book']['title'].split('(')[0].strip()
    book = book.withBookName(book_title)

    # adding authors as a list
    authors = dict_response['GoodreadsResponse']['book']['authors']['author']
    authors_list = list()

    for author in authors:
        authors_list.append(author['name'])

    book = book.hasAuthors(authors_list)

    # adding ID
    ID = dict_response['GoodreadsResponse']['book']['id']
    book = book.hasId(ID)

    # adding ISBN
    isbn = dict_response['GoodreadsResponse']['book']['isbn']
    book = book.hasISBN(isbn)

    # adding ISBN13
    isbn13 = dict_response['GoodreadsResponse']['book']['isbn13']
    book = book.hasISBN13(isbn13)

    # adding Publication Date
    publication_date = f"{dict_response['GoodreadsResponse']['book']['publication_day']}-{dict_response['GoodreadsResponse']['book']['publication_month']}-{dict_response['GoodreadsResponse']['book']['publication_year']}"
    book = book.wasPublishedOn(publication_date)

    # adding Best Book ID
    best_book_id = dict_response['GoodreadsResponse']['book']['work']['best_book_id']['#text']
    book = book.hasBestBookId(best_book_id)

    # adding Reviews Count
    reviews_count = dict_response['GoodreadsResponse']['book']['work']['reviews_count']['#text']
    book = book.hasReviewsCount(reviews_count)

    # adding Ratings Sum
    ratings_sum = dict_response['GoodreadsResponse']['book']['work']['ratings_sum']['#text']
    book = book.hasRatingsSum(ratings_sum)

    # adding Ratings Count
    ratings_count = dict_response['GoodreadsResponse']['book']['work']['ratings_count']['#text']
    book = book.hasRatingsCount(ratings_count)

    # adding Text Ratings Count
    text_reviews_count = dict_response['GoodreadsResponse']['book']['work']['text_reviews_count']['#text']
    book = book.hasTextReviewsCount(text_reviews_count)

    # adding Avg Rating
    avg_rating = dict_response['GoodreadsResponse']['book']['average_rating']
    book = book.hasAverageRatings(avg_rating)

    # extracting reviews url from iframe
    reviews_widget = dict_response['GoodreadsResponse']['book']['reviews_widget']
    review_widgets_json = json.loads(json.dumps(reviews_widget))

    soup = BeautifulSoup(review_widgets_json, features="html.parser")
    reviews_url = soup.find('iframe').get('src').replace('DEVELOPER_ID', CONFIG['CLIENT_KEY']).replace("amp;","")
    return book.build(), reviews_url


def reviews_provider(url):
    pass

def reviewer_provider():
    pass
