import asyncio
import random

from psycopg2 import errors

from support.helper import config_reader

try:
    import psycopg2
except Exception as e:
    print(e)

def initialize_database():
    # read connection parameters
    CONFIG = config_reader()

    connection = None

    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database... ⏰')

        connection = psycopg2.connect(**CONFIG['DB-CONFIG'])

        if CONFIG['AUTOCOMMIT'] == "True":
            print("Enabling autocommit in connection ✨")
            connection.autocommit = True

        # create a cursor
        print("Creating a cursor")
        cursor = connection.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cursor.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cursor.fetchone()
        print(db_version)

        return connection, cursor

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None, None



def close_db_connection(connection):
    if connection is not None:
        connection.close()
        print('Database connection closed.')


# async def query_queue_proviDer(queryQueue):
#     while True:
#         await asyncio.sleep(1)
#         print("Adding item to queue")
#         await queryQueue.put(random.randint(1, 10))
#
#
# async def query_queue_consumer(iD, queryQueue):
#     while True:
#         await asyncio.sleep(1)
#         print(f"Consumer : {iD} attempting to get from queue")
#         item = await queryQueue.get()
#         if item is None:
#             break
#         print(f"Consumer : {iD} consumed article with iD: {item}")
#
# async def main(loop):
#     queryQueue = asyncio.Queue(loop=loop, maxsize=10)
#     await asyncio.wait([query_queue_proviDer(queryQueue), query_queue_consumer(1, queryQueue), query_queue_proviDer(2, queryQueue)])

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main(loop))
# print("All Workers completed")
# loop.close()

def execute_query_book(query, connection, cursor):

    book_name = 'The Girl with the Dragon Tattoo'
    iD = '2429135'
    authors = ['Stieg Larsson', 'Reg Keeland']
    isbn = '0307269752'
    isbn13 = '9780307269751'
    publication_date = '16-9-2008'
    best_book_iD =  '2429135'
    reviews_count = '3679643'
    ratings_sum = '10600984'
    ratings_count = '2562866'
    text_reviews_count ='68257'
    average_ratings = '4.14'
    # 
    # book_name = 'The Girl with the Dragon Tattoo'
    # iD = '2429135'
    # authors = ['Stieg Larsson', 'Reg Keeland']
    # isbn = '0307269752'
    # isbn13 = '9780307269751'
    # publication_date = '16-9-2008'
    # best_book_iD =  '2429135'
    # reviews_count = '3679643'
    # ratings_sum = '10600984'
    # ratings_count = '2562866'
    # text_reviews_count ='68257'
    # average_ratings = '4.14'
    sql = """INSERT INTO public."Book"(book_name, iD, authors, isbn, isbn13, publication_date, best_book_iD, reviews_count, ratings_sum, ratings_count, text_reviews_count, average_ratings) VALUES (%s, %s,ARRAY%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    cursor.execute(sql, (book_name, iD, authors, isbn, isbn13, publication_date, best_book_iD, reviews_count, ratings_sum, ratings_count, text_reviews_count, average_ratings))
    connection.commit()
    return "200 !"


def execute_query_reviews(query, connection, cursor):
    sql = """INSERT INTO reviews(vendor_name)
                 VALUES(%s) RETURNING vendor_iD;"""
    cursor.execute(sql, (query))
    connection.commit()

def execute_query_reviewer(query, connection, cursor):
    sql = """INSERT INTO reviewer(vendor_name)
                 VALUES(%s) RETURNING vendor_iD;"""
    cursor.execute(sql, (query))
    connection.commit()

def json_dump_data(query):
    pass

def csv_dump_data(query):
    pass


