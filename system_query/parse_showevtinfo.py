import detect_utils
import json
from pprint import pprint

def find_pmu(keys, name_line):

    name = name_line.split(":")[1].split(" ")[1].strip(" ")
    
    for key in keys:
        #print("name:", name, "key:", key, name==key)
        if(name == key):
            #print("MATCH")
            return key
                    
    return None

def get_masks_modifiers(lines):

    ret = {}
    ret['masks'] = {}
    ret['modifiers'] = {}
    
    for line in lines:
        if(line.find("Umask") != -1):
            fields = line.split(":")
            val = fields[3].strip(" ").strip("[").strip("]")
            desc = fields[5][1:]
            ret['masks'][val] = desc
        if(line.find("Modif") != -1):
            fields = line.split(":")
            val = fields[3].strip(" ").strip("[").strip("]")
            desc = fields[4][1:]
            ret['modifiers'][val] = desc

    return ret
            
##Mutate pmus dict for every event 
def parse_event(pmus, event):
    
    pmu_keys = list(pmus.keys())
    lines = event.split('\n')
    #print('lines:', lines)
    
    idx = int(lines[1].split(":")[1])
    pmu = find_pmu(pmu_keys, lines[2])
    name = lines[3].split(":")[1].strip(" ")
    equiv = lines[4].split(":")[1].strip(" ")
    flags = lines[5].split(":")[1].strip(" ")
    desc = lines[6].split(":")[1][1:]
    code = lines[7].split(":")[1].strip(" ")
    
    #print('pmu:', pmu)
    #print('name:', name)
    #print('equiv:', equiv)
    #print('flags:', flags)
    #print('desc:', desc)
    #print('code:', code)

    masks_modifiers = get_masks_modifiers(lines)
    
    pmus[pmu]['events'][idx] = {}
    pmus[pmu]['events'][idx]['name'] = name
    pmus[pmu]['events'][idx]['equiv'] = equiv
    pmus[pmu]['events'][idx]['flags'] = flags
    pmus[pmu]['events'][idx]['desc'] = desc
    pmus[pmu]['events'][idx]['code'] = code
    if(masks_modifiers['masks']): ##Empty dictionaries evaluates to false
        pmus[pmu]['events'][idx]['masks'] = masks_modifiers['masks']
    if(masks_modifiers['modifiers']):
        pmus[pmu]['events'][idx]['modifiers'] = masks_modifiers['modifiers']
    
    return pmus


def parse_evtinfo():

    event_info = detect_utils.cmd('../pmu_event_query/showevtinfo')[1]
    #print(event_info[1])


    detected_start = event_info.find("Detected PMU models")
    detected_end = event_info.find("Total events")

    #print('Detected:', event_info[detected_start:detected_end])

    detected_pmus = event_info[detected_start:detected_end].split('\n')
    detected_pmus = detected_pmus[1:]
    detected_pmus = [x.strip('\t').strip('[').strip(']') for x in detected_pmus]
    #print('detected_pmus:', detected_pmus)

    pmus = {}
    for item in detected_pmus:
        fields = item.split(',')
        #print('fields', fields)
        if(len(fields) == 1):
            continue
        fields[1] = fields[1].strip(' ')
        pmus[fields[1]] = {'name': fields[2].split('"')[1],
                           'no_events': int(fields[3].split(' ')[1]),
                           'max_encoding': int(fields[4].split(' ')[1]),
                           'no_counters': int(fields[5].split(' ')[1]),
                           'type': fields[6][1:],
                           'events': {}}

        
        
    #print('################')
    #for key in pmus:
        #print(key, pmus[key])


    event_start = event_info.find("Total events")
    parse_events = event_info[event_start:]
    #print('parse_events:', parse_events)

    events_list = parse_events.split("#-----------------------------")

    
    for event in events_list[1:]: ##OR remove ''
        #print('event:', event)
        pmus = parse_event(pmus, event)

        
    return pmus
        
if __name__ == "__main__":

    event_info = parse_evtinfo()
    pprint(event_info)

    with open("evtinfo.json", "w") as outfile:
        json.dump(event_info, outfile)
