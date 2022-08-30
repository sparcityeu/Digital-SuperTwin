import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
import create_dt
import generate_dt
import remote_probe
import initiate
import instantiate

import json
import requests
from os import getenv

import webbrowser

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import pprint

import system_dash_queries

node_id = 0
edge_id = 0

def next_node_id():
    global node_id
    
    node_id += 1
    return str(node_id)

def next_edge_id():
    global edge_id

    edge_id += 1
    return str(node_id)

nodes_hash = {}
edges_hash = {}

nodes_hash_reverse = {}
edges_hash_reverse = {}

nodes = []
edges = []

def get_mongodb(hostname):

    ##Create a connection for mongodb
    connection_string = "mongodb://localhost:27017"
    client = MongoClient(connection_string)
    
    return client[hostname]


def main(hostname, twin_id):

    global nodes_hash
    global edges_hash

    global nodes_hash_reverse
    global edges_hash_reverse

    global nodes
    global edges
    
    mongodb = get_mongodb(hostname)
    collection = mongodb['twin']
    entry = collection.find_one({'_id': ObjectId(twin_id)})
    twin = entry["dtdl_twin"]
    print("Found twin:", type(twin))

    for g_key in twin:

        #create nodes and hash tables
        g_key_id = next_node_id()
        nodes_hash[g_key] = g_key_id
        nodes_hash_reverse[g_key_id] = g_key
        g_dict = twin[g_key]
        node_dict = {"id": g_key_id, "title": g_dict['displayName']}
        nodes.append(node_dict)

    for g_key in twin:

        #create edges
        g_dict = twin[g_key]
        contents = g_dict['contents']

        for content in contents:
            if(content['@type'] == 'Relationship'):
                edge_dict = {"id": next_edge_id(), "source": nodes_hash[g_key], "target": nodes_hash[content['target']]}
                edges.append(edge_dict)


    #print('Nodes:', nodes)
    #print('Edges:', edges)
    
    system_dash_queries.main(nodes, edges)
    

    
if __name__ == "__main__":

    main("dolap", "630d3c823d3509908600a2a2")
