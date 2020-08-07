import json
import re

from bs4 import BeautifulSoup

from domain.book import BookBuilder
from domain.review import ReviewBuilder
from domain.reviewer import ShelfBuilder, ReviewerBuilder

try:
    import requests
    from support.helper import config_reader, response_to_json_dict, make_html_soup, get_api_response, oauth_validator, \
        get_auth_api_response
except Exception as e:
    print(e)


def book_provider(book_id):
    CONFIG = config_reader()

    dict_response, json_response = get_api_response(CONFIG['BOOK_INFO_ENDPOINT'], "BOOKID", book_id)

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
    if isbn == "":
        print("No ISBN.. Using regex to explicit scrapping...")
    else:
        isbn = re.findall(r'ISBN (\d{10})', json_response)[0]
    book = book.hasISBN(isbn)

    # adding ISBN13
    isbn13 = dict_response['GoodreadsResponse']['book']['isbn13']
    if isbn13 == "":
        print("No ISBN.. Using regex to explicit scrapping...")
    else:
        isbn13 = re.findall(r'ISBN13: (\d{13})', json_response)[0]
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
    reviews_url = soup.find('iframe').get('src')

    book = book.build()

    # api request need to be done there
    return book, reviews_url


def reviews_provider(reviews_url, driver,book_id):
    page = 0
    while True:
        page += 1
        reviews_url = reviews_url + f'&page={page}'
        print(f"Driver Getting URL 🌍 : {reviews_url}")
        response = requests.get(reviews_url)
        html = response.content
        soup = make_html_soup(html)

        reviews_links_in_a_page = soup.find_all('a', attrs={'class': 'gr_more_link'})
        if len(reviews_links_in_a_page) == 0:
            break

        for review_link in reviews_links_in_a_page:

            review = ReviewBuilder.initialize()
            review_url = review_link.get('href')
            driver.get(review_url)
            html = driver.page_source
            soup = make_html_soup(html)
            review_id = re.findall(r'(\d{1,13})', review_url)[0]
            review = review.hasReviewID(review_id)

            reviewer_page = soup.find('h1').find('a').get('href')
            print(f"Reviewer's Home Page Link : {'https://www.goodreads.com' + reviewer_page}")

            reviewer_id = re.findall(r'(\d{1,13})', reviewer_page)[0]
            review = review.byReviewerID(reviewer_id)

            rating = soup.find('meta', attrs={'itemprop': 'ratingValue'}).get('content')
            review = review.hasRating(rating)

            review_text = soup.find('div', attrs={'itemprop': 'reviewBody'}).get_text().strip()
            review = review.hasText(review_text)

            likes = soup.find('span', attrs={'class': 'likesCount'}).get_text().split(' likes')[0].strip()
            review = review.hasLikes(likes)

            review = review.hasBookId(book_id)
            review = review.build()

            print("=========================================================================================")
            reviewer = reviewer_provider(reviewer_id)

            # api request to be done here


def reviewer_provider(reviewer_id):
    CONFIG = config_reader()
    reviewer = ReviewerBuilder.initialize()
    dict_response, json_response = get_api_response(CONFIG['REVIEWER_INFO_ENDPOINT'], 'USERID', reviewer_id)

    reviewer_name = dict_response['GoodreadsResponse']['user']['name']
    reviewer = reviewer.hasName(reviewer_name).hasID(reviewer_id)

    if 'private' not in dict_response['GoodreadsResponse']['user']:
        shelves = []
        temp_shelves = dict_response['GoodreadsResponse']['user']['user_shelves']['user_shelf']

        for temp_shelf in temp_shelves:
            shelf = ShelfBuilder.initialize()

            shelf_id = temp_shelf['id']['#text']
            shelf = shelf.hasShelfID(shelf_id)

            shelf_name = temp_shelf['name']
            shelf = shelf.hasShelfName(shelf_name)

            book_count = temp_shelf['book_count']['#text']
            shelf = shelf.hasBookCount(book_count)

            shelf = shelf.build()

            shelves.append(shelf)

        reviewer = reviewer.hasShelves(shelves)

        number_of_reviews = dict_response['GoodreadsResponse']['user']['reviews_count']['#text']
        reviewer = reviewer.hasTotalReviews(number_of_reviews)

        friends_count = dict_response['GoodreadsResponse']['user']['friends_count']['#text']
        reviewer = reviewer.hasFriendsCount(friends_count)

        following = []
        page = 0
        while True:
            page += 1
            dict_response, json_response = get_auth_api_response(CONFIG['FOLLOWING_INFO_ENDPOINT'], 'USERID',
                                                                 reviewer_id,
                                                                 page)
            total_number_of_following = dict_response['GoodreadsResponse']['following']['@total']

            following_ = dict_response['GoodreadsResponse']['following']['user']

            if total_number_of_following == "1":
                following.append(following_['id'])
            elif total_number_of_following == "0":
                following = []
            else:

                for f in following_:
                    following.append(f['id'])

            following_end_count = dict_response['GoodreadsResponse']['following']['@end']
            print(f"Pulled {following_end_count} out of {total_number_of_following} following")
            if following_end_count == total_number_of_following:
                break

        reviewer = reviewer.hasFollowing(following)

        followers = []
        page = 0
        while True:
            page += 1
            dict_response, json_response = get_auth_api_response(CONFIG['FOLLOWERS_INFO_ENDPOINT'], 'USERID',
                                                                 reviewer_id,
                                                                 page)
            total_number_of_followers = dict_response['GoodreadsResponse']['followers']['@total']

            followers_ = dict_response['GoodreadsResponse']['followers']['user']

            if total_number_of_followers == "1":
                followers.append(followers_['id'])
            elif total_number_of_followers == "0":
                followers = []
            else:
                for f in followers_:
                    followers.append(f['id'])

            followers_end_count = dict_response['GoodreadsResponse']['followers']['@end']
            print(f"Pulled {followers_end_count} out of {total_number_of_followers} followers")
            if followers_end_count == total_number_of_followers:
                break

        reviewer = reviewer.hasFollowers(followers)

    reviewer = reviewer.build()

    return reviewer
