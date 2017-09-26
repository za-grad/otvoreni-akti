import os
from dotenv import load_dotenv
from flask import Flask
from flask import jsonify

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

from .search import search

app = Flask(__name__)

@app.route("/search/<query>")
def search_req(query):
    result = search(query)
    return jsonify(result)
