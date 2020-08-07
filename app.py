"""For running this script, please ensure that `sample` directory has `resources` directory container chromedriver
for your OS executable file, clone this repository for better usage.
"""

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
    from support.helper import config_reader, make_html_soup, oauth_validator, clean_up, get_auth_api_response, \
        file_creator
    from associate_runner import book_provider, reviews_provider, write_book_object_to_file, \
        write_review_object_to_file, write_reviewer_object_to_file
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
except Exception as e:
    print(e)

# getting a config from config.ini
CONFIG = config_reader()
# identifying OS of the host
print(f"Accessing OS ... Found : {platform.system()}")

# adding options for headless browsing(headless meaning running in background)
chrome_options = Options()
chrome_options.add_argument("--headless")
# declaring path for webdriver
chrome_driver_path = f"./resources/{platform.system()}/chromedriver"
# initializing Chrome webdriver with options `headless` and executable_path `\path\to\chromedriver`
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path,
                          service_log_path="./chromedriver.log")
# deleting all the existing cookies of the headless browser
driver.delete_all_cookies()

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

def element_grabber(param, by_type="xpath"):
    #  Grabbing elements by either xpath or id using find_element() in driver for our Selenium
    global driver
    element = None
    if by_type == "xpath":
        element = driver.find_element(By.XPATH, param)
    elif by_type == "ID":
        element = driver.find_element(By.ID, param)
    return element


def link_navigator():
    if os.name == "nt":
        _ = os.system('cls')

    global driver
    print("Execution starts here 🔥 ..", end="\n\n")

    # opening the goodreads website using selenium framework
    print(f"Getting URL 🌍: {CONFIG['ROOT_URL']}", end="\n\n")
    driver.get(CONFIG['ROOT_URL'])
    # logging into goodreads API as a developer
    try:

        # grabbing the email field
        email_input_box = element_grabber(
            "/html/body/div[2]/div[1]/div/div/div[1]/div/div/form/div[1]/input[1]")
        # sending the email as input to the above field
        email_input_box.send_keys(CONFIG['EMAIL_ID'])

        # grabbing the password field
        password_textbox = element_grabber(
            "/html/body/div[2]/div[1]/div/div/div[1]/div/div/form/div[2]/div/input")
        # sending the password as input to the above field
        password_textbox.send_keys(CONFIG['PASSWORD'])

        # grabbing sign in button
        sign_btn = element_grabber(
            "/html/body/div[2]/div[1]/div/div/div[1]/div/div/form/div[3]/input[1]")
        # submitting the login form
        sign_btn.click()

        for child_url in CONFIG['CHILD_URLS']:
            page = 0
            while True:
                page += 1
                # appending pages to the url
                child_url = child_url + f"?page={page}"
                print(f"Getting Child URL 🌍: {child_url}", end="\n\n")
                driver.get(child_url)
                # grabbing the page source of the webpage
                html = driver.page_source
                # now we make a Beautiful Soup out of the html
                soup = make_html_soup(html)

                # Find number of books provided by the link
                t = soup.find('div', attrs={'class': 'stacked'})
                total_number_of_books = t.find('div').get_text().strip().split(" books")[0]

                print(f"# books found = {total_number_of_books}", end="\n\n")

                # find all the books in one page
                table_rows = soup.find_all('tr')
                if len(table_rows) == 0:
                    break
                for table_row in table_rows:

                    a_tag = table_row.find('a', attrs={'class': 'bookTitle'})
                    ID = re.findall(r'(\d{1,11})', a_tag['href'])[0]
                    print(f"Redirecting URL : {CONFIG['ROOT_URL'][:len(CONFIG['ROOT_URL']) - 1] + a_tag['href']}")
                    span = a_tag.find('span')

                    title = span.get_text().split('(')[0].strip()

                    a_tag = table_row.find('a', attrs={'class': 'authorName'})
                    span = a_tag.find('span', attrs={'itemprop': 'name'})
                    author = span.get_text()

                    print(f"Accessing {title} by {author} with ID:{ID} ...")

                    # pulling book info from bookreads api
                    book, reviews_url = book_provider(ID, book_file)

                    # explicitly imbibing ISBN into links using regular expressions
                    if reviews_url.find("isbn") == -1:
                        reviews_url += f"&isbn={book.get_isbn()}"
                    # replacing the word DEVELOPER_ID with key
                    reviews_url = reviews_url.replace("DEVELOPER_ID", CONFIG['CLIENT_KEY'])

                    reviews_provider(reviews_url, driver, book.get_id(), review_file, reviewer_file)

                    # break
                # break
            # break



    except Exception as exception:
        traceback.print_exc()
    finally:
        # finally quiting the the driver
        driver.quit()


# START HERE
if __name__ == "__main__":
    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')
    # Registering the app.py with OAuth
    oauth_validator()
    link_navigator()
    # cleaning up project, closing files, etc
    clean_up([book_file, review_file, reviewer_file])
    input("\n\n\nPress enter to exit 🚀...")

    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')
