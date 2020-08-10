import requests

from support.asynch import get_links

try:
    import json
    import re
    import pprint
    import xmltodict
    import urllib
    import os
    import platform
    import traceback
    import time
    from backports import configparser
    from bs4 import BeautifulSoup
    from collections import defaultdict
    from support.auxillary import config_reader, make_html_soup, oauth_validator, clean_up, get_auth_api_response, \
        file_creator
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

def link_navigator():
    global books_urls
    books_urls = list()
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

                # for link in get_links(table_rows=table_rows, CONFIG=CONFIG):
                #     print(link)


                    # pulling book info from bookreads api
                #     book, reviews_url = book_provider(ID, book_file)
                #
                #     # explicitly imbibing ISBN into links using regular expressions
                #     if reviews_url.find("isbn") == -1:
                #         reviews_url += f"&isbn={book.get_isbn()}"
                #     # replacing the word DEVELOPER_ID with key
                #     reviews_url = reviews_url.replace("DEVELOPER_ID", CONFIG['CLIENT_KEY'])
                #
                #     reviews_provider(reviews_url, driver, book.get_id(), review_file, reviewer_file)
                # break
                usage_url = child_url

            break
    except Exception as exception:
        traceback.print_exc()
    finally:
        # finally quiting the the driver
        # driver.quit()
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

