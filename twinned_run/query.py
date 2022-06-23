import sys
from influxdb import InfluxDBClient
import pymongo
from pymongo import MongoClient









def get_mongodb():

    ##Create a connection for mongodb
    connection_string = "mongodb://localhost:27017"
    client = MongoClient(connection_string)
    
    return client["digital_twin"]

def get_influxdb():

    ##Create a connection for influxdb
    influxdb = InfluxDBClient(host="localhost", port=8086)

    return influxdb
    


def main():

    mongodb = get_mongodb()
    mongodb = mongodb["observations"]
    influxdb = get_influxdb()


    #print("InfluxDBS: ", influxdb.get_list_database())
    
    try0 = mongodb.find({"command": "stress --cpu 8 --io 4 --vm 16 --vm-bytes 128M --timeout 15s"})
    for item in try0:
        print("item", item["_id"], item["influxdb_tag"])








if __name__ == "__main__":

    main()

