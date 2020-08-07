from svc.db_svc import initialize_database, execute_query_reviewer, execute_query_reviews, execute_query_book

try:
    import os
    from flask import Flask, make_response, send_from_directory, render_template, request
    from flask_cors import CORS, cross_origin
    from support import provider

except Exception as e:
    print(e)

# Initializing the Flask app
app = Flask(__name__)

# Enabling `Cross Origin Resource Policy` for app
CORS(app=app, support_credentials=True)

"""
Initiatize the Database, make connections, etc; 
Also triggers the query consumer
"""

connection = None
cursor = None

@app.route("/asy/db/v1.0/config/init", methods=["GET"])
@cross_origin(supports_credentials=True)
def init_db():
    global connection, cursor

    print("Looking for database service 🧭")
    print("Service found..")
    print("Triggering Database Initialisation... 🔥")
    connection, cursor = initialize_database()
    if connection != None and cursor != None:
        print("Database initialised ! 🚀")
    else:
        return "Database error !"
    return "Success 200 !!"

"""
Add Insert Queries to the provider Queue using query provider for Book Table
"""


@app.route("/asy/db/v1.0/resources/book/q_query", methods=["POST"])
@cross_origin(supports_credentials=True)
def add_create_insert_query_book():
    query = dict()

    query['book_name'] = request.args.get('book_name')
    query['id'] = request.args.get('id')
    query['authors'] = request.args.get('authors')
    query['isbn'] = request.args.get('isbn')
    query['isbn13'] = request.args.get('isbn13')
    query['publication_date'] = request.args.get('publication_date')
    query['best_book_id'] = request.args.get('best_book_id')
    query['reviews_count'] = request.args.get('reviews_count')
    query['ratings_sum'] = request.args.get('ratings_sum')
    query['ratings_count'] = request.args.get('ratings_count')
    query['text_reviews_count'] = request.args.get('text_reviews_count')
    query['average_ratings'] = request.args.get('average_ratings')

    if execute_query_book(query, connection, cursor)=="200":
        return("Write Successful")
    return "OK"
"""
Add Insert Queries to the provider Queue using query provider for Book Table
"""


@app.route("/asy/db/v1.0/resources/reviews/q_query ", methods=["POST"])
@cross_origin(supports_credentials=True)
def add_create_insert_query_reviews():
    execute_query_reviews(query, connection, cursor)
    pass

"""
Add Insert Queries to the provider Queue using query provider for Book Table
"""


@app.route("/asy/db/v1.0/resources/reviewer/q_query ", methods=["POST"])
@cross_origin(supports_credentials=True)
def add_create_insert_query_reviewer():
    execute_query_reviewer(query, connection, cursor)
    pass

"""
Get current state of Query Queue
"""


@app.route("/asy/db/v1.0/resources/view_q", methods=["GET"])
@cross_origin(supports_credentials=True)
def view_create_insert_query():
    pass


"""
Takes the View Table query and dumps the data into json file
"""


@app.route("/asy/json/v1.0/resources/dump", methods=["GET"])
@cross_origin(supports_credentials=True)
def json_dump():
    pass


"""
Takes the View Table query and dumps the data into csv file
"""


@app.route("/asy/csv/v1.0/resources/dump", methods=["GET"])
@cross_origin(supports_credentials=True)
def csv_dump():
    pass


"""
Closes the database connection
"""


@app.route("/asy/db/v1.0/config/close", methods=["GET"])
@cross_origin(supports_credentials=True)
def close_db():
    pass


# Setting error route
@app.errorhandler(404)
def not_found(error):
    JSON = provider.error_provider()
    return make_response(JSON, 404)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
