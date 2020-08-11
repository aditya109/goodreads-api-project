from itertools import chain
from typing import List

try:
    import os
    import re
    import time
    import json
    import pprint
    import urllib
    import requests
    import xmltodict
    import platform
    import traceback
    import concurrent
    from concurrent.futures.thread import ThreadPoolExecutor
    from bs4 import BeautifulSoup
    from collections import defaultdict
    from support.auxillary import config_reader, make_html_soup, oauth_validator, clean_up, get_auth_api_response, \
        file_creator, get_api_response, get_page_content_response
    from associate_runner import book_provider, reviews_provider, write_book_object_to_file, \
        write_review_object_to_file, write_reviewer_object_to_file

except Exception as e:
    print(e)

# getting aconfig from config.ini
CONFIG = config_reader()
# identifying OS of the host
print(f"Accessing OS ... Found : {platform.system()}")

# getting the defined extension
extension = CONFIG['FILETYPE']
# providing names to the files
filenames = ['book', 'review', 'reviewer']
# adding extensions to the file names
for idx, filename in enumerate(filenames):
    filenames[idx] = filenames[idx] + '.csv'
# getting file pointer for the file
book_file, review_file, reviewer_file = file_creator(filenames)

# initializing files for csvs
write_book_object_to_file(book_file, None, mode="init")
write_review_object_to_file(review_file, None, mode="init")
write_reviewer_object_to_file(reviewer_file, None, mode="init")

def links_flattener(matrix):
    flattened_links = [list__.result() for list__
                       in matrix]
    flattened_links = list(chain.from_iterable(flattened_links))
    return flattened_links


def perform_reviews_links_task(cumulative_reviews_url_for_one_book) -> List:
    # storing all review specific urls from one book
    review_specific_links_for_one_book = perform_parallel_tasks(get_href_links_from_reviews,
                                                                cumulative_reviews_url_for_one_book)

    flattened_links = links_flattener(review_specific_links_for_one_book)
    return flattened_links


def perform_parallel_tasks(function, items)-> List:
    results = []
    # using multithreading concept to fasten the web pull
    with ThreadPoolExecutor(50) as executor:
        # executing GET request of link asynchronously
        futures = [executor.submit(function, item) for item in items]
        # pulling the results from the concurrent execution array `futures`
        for result in concurrent.futures.as_completed(futures):
            # this gives me a list of future object
            results.append(result)

    return results


def get_links(table_rows)->List:
    for table_row in table_rows:
        a_tag = table_row.find('a', attrs={'class': 'bookTitle'})
        book_id = re.findall(r'(\d{1,11})', a_tag['href'])[0]
        book_endpoint_url = CONFIG['BOOK_INFO_ENDPOINT'].replace("BOOKID", book_id).replace('DEVELOPER_ID',
                                                                                            CONFIG['CLIENT_KEY'])
        yield book_endpoint_url


def get_href_links_from_reviews(link)->List:
    html = get_page_content_response(link)
    a_tags_in_a_page = html.find_all('a', attrs={'class': 'gr_more_link'})
    href_links = [a_tag.get('href') for a_tag in a_tags_in_a_page]
    return href_links


def link_navigator():
    if os.name == "nt" and os.name == "mac":
        _ = os.system('clear')

    print("Execution starts here 🔥 ..", end="\n\n")
    try:
        for child_url in CONFIG['CHILD_URLS']:
            page = 0
            while True:
                page += 1
                # appending pages to the url
                usage_url = child_url + f"?page={page}"
                print(f"Getting page of {page} : Child URL 🌍: {usage_url}", end="\n\n")
                # going to the first page of the child_url
                response = requests.get(usage_url)
                print(f"Server RTT : {response.elapsed.total_seconds()} secs")
                # grabbing the html content of the requests
                html = response.content
                # now we make a Beautiful Soup out of the html
                soup = make_html_soup(html)

                # find all the books in one page
                table_rows = soup.find_all('tr')
                # edge condition to check to break the loop on finding the first invalid page
                if len(table_rows) == 0:
                    print(f"No books found ! Ending Scape on URL {child_url} !")
                    break

                print(f"Total Number of Books in this page : {len(table_rows)}")

                # start_time = time.time()
                # print(f"Time taken for parse <all> : {time.time() - start_time} seconds")

                # ====================#################==============================
                # pulling book info from bookreads api

                book_api_hit_results = perform_parallel_tasks(get_api_response, get_links(table_rows))

                # `cumulative_reviews_urls_for_all_books` holds the review urls for all books in one page
                cumulative_reviews_urls_for_all_books = list()
                # list of all `book` objects returned
                books_list = list()
                # iterating through all the book API hit results
                for book_api_hit_result in book_api_hit_results:
                    # here from each future object, ew extract result using result() => this return a tuple
                    dict_response = book_api_hit_result.result()[0]
                    json_response = book_api_hit_result.result()[1]
                    # sending `dict_response` and `json_response` to book_provider()
                    book, review_url = book_provider(dict_response, json_response)
                    # checking for books with None as their value, since we are rejecting books with no ISBNs
                    if book is not None:
                        # appending all the book objects to the `books_list`
                        books_list.append(book)
                        # some books who dirctly don't have XML field `ISBN` don't have `isbn` in their review url, thereby invalidating it, hence we find explicitly find the ISBN value and append it to the review url
                        if "isbn" not in review_url:
                            review_url = review_url + f"&isbn={book.get_isbn()}"
                        # replacing `DEVELOPER_ID` with `CLIENT KEY`
                        cumulative_reviews_urls_for_all_books.append(
                            review_url.replace("DEVELOPER_ID", CONFIG['CLIENT_KEY']))
                        # writing the book object to the output file
                        write_book_object_to_file(book_file, book, "normal")

                print(f"Successfully pulled {len(books_list)} out of {len(table_rows)} books' info..")

                # ====================#################==============================
                # pulling reviews info from bookreads api
                # making 2D matrix of reviews URLs
                # each rows contains 10 pages of same review url
                cumulative_reviews_urls_for_all_books = [
                    [cumulative_reviews_url_for_one_book + f"&page={page}" for page in range(1, 11)] for
                    cumulative_reviews_url_for_one_book in cumulative_reviews_urls_for_all_books]

                 # iterating through all reviews urls for all books

                specific_review_links_results = perform_parallel_tasks(perform_reviews_links_task, cumulative_reviews_urls_for_all_books)

                for specific_review_links_result in specific_review_links_results:
                    for link in specific_review_links_result.result():
                        print(link)
                    break

                break
            break
    except Exception as E:
        traceback.print_exc()
        print(E)
    finally:
        pass


# START HERE
if __name__ == "__main__":
    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')
    # Registering the app.py with OAuth
    # oauth_validator()
    link_navigator()
    # cleaning up project, closing files, etc
    clean_up([book_file, review_file, reviewer_file])
    input("\n\n\nPress enter to exit 🚀...")

    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')
