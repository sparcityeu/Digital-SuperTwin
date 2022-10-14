import sys
sys.path.append("../")

import utils

from flask import Flask, request, jsonify, json, abort
from flask_cors import CORS, cross_origin

import pprint

import pymongo
from pymongo import MongoClient

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

methods = ('GET', 'POST')


dummy_time = 1450754160000 ##Dummy time works, but for a better solution, "time_from" and "time_to" from incoming query could be used


data = {}


@app.route('/', methods=methods)
@cross_origin()
def hello_world():
    return 'OK'

@app.route('/search', methods=methods)
@cross_origin()
def find_metrics():
    #print('/search:', request.headers, request.get_json())
    return jsonify(list(data))
    


@app.route('/query', methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    print(request.headers, request.get_json())
    req = request.get_json()
    print("############")
    print("Request Targets:", req["targets"])
    print("############")
    pprint.pprint(req["targets"][0]["target"])

    target = req["targets"][0]["target"]
    print("TARGET:", target, "DATA:", data[target])
    answer = [{"target": target, "datapoints": [[data[target], dummy_time]]}]
    
    
    return jsonify(answer)


def main(SuperTwin):
    
    global data
    
    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]
    twin = meta_with_twin["twin_description"]

    data = utils.fill_data(twin, SuperTwin.name, SuperTwin.addr)
    app.run(host='0.0.0.0', port=5052, debug=True)


if __name__ == '__main__':

    main("dolap", "10.36.54.195")
