#!flask/bin/python
from flask import Flask, jsonify, request
from flask import abort
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from Rojak import Rojak
rojak = Rojak()

app = Flask(__name__)

@app.route('/todo/api/v1.0/recipes/', methods=['POST'])
@cross_origin()
def get_data():
    if "content" in request.json:
        name = json.loads(request.json)["content"]
    else:
        print("Error! No content found!")
        abort(404)

    task = rojak.search(name) 
    if len(task) == 0:
        abort(404)
    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True)
