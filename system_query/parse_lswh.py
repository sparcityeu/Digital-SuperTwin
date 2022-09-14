import json
import detect_utils
import pprint

#from collections.abc import MutableMapping
import collections

recurse = 0

def flatten(dictionary, parent_key=False, separator='_'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(flatten({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


def find_field_recursive(top_dict, _class, _description, found):
    #global recurse
    #print("Recursing for ", recurse, "time")
    #recurse += 1

    print("id:", top_dict["id"])

    '''
    if("class" in top_dict and "description" in top_dict):
        print("Here recurse, _class: ", top_dict["class"], "_description: ", top_dict["description"])
    else:
        #pprint.pprint(top_dict)
        print("Peripheral:", top_dict["id"])
    '''

    condition = (top_dict["class"] == _class) and (top_dict["description"] == _description)
    
    if(condition):

        print("Found!")
        pprint.pprint(top_dict)
        found.append(top_dict)
    
    
    elif("children" in top_dict and not condition):
        for i in range(len(top_dict["children"])):
            find_field_recursive(top_dict["children"][i], _class, _description, found)
            
            
        
def find_field(top_dict, _class, _description, found):

    return find_field_recursive(top_dict, _class, _description, found)
        


def parse_lshw():
    
    out = detect_utils.cmd('lshw -json')[1]

    out = json.loads(out)[0]
    #pprint.pprint(out)
    
    system = {}
    system['uuid'] = out['configuration']['uuid']

    found = []
    #find_field(out, "memory", "BIOS", found)
    find_field(out, "processor", "CPU", found)
    print("Found:", found)
    

if __name__ == "__main__":

    parse_lshw()
