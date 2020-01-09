#!flask/bin/python
import logging
import sys

from flask import Flask, jsonify, request
from flask import abort
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from RojakCore import KnowledgeGraph
rojak = KnowledgeGraph()
app = Flask(__name__)

# Logging Start
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
# Logging Ends

@app.route('/todo/api/v1.0/recipes/', methods=['POST'])
@cross_origin()
def get_data():
    if "content" in request.json:
        query = request.json["content"]
    else:
        print("Error! No content found!")
        abort(404)

    task = rojak.search(query)
    if len(task) == 0:
        abort(404)
    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True)
