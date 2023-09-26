import os, time
from influxdb_client_3 import InfluxDBClient3, Point


def get_token():

    reader = open("cloud_influx.txt")
    token = reader.readlines()[0].split("INFLUXDB_TOKEN=")[1].strip("\n")

    return token


def get_client():

    token = get_token()
    org = "Academic"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = InfluxDBClient3(host=host, token=token, org=org, database="supertwin")

    return client



if __name__ == "__main__":

    client = get_client()
    

