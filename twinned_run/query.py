import sys
from influxdb import InfluxDBClient
import pymongo
from pymongo import MongoClient


def get_mongodb():

    ##Create a connection for mongodb
    connection_string = "mongodb://host.docker.internal:27017"
    client = MongoClient(connection_string)
    
    return client["digital_twin"]

def get_influxdb():

    ##Create a connection for influxdb
    influxdb = InfluxDBClient(host="host.docker.internal", port=8086)

    return influxdb
    


def main():

    mongodb = get_mongodb()
    mongodb = mongodb["observations"]
    influxdb = get_influxdb()


    #print("InfluxDBS: ", influxdb.get_list_database())
    
    #try0 = mongodb.find({"command": "stress --cpu 8 --io 4 --vm 16 --vm-bytes 128M --timeout 15s"})

    
    try0 = mongodb.find({"command": "stress --cpu 12 --io 4 --vm 16 --vm-bytes 512M --timeout 60s"})
    try1 = mongodb.find({"command": "stress --cpu 4 --io 4 --vm 16 --vm-bytes 512M --timeout 60s"})

    for item in try0:
        print("item0", item["_id"], item["influxdb_tag"])

    for item in try1:
        print("item1", item["_id"], item["influxdb_tag"])








if __name__ == "__main__":

    main()

