# https://flask.palletsprojects.com/en/2.0.x/
from flask import Flask, render_template, jsonify

# https://docs.python.org/3/library/urllib.parse.html
from urllib.parse import quote

# https://pymongo.readthedocs.io/en/stable/index.html
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# https://docs.python.org/3/library/logging.html
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__.split('.')[0])


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify(
        status=500
    )


@app.errorhandler(403)
def forbidden(error):
    return jsonify(
        status=403
    ), 403,  {'ContentType': 'application/json'}


@app.errorhandler(404)
def page_not_found(error):
    return jsonify(
        status=404
    ), 404,   {'ContentType': 'application/json'}


@app.errorhandler(405)
def invalide_request_method(error):
    return jsonify(
        status=405
    ), 405,  {'ContentType': 'application/json'}


# Create a URL route in our application for "/"
@app.route('/', methods=['GET', 'HEAD'])
def home():
    """
    This function just responds to the browser URL
    localhost:5000/. Support GET and HEAD methods.

    Returns:
         html: the rendered template 'home.html'
    """

    return render_template('home.html')


@app.route('/urlinfo/1/<path:url>', methods=['GET'])
def approval_lookup(url):
    """
    This function just responds to the browser ULR
    localhost:5000/urlinfo/1/<path:url>. Supports
    Get method

    Args:
        url (str): the url string to be check against
        black list database

    Returns:
         json:  approved and status keys
    """

    is_approved = False
    is_approved = is_approved_url(url)

    log.info(f"url: {url}, approved: {is_approved}")

    return jsonify(
        approved=is_approved,
        status=200
    ), 200, {'ContentType': 'application/json'}


@app.route('/add_test_data', methods=['GET'])
def add_data():
    """
    This route will call a function
     adding some test data to mongodb

    Returns
        json: success and satus keys
    """

    added = False
    added = add_mongo_test_data()

    log.info(f"data added: {added}")

    return jsonify(
        success=added,
        status=200
    ), 200, {'ContentType': 'application/json'}


def is_approved_url(url):
    """
    Checks to see if a URL in in a black
    list database.

    Args:
        url (str): a partial non-encoded url top be checked

    Returns:
         boolean: True if url is approved
    """
    black_list_results = {'url': url, 'approved': False, "found": False}

    url_obj = lookup_url(url)
    if url_obj:
        log.debug(f"lookup url obj: {url_obj}")
        black_list_results['found'] = True
        black_list_results['approved'] = url_obj.get('approved')

    return black_list_results.get('approved')


def mongodb_connect():
    """
    Establishes connection to mongodb on mongo container using port 27017

    Returns:
        class: database connection handler

    """

    try:
        conn = (MongoClient(host="mongo", port=27017, username='root',
                            password='rootpassword'))
        return conn

    except ConnectionFailure:
        log.error("Cannot connect to database")
    except ServerSelectionTimeoutError:
        log.error("Connection to database timedout")
    except Exception as e:
        log.error(f"Connection to database timedout: {e}")


def lookup_url(url):
    """
    This function encodes the supplied url and
     looks searches for it in from a mongo collection

    Args:
        url (string): a partial url.

    Returns:
         json: json document if found in database.
    """

    conn = mongodb_connect()
    if conn is None:
        log.error("No database connection")
        return False

    # URL are stored encoded in the DB.
    # String must be encoded for search.
    encoded_url = str(quote(url, safe=""))
    log.debug(f"encoded url: {encoded_url}")

    try:
        # Use pwolstenholme DB
        db = conn.pwolstenholme
        log.debug(f"database: {db}")
        # Use the urlinfo collection
        collection = db.urlinfo
        log.debug(f"collection: {collection}")

        # Search for url in database
        for doc in collection.find({'url': encoded_url}):
            log.debug(f"found url in collection {doc}")
            return doc
    except AttributeError:
        log.warning(f"url not found in black list {url}")
        return False
    finally:
        conn.close()


def add_mongo_test_data():
    """
    This function adds test data to a mongo collection

    Return:        returns a boolean
    """

    # Small set of test data
    url_info = [
        {'url': 'www.sfu.ca%2Fabout%2Feconomic-recovery%2F1-10.html', 'approved': True},   # noqa: E501
        {'url': 'ubc.ca%2Facademics%2F', 'approved': True},
        {'url': 'umbrella.cisco.com%2F%3Fdtid%3Dosscdc000283', 'approved': True},  # noqa: E501
        {'url': 'www.geeksforgeeks.org%3A443%2Fpython-build-a-rest-api-using-flask%2F', 'approved': True},  # noqa: E501
        {'url': 'www.central1.com:443/cgi-bin/badstuff.pl', 'approved': True}
    ]  # noqa: E501

    conn = mongodb_connect()
    if conn is None:
        log.error("No database connection")
        return False

    try:
        # Use pwolstenholme DB
        db = conn.pwolstenholme
        collection = db.urlinfo
        # # Start with a clean collection
        collection.drop()
        # if not db.collection.drop():
        # 	log.debug(f"collection not dropped")

        # # Drop existing indexes
        # if not collection.drop_indexes():
        # 	log.debug(f"indexes not dropped")

        # # if not collection.create_index('url'):
        # # 	log.debug(f"indexes not added")

        # # TODO: investigate failing unique flage for indexes
        # # Create on unique index on the url key. Unique key is failing
        # # collection.create_index('url', unique=True)

        # Insert of few documents for testing
        result = collection.insert_many(url_info)
        log.debug(f"number of records added: {len(result.inserted_ids)}")

        return True
    except Exception as e:
        log.warning(f"could not add records to mongo: {e}")
        return False
    finally:
        conn.close()


#  If we're running in stand alone mode, run the application
if __name__ == '__main__':
    # app.run(debug=True, ssl_context='adhoc')
    app.debug = True
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
