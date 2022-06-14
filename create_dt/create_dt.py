import sys
sys.path.append('../system_query')

import probe
import detect_utils

from pprint import pprint

def get_main_interface(_id):
    
    interface = {}

    interface['@id'] = _id
    interface['@type'] = 'Interface'
    interface['contents'] = []
    
    #Optional
    interface['comment'] = ''
    interface['description'] = ''
    interface['displayName'] = ''

    return interface

def get_interface(_id, name):
    
    interface = {}

    interface['@id'] = _id
    interface['@type'] = 'Interface'
    interface['contents'] = []
    
    #Optional
    interface['comment'] = ''
    interface['description'] = name
    interface['displayName'] = name

    return interface
    

def get_relationship(name, _id, target):

    rel = {}
    rel['@type'] = 'Relationship'
    rel['name'] = name

    #Optional
    rel['id'] = _id
    rel['comment'] = ''
    rel['description'] = ''
    rel['displayName'] = ''
    rel['target'] = target
    
    return rel


def get_component(name, _id):

    comp = {}
    comp['@type'] = 'Component'
    comp['name'] = name
    comp['schema'] = 'Array'

    #optional
    comp['comment'] = ''
    comp['description'] = ''
    comp['displayName'] = ''

    return comp

def get_telemetry(name, _id):

    tel = {}
    tel['@type'] = 'Telemetry'
    tel['name'] = name
    tel['schema'] = 'string/dbpointer'
    
    #optional
    tel['comment'] = ''
    tel['description'] = ''
    tel['displayName'] = ''

    return tel
    
def _filter(metric):

    _type = ''
    
    if(metric.find('percpu') != -1):
        _type = 'percpu'
    elif(metric.find('pernode') != -1):
        _type = 'pernode'
    elif(metric.find('kernel') != -1):
        _type = 'kernel'
    elif(metric.find('numa') != -1):
        _type = 'pernode'
    elif(metric.find('mem') != -1):
        _type = 'mem'
    elif(metric.find('network.interface') != -1):
        _type = 'pernetwork'
    elif(metric.find('network') != -1):
        _type = 'network'
    elif(metric.find('disk') != -1):
        _type = 'disk'
    elif(metric.find('hwcounters.UNC') != -1):
        _type = 'uncore'
    elif(metric.find('ENERGY') != -1):
         _type = 'energy'
    elif(metric.find('perfevent.hwcounters') != -1):
        _type = 'perfevent'
         
    return _type
        
if __name__ == "__main__":

    metrics = detect_utils.output_lines('pmprobe')
    metrics = [x.split(" ")[0] for x in metrics]
    
    #print(metrics)
    #exit(1)
    
    dt = get_main_interface('dtmi:dt:DOLAP;1')
    dt['@context'] = 'dtmi:dtdl:context;2'
    
    #dt["contents"].append(get_relationship('CPU', 'dtmi:dt:cpu;1', dt['@id']))
    #dt['contents'].append(get_interface('dtmi:dt:cpu;1', 'CPU'))

    
    
    pprint(dt)
    _sys_dict = probe.main()

    for key in _sys_dict:
        print(key)


    print(_sys_dict['affinity'])
    #exit(1)
    for key in _sys_dict['affinity']['socket']:
        name = 'NUMA'
        _id = 'dtmi:dt:NUMA;' + str(key)
        print('key:', key)
        #exit(1)
        #dt['contents'].append(get_interface(_id, name))
        this_numa = get_interface(_id, name)

        mid = 0
        for metric in metrics:
            mid = mid + 1
            if(_filter(metric) == 'pernode' or _filter(metric) == 'energy' or _filter(metric) == 'uncore'):
                _id = 'dtmi:dt:NUMAmetric;' + str(mid)
                this_numa['contents'].append(get_telemetry(metric, _id))
                
        for core in _sys_dict['affinity']['socket'][key]['cores']:
            #print('!!!', _sys_dict['affinity']['socket'][key][])
            #exit(1)
            name = 'CORE' + str(core)
            _id = 'dtmi:dt:CORE;'+ str(core)
            this_core = get_interface(_id, name)

            tid = 0
            for thread in _sys_dict['affinity']['socket'][key]['cores'][core]:
                name = 'THREAD' + str(thread)
                _id = 'dtmi:dt:THREAD;'+ str(thread)
                this_thread = get_interface(_id, name)

                for metric in metrics:
                    tid = tid + 1
                    if(_filter(metric) == 'percpu'):
                        _id = 'dtmi:dt:THREADmetric;' + str(tid)
                        this_telemetry = get_telemetry(metric, _id)

                        this_thread['contents'].append(this_telemetry)

                this_core['contents'].append(this_thread)

            this_numa['contents'].append(this_core)

        dt['contents'].append(this_numa)



    pprint(dt)
