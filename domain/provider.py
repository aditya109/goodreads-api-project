try:
    import json
    import csv
    import re
    from bs4 import BeautifulSoup
    from domain.book import BookBuilder
    from domain.review import ReviewBuilder
    from domain.reviewer import ShelfBuilder, ReviewerBuilder
    import requests
    from support.auxillary import *
except Exception as e:
    print(e)


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

        # building the `book` object
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
    # adding review_id
    review = review.hasReviewID(review_id)

    # grabbing the reviewer ID
    reviewer_page = soup.find('h1').find('a').get('href')
    reviewer_id = re.findall(r'(\d{1,13})', reviewer_page)[0]
    review = review.byReviewerID(reviewer_id)

    # grabbing ratings
    rating = soup.find(
        'meta', attrs={'itemprop': 'ratingValue'}).get('content')
    review = review.hasRating(rating)

    # grabbing review text
    review_text = soup.find(
        'div', attrs={'itemprop': 'reviewBody'}).get_text().strip()
    review = review.hasText(review_text)

    # grabbing likes
    likes = soup.find('span', attrs={'class': 'likesCount'})
    if likes is not None:
        likes = likes.get_text().split(' likes')[0].strip()
        review = review.hasLikes(likes)

    # grabbing book ID
    book_url = soup.find(
        'a', attrs={'class': 'bookTitle', 'itemprop': 'url'}).get('href')
    book_id = re.findall(r'(\d{1,13})', book_url)[0]
    review = review.hasBookId(book_id=book_id)
    # building `review` object
    review = review.build()

    return review


def reviewer_provider(dict_response, CONFIG):
    # initialising a ReviewerBuilder object
    reviewer = ReviewerBuilder.initialize()

    # grabbing reviewer ID
    reviewer_id = dict_response['GoodreadsResponse']['user']['id']
    reviewer = reviewer.hasID(reviewer_id)

    # grabbing reviewer ID
    reviewer_name = dict_response['GoodreadsResponse']['user']['name']
    reviewer = reviewer.hasName(reviewer_name)

    # rejecting reviewer if reviewer is private
    if 'private' in dict_response['GoodreadsResponse']['user']:
        print("==> Private User")
    else:
        # extracting info for a public user
        print("==> Public User")

        # grabbing info on reviewer's shelves (shelfID, shelfName, shelfBookCount)
        shelves = []
        temp_shelves = dict_response['GoodreadsResponse']['user']['user_shelves']['user_shelf']

        for temp_shelf in temp_shelves:
            # initializing a ShelfBuilder object
            shelf = ShelfBuilder.initialize()

            # grabbing shelf ID
            shelf_id = temp_shelf['id']['#text']
            shelf = shelf.hasShelfID(shelf_id)

            # grabbing shelf Name
            shelf_name = temp_shelf['name']
            shelf = shelf.hasShelfName(shelf_name)

            # grabbing shelf book count
            book_count = temp_shelf['book_count']['#text']
            shelf = shelf.hasBookCount(book_count)

            # building Shelf object
            shelf = shelf.build()

            # appending above built object to shelves list
            shelves.append(shelf)

        # putting shelves as a list
        reviewer = reviewer.hasShelves(shelves)

        # grabbing total number of reviews
        number_of_reviews = dict_response['GoodreadsResponse']['user']['reviews_count']['#text']
        reviewer = reviewer.hasTotalReviews(number_of_reviews)

        # grabbing friends' count
        friends_count = dict_response['GoodreadsResponse']['user']['friends_count']['#text']
        reviewer = reviewer.hasFriendsCount(friends_count)

        # grabbing list of users(reviewer) followed by reviewer of interest
        (dict_response, json_response) = get_auth_api_response(CONFIG['FOLLOWING_INFO_ENDPOINT'], 'USERID',
                                                               reviewer_id)
        # checking for reviewers with non-authenticated list of following or zero following
        if dict_response['GoodreadsResponse']['following']['@total'] == '0':
            pass
        else:
            # following[] is used to store
            following = []
            # pages is used count the total no. of simulatanoues page pulls
            pages = 1
            # extracting total number of following
            total_number_of_following = dict_response['GoodreadsResponse']['following']['@total']

            # extracting all following in one page
            following_ = dict_response['GoodreadsResponse']['following']['user']

            if total_number_of_following == "1":
                # checking if total number of following is 1
                following.append(following_['id'])
            elif total_number_of_following == "0":
                # skipping if total number of following is 0
                pass
            else:
                # extracting all following ID and appending to following[]
                for f in following_:
                    following.append(f['id'])
            # calculating pages for simultaneous page pulls
            # EACH API HIT ONLY CONTAINS 30 RESULTS
            if int(total_number_of_following) > 30:
                if int(total_number_of_following) % 30 == 0:
                    pages = int(total_number_of_following) // 30
                else:
                    pages = int(total_number_of_following) // 30 + 1
            if pages > 1:
                # forming list of param list for each reviewer
                pages_params = [[CONFIG['FOLLOWING_INFO_ENDPOINT'], 'USERID', reviewer_id, i] for i in
                                range(2, pages + 1)]
                # performing parallel tasks for auth api requests
                following_hit_results = perform_parallel_tasks(
                    get_auth_api_response, pages_params)
                # extracting results off following_hit_results[]
                for result in following_hit_results:
                    # tuple unpacking for result
                    (dict_response, json_response) = result.result()
                    # grabbing list of all following
                    following_hit_result = dict_response['GoodreadsResponse']['following']['user']
                    # appending user ID to following[]
                    if isinstance(following_hit_result, list):
                        for f in following_hit_result:
                            following.append(f['id'])
                    else:
                        following.append(following_hit_result['id'])
            print(
                f"Total Following pulled : {len(following)}/{total_number_of_following}")
            # putting following[] to reviewer
            reviewer = reviewer.hasFollowing(following)

        # grabbing list of users(reviewer) following reviewer of interest
        (dict_response, json_response) = get_auth_api_response(CONFIG['FOLLOWERS_INFO_ENDPOINT'], 'USERID',
                                                               reviewer_id)
        # checking for reviewers with non-authenticated list of followers or zero followers
        if dict_response['GoodreadsResponse']['followers']['@total'] == '0':
            pass
        else:
            # followers[] is used to store
            followers = []
            # pages is used count the total no. of simulatanoues page pulls
            pages = 1
            # extracting total number of followers
            total_number_of_followers = dict_response['GoodreadsResponse']['followers']['@total']

            # extracting all followers in one page
            followers_ = dict_response['GoodreadsResponse']['followers']['user']

            if total_number_of_followers == "1":
                # checking if total number of followers is 1
                followers.append(followers_['id'])
            elif total_number_of_followers == "0":
                # skipping if total number of followers is 0
                pass
            else:
                # extracting all followers ID and appending to followers[]
                for f in followers_:
                    followers.append(f['id'])
            # calculating pages for simultaneous page pulls
            # EACH API HIT ONLY CONTAINS 30 RESULTS
            if int(total_number_of_followers) > 30:
                if int(total_number_of_followers) % 30 == 0:
                    pages = int(total_number_of_followers) // 30
                else:
                    pages = int(total_number_of_followers) // 30 + 1
            if pages > 1:
                # forming list of param list for each reviewer
                pages_params = [[CONFIG['FOLLOWERS_INFO_ENDPOINT'], 'USERID', reviewer_id, i] for i in
                                range(2, pages + 1)]
                # performing parallel tasks for auth api requests
                follower_hit_results = perform_parallel_tasks(
                    get_auth_api_response, pages_params)
                # extracting results off followers_hit_results[]
                for result in follower_hit_results:
                    # tuple unpacking for result
                    (dict_response, json_response) = result.result()
                    # grabbing list of all followers
                    follower_hit_result = dict_response['GoodreadsResponse']['followers']['user']
                    # appending user ID to followers[]
                    if isinstance(follower_hit_result, list):
                        for f in follower_hit_result:
                            followers.append(f['id'])
                    else:
                        followers.append(follower_hit_result['id'])
            print(
                f"Total Followers pulled : {len(followers)}/{total_number_of_followers}")
            # putting followers[] to reviewer
            reviewer = reviewer.hasFollowers(followers)
    reviewer = reviewer.build()
    return reviewer
