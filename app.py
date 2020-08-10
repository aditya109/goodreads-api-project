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
        file_creator, get_api_response
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

def api_pull_using_thread_pool_executor(links):
    results = []
    # using multithreading concept to fasten the web pull
    with ThreadPoolExecutor(50) as executor:
        # executing GET request of link asynchronously
        futures = [executor.submit(get_api_response, link) for link in links]
        # pulling the results from the concurrent execution array `futures`
        for result in concurrent.futures.as_completed(futures):
            results.append(result)
    return results


def get_links(table_rows):
    for table_row in table_rows:
        a_tag = table_row.find('a', attrs={'class': 'bookTitle'})
        book_id = re.findall(r'(\d{1,11})', a_tag['href'])[0]
        book_endpoint_url = CONFIG['BOOK_INFO_ENDPOINT'].replace("BOOKID", book_id).replace('DEVELOPER_ID',
                                                                                            CONFIG['CLIENT_KEY'])
        yield book_endpoint_url


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

                # pulling book info from bookreads api
                book_provider_results = api_pull_using_thread_pool_executor(links=get_links(table_rows))

                review_urls = list()
                books_list = list()
                for book_provider_result in book_provider_results:
                    dict_response = book_provider_result.result()[0]
                    json_response = book_provider_result.result()[1]
                    book, review_url = book_provider(dict_response, json_response)
                    if book is not None:
                        books_list.append(book)
                        review_urls.append(review_url)
                        write_book_object_to_file(book_file, book, "normal")

                # pulling reviews info from bookreads api
                reviews_provider_results = api_pull_using_thread_pool_executor(links=review_urls)
                



                #     reviews_provider(reviews_url, driver, book.get_id(), review_file, reviewer_file)
                # break
                break
            break
    except Exception as E:
        traceback.print_exc()
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
