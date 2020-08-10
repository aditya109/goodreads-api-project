try:
    import os
    import re
    import time
    import asyncio
    import aiohttp
    import aiofiles
    import requests
    import concurrent

    from typing import IO
    from bs4 import BeautifulSoup
    from aiohttp import ClientSession
    from support.auxillary import config_reader
    from concurrent.futures import ProcessPoolExecutor
    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import Future

except Exception as E:
    print(E)

async def fetch_html(url, session, **kwargs) -> str:
    """
    GET request wrapper to fetch page HTML
    :param url: str
    :param session: ClientSession
    :param kwargs: dict
    :return: str
    """
    response = await session.request(method='GET', url=url, **kwargs)
    response.raise_for_status()
    html = await response.text()
    return html

async def parse_html(url, session, **kwargs):
    global html
    try:
        html = await fetch_html(url=url, session=session, **kwargs)
    except aiohttp.ClientError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        return html

async def write_one(file, url, **kwargs) -> None:
    """Write the found HREFs from `url` to `file`."""
    res = await parse_html(url=url, **kwargs)
    if not res:
        return None
    async with aiofiles.open(file, "a", encoding='utf-8') as f:
        for p in res:
            await f.write(f"{url}\t{p}\n")

async def bulk_crawl_and_write(file, urls, **kwargs) -> None:
    """Crawl & write concurrently to `file` for multiple `urls`."""
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                # write_one(file=file, url=url, session=session, **kwargs)
                parse_html(url=url, session=session)

            )
        await asyncio.gather(*tasks)

def parse(link):
    start_time = time.time()
    r = requests.get(link)

    soup = BeautifulSoup(r.content.decode('utf-8', 'ignore'), 'lxml')
    print(f"Time taken for parse {link} : {time.time() - start_time} seconds")
    return soup

def get_links(table_rows, CONFIG=None):
    for table_row in table_rows:
        a_tag = table_row.find('a', attrs={'class': 'bookTitle'})
        book_id = re.findall(r'(\d{1,11})', a_tag['href'])[0]
        book_endpoint_url = CONFIG['BOOK_INFO_ENDPOINT'].replace("BOOKID", book_id).replace('DEVELOPER_ID', CONFIG['CLIENT_KEY'])
        yield book_endpoint_url





