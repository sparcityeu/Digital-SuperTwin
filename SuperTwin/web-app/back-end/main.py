from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.flask_db

@app.route('/', methods=['GET'])
def test():
    return "test test test test"

if __name__ == '__main__':
    app.run(port=5000,debug=True)