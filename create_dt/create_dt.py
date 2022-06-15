import sys
sys.path.append("../system_query")

import probe
import detect_utils

from pprint import pprint
import json

context = "dtmi:dtdl:context;2"

def get_interface(_id, displayname = "", description = ""):

    interface = {}

    interface["@type"] = "Interface"
    interface["@id"] = _id
    interface["@context"] = context
    
    interface["contents"] = []

    if(displayname != ""):
        interface["displayname"] = displayname
    if(description != ""):
        interface["description"] = description



def get_relationship(_id, name, target, displayname = "", description = ""):
    
    relationship = {}

    relationship["@type"] = "Relationship"
    relationship["@id"] = _id
    relationship["name"] = name


    if(displayname != ""):
        relationship["displayname"] = displayname
    if(description != ""):
        relationship["description"] = description
    
    


def main():

    



if __name__ == "__main__":

    main()



