import sys

# https://flask.palletsprojects.com/en/2.0.x/
from flask import Flask, json, render_template, jsonify

# https://docs.python.org/3/library/urllib.parse.html
from urllib.parse import quote

# https://pymongo.readthedocs.io/en/stable/index.html
from pymongo import MongoClient, collection, server_description
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
	), 403,  {'ContentType':'application/json'}


@app.errorhandler(404)
def page_not_found(error):
	return jsonify(
		status=404
	), 404,   {'ContentType':'application/json'}


@app.errorhandler(405)
def invalide_request_method(error):
	return jsonify(
		status=405
	), 405,  {'ContentType':'application/json'}


# Create a URL route in our application for "/"
@app.route('/')
def home():
	"""
	This function just responds to the browser URL
	localhost:5000/

	:return:        the rendered template 'home.html'
	"""

	return render_template('home.html')


# TODO: Test with non GET request method
@app.route('/urlinfo/1/<path:url>', methods=['GET'])
def approval_lookup(url):
	"""
	This function just responds to the browser ULR
	localhost:5000/

	:return:        json with boolean response'
	"""

	is_approved = False
	is_approved = is_approved_url(url)

	log.info(f"url: {url}, approved: {is_approved}")

	return jsonify(
		approved=is_approved,
		status=200
	), 200, {'ContentType':'application/json'}


def is_approved_url(url):
	"""
	This function checks to see if a URL in in a black
	list database.

	:return:        boolean'
	"""
	black_list_results = {"url": url, "approved": False, "found": False}

	url_obj = lookup_url(url)
	if url_obj:
		log.debug(f"lookup url obj: {url_obj}")
		black_list_results['found'] = True
		black_list_results['approved'] = url_obj.get('approved')

	return black_list_results.get('approved')


def mongodb_connect():
	"""
	This function connections to a mongodatabase on localhost using port 27017

	:return:        connection object
	"""

	try:
		conn = MongoClient(host="mongo", port=27017, username='root', password='rootpassword')
		return conn
	except ConnectionFailure:
		log.error("Cannot connect to database")
	except ServerSelectionTimeoutError:
		log.error("Connection to database timedout")
	except:
		log.error("Unknown connection error")



def lookup_url(url):
	"""
	This function looks up the supplied URL from a mongo collection

	:return:        returns a json document
	"""

	conn =  mongodb_connect()
	if conn is None:
		log.error("No database connection")
		return False

	# URL are stored encoded in the DB. String must be encoded as well.
	encoded_url = str(quote(url, safe=""))
	log.debug(f"encoded url: {encoded_url}")

	try:
		# Use pwolstenholme DB
		db = conn.pwolstenholme
		log.debug(f"database: {db}")
		# Use the urlinfo collection
		collection = db.urlinfo
		log.debug(f"collection: {collection}")

		for doc in collection.find({"url": encoded_url}):
			log.debug(f"found url in collection {doc}")
			# TODO: manage more than one result
			return doc
	except AttributeError:
		log.warning(f"url not found in black list {url}")
		return False
	finally:
		conn.close()


#  If we're running in stand alone mode, run the application
if __name__ == '__main__':
	# app.run(debug=True, ssl_context='adhoc')
	app.debug=True
	from waitress import serve
	serve(app, host="127.0.0.1", port=5000)