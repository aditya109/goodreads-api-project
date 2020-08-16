try:
    import json
    import csv
    import re
    import pprint

    from bs4 import BeautifulSoup
    from domain.book import BookBuilder
    from domain.review import ReviewBuilder
    from domain.reviewer import ShelfBuilder, ReviewerBuilder
    import requests
    from support.auxillary import config_reader, response_to_json_dict, make_html_soup, get_api_response, \
        oauth_validator, \
        get_auth_api_response, perform_parallel_tasks
except Exception as e:
    print(e)

pp = pprint.PrettyPrinter(indent=2)


def book_provider(dict_response, json_response):
    flag = True
    # using Builder to initialize Book object
    book = BookBuilder.initialize()

    # initializing Book Title
    book_title = dict_response['GoodreadsResponse']['book']['title'].split('(')[
        0].strip()
    book = book.withBookName(book_title)

    # adding authors as a list
    authors = dict_response['GoodreadsResponse']['book']['authors']['author']
    authors_list = list()

    if isinstance(authors, list):
        for author in authors:
            authors_list.append(author['name'])
    elif isinstance(authors, dict):
        authors_list.append(authors['name'])

    book = book.hasAuthors(authors_list)

    # adding ID
    ID = dict_response['GoodreadsResponse']['book']['id']
    book = book.hasId(ID)

    # adding ISBN
    isbn = dict_response['GoodreadsResponse']['book']['isbn']
    if isbn is None:
        isbn = re.findall(r'ISBN (\d{10})', json_response)
        if len(isbn) == 0:
            flag = False
        else:
            book = book.hasISBN(isbn[0])
    else:
        book = book.hasISBN(isbn)

    if flag:
        # adding ISBN13
        isbn13 = dict_response['GoodreadsResponse']['book']['isbn13']
        if isbn13 is None:
            isbn13 = re.findall(r'ISBN13: (\d{13})', json_response)
            if len(isbn13) == 0:
                print("ISBN13 Not Found !\n")
            else:
                book = book.hasISBN13(isbn13[0])
        else:
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
        review_url = soup.find('iframe').get('src')

        book = book.build()

        return book, review_url
    else:
        return None, None


def reviews_provider(soup):
    # initializing a `ReviewBuilder` object
    review = ReviewBuilder.initialize()

    # scraping page URL off the review page
    page_url = soup.find('link').get('href')
    # using REGEX expression to extract review_id
    review_id = re.findall(r'(\d{1,13})', page_url)[0]
    # adding review_id to `review` object
    review = review.hasReviewID(review_id)

    reviewer_page = soup.find('h1').find('a').get('href')
    reviewer_id = re.findall(r'(\d{1,13})', reviewer_page)[0]
    review = review.byReviewerID(reviewer_id)

    rating = soup.find(
        'meta', attrs={'itemprop': 'ratingValue'}).get('content')
    review = review.hasRating(rating)

    review_text = soup.find(
        'div', attrs={'itemprop': 'reviewBody'}).get_text().strip()
    review = review.hasText(review_text)

    likes = soup.find('span', attrs={'class': 'likesCount'})
    if likes is not None:
        likes = likes.get_text().split(' likes')[0].strip()
        review = review.hasLikes(likes)

    book_url = soup.find('a', attrs={'class': 'bookTitle', 'itemprop': 'url'}).get('href')
    book_id = re.findall(r'(\d{1,13})', book_url)[0]
    review = review.hasBookId(book_id=book_id)
    review = review.build()

    return review


def reviewer_provider(dict_response, json_response):
    CONFIG = config_reader()
    reviewer = ReviewerBuilder.initialize()


    reviewer_id = dict_response['GoodreadsResponse']['user']['id']
    reviewer = reviewer.hasID(reviewer_id)
    reviewer_name = dict_response['GoodreadsResponse']['user']['name']
    reviewer = reviewer.hasName(reviewer_name)

    if 'private' in dict_response['GoodreadsResponse']['user']:
        print("==> Private User")
    else:
        print("==> Public User")
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

        (dict_response, json_response) = get_auth_api_response(CONFIG['FOLLOWING_INFO_ENDPOINT'], 'USERID',
                                                               reviewer_id)
        print(f"=====================> Auth Status : {dict_response['GoodreadsResponse']['Request']['authentication'] }")
            # following = []
            # pages = -1
            # total_number_of_following = dict_response['GoodreadsResponse']['following']['@total']
            #
            # following_ = dict_response['GoodreadsResponse']['following']['user']
            # print(f"total_number_of_following ==> {total_number_of_following}")
            # if total_number_of_following == "1": following.append(following_['id'])
            # elif total_number_of_following == "0": pass
            # else:
            #     for f in following_:
            #         following.append(f['id'])
            # if int(total_number_of_following) > 30:
            #     if int(total_number_of_following) % 30 == 0:
            #         pages = int(total_number_of_following) // 30
            #     else:
            #         pages = int(total_number_of_following) // 30 + 1
            # if pages > 1:
            #     pages_params = [[CONFIG['FOLLOWING_INFO_ENDPOINT'], 'USERID', reviewer_id, i] for i in
            #                     range(2, pages + 1)]
            #     follower_hit_results = perform_parallel_tasks(get_auth_api_response, pages_params)
            #     for result in follower_hit_results:
            #         follower_hit_result = dict_response['GoodreadsResponse']['following']['user']
            #         for f in follower_hit_result:
            #             print(f['id'])
            #             following.append(f['id'])
            # print(f"Total Following pulled : {len(following)}")
            #         # break
        return None
            # following = []
            # page = 0
            # while True:
            #     page += 1

            #
            #
            #
            #     following_end_count = dict_response['GoodreadsResponse']['following']['@end']
            #     print(
            #         f"Pulled {following_end_count} out of {total_number_of_following} following")
            #     break

            # reviewer = reviewer.hasFollowing(following)

            # dict_response, json_response = get_auth_api_response(CONFIG['FOLLOWERS_INFO_ENDPOINT'], 'USERID',
            #                                                      reviewer_id, page)
            #
            # total_number_of_followers = dict_response['GoodreadsResponse']['followers']['@total']
            # followers_ = dict_response['GoodreadsResponse']['followers']['user']
            # followers_end_count = dict_response['GoodreadsResponse']['followers']['@end']

            # followers = []
            # page = 0
            # while True:
            #     page += 1
            #     dict_response, json_response = get_auth_api_response(CONFIG['FOLLOWERS_INFO_ENDPOINT'], 'USERID',
            #                                                          reviewer_id, page)
            #
            #
            #     if total_number_of_followers == "1":
            #         followers.append(followers_['id'])
            #     elif total_number_of_followers == "0":
            #         followers = []
            #     else:
            #         for f in followers_:
            #             followers.append(f['id'])
            #
            #     print(
            #         f"Pulled {followers_end_count} out of {total_number_of_followers} followers")
            #     if followers_end_count == total_number_of_followers:
            #         break

            # reviewer = reviewer.hasFollowers(followers)

    # reviewer = reviewer.build()
    # return reviewer
    # return None


# OK
def write_book_object_to_file(file, book=None, mode="normal"):
    CONFIG = config_reader()
    extension = CONFIG['FILETYPE']

    if extension == "json":
        json_obj = json.dumps(book.__dict__)
        json.dump(json_obj, file)
    elif extension == "csv":
        writer = csv.writer(file, delimiter=',', quotechar='"')
        if mode == "init":
            writer.writerow(
                ["book_name", "id", "authors", "isbn", "isbn13", "publication_date", "best_book_id", "reviews_count",
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
                s = []
                s.append(shelf.get_shelf_id())
                s.append(shelf.get_shelf_name())
                s.append(shelf.get_book_count())
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
