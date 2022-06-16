import sys
sys.path.append("../system_query")

import probe
import detect_utils

from pprint import pprint
import json

context = "dtmi:dtdl:context;2"

globvar = -1

metrics = detect_utils.output_lines('pmprobe')                                                  
metrics = [x.split(" ")[0] for x in metrics]

def g():

    global globvar
    globvar = globvar + 1

    return str(globvar)


def get_interface(_id, displayname = "", description = ""):

    interface = {}

    interface["@type"] = "Interface"
    interface["@id"] = _id
    interface["@context"] = context
    
    interface["contents"] = []

    if(displayname != ""):
        interface["displayName"] = displayname
    if(description != ""):
        interface["description"] = description


    return interface


def get_relationship(_id, name, target, displayname = "", description = ""):
    
    relationship = {}

    relationship["@type"] = "Relationship"
    relationship["@id"] = _id
    relationship["name"] = name
    relationship["target"] = target

    if(displayname != ""):
        relationship["displayName"] = displayname
    if(description != ""):
        relationship["description"] = description

    return relationship


def get_property(_id, name, schema = "string", displayname = "", description = ""):

    _property = {}

    _property["@id"] = _id
    _property["@type"] = "Property"
    _property["name"] = name #Note that this name is different than displayName
    _property["schema"] = schema #In dtdl v2, properties require name field and schema

    
    if(displayname != ""):
        _property["displayName"] = displayname
    if(description != ""):
        _property["description"] = str(description) 
    
    return _property

def get_id(hostname, component, num, letter, version):
    
    _id = "dtmi:dt" + ":" + hostname + ":" + component + ":" + letter + str(num) + ";" + str(version)
    return _id


def get_telemetry(hostname, name, displayname, comp, num, version, description = "db pointer"):

    telemetry = {}

    telemetry["@id"] = get_id(hostname, comp+"TEL", num, "T", 1)
    telemetry["@type"] = "Telemetry"
    telemetry["schema"] = "string" #For now
    telemetry["name"] = name
    
    telemetry["description"] = description
    telemetry["displayName"] = displayname

    return telemetry
    

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
        _type = 'perfevent.hwcounters'
                                                                                                    
    return _type

def get_my_metrics(my_types):

    my_metrics = []
    for my_type in my_types:
        for item in metrics:
            if(_filter(item) == my_type):
                my_metrics.append(item)

    return my_metrics

                
def add_cpus(models_dict, _sys_dict, top_id, hostname):


    for socket in _sys_dict["affinity"]["socket"]:

        displayName = "socket" + str(socket)
        this_socket_id = get_id(hostname, "socket", socket, "S", 1) #To avoid 0 and conform id req
        this_socket = get_interface(this_socket_id, displayname = displayName)

        ##Add some properties
        ##Assumes one type of cpu
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 1, "C", 1),
                                                    "model", description = _sys_dict["cpu"]["specs"]["model"]))
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 2, "C", 1),
                                                    "cores", description = _sys_dict["cpu"]["specs"]["cores"]))
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 3, "C", 1),
                                                    "threads", description = _sys_dict["cpu"]["specs"]["threads"]))
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 4, "C", 1),
                                                    "threads_per_core", description = _sys_dict["cpu"]["specs"]["threads_per_core"]))
        #this_socket["contents"].append(get_property(get_id(hostname, "cpuspecs", 5, "C", 1),
        #"flags", description = _sys_dict["cpu"]["specs"]["flags"]))
        ## Out of use for now, need to figure out maximum length problem or "instance problem"
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 6, "C", 1),
                                                    "hyperthreading", description = _sys_dict["cpu"]["specs"]["hyperthreading"]))
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 7, "C", 1),
                                                    "max_mhz", description = _sys_dict["cpu"]["specs"]["max_mhz"]))
        this_socket["contents"].append(get_property(get_id(hostname, displayName+"cpuspecs", 8, "C", 1),
                                                    "min_mhz", description = _sys_dict["cpu"]["specs"]["min_mhz"]))
        ##Add some properties

        #Connect socket to the system
        models_dict[top_id]["contents"].append(get_relationship(get_id(hostname, "ownership", g(), "O",1), "contains"+g(), this_socket_id))
        #Connect socket to the system

        #add metrics as telemetry
        my_metrics = get_my_metrics(["pernode", "energy"])
        for count, metric in enumerate(my_metrics):
            m_name = "metric" + str(count)
            this_socket["contents"].append(get_telemetry(hostname, m_name, metric, displayName, count, 1))
        #add metrics as telemetry

        ##add this socket to digital twin
        models_dict[this_socket_id] = this_socket
        ##add this socket to digital twin
        
        ##Now this socket's cores
        for core in _sys_dict["affinity"]["socket"][socket]["cores"]:
        
            core_displayName = "core" + str(core)
            this_core_id = get_id(hostname, displayName+"core", core, "C", 1)
            this_core = get_interface(this_core_id, displayname = core_displayName)

            #Connect core to socket
            models_dict[this_socket_id]["contents"].append(get_relationship(get_id(hostname, "ownership", displayName+str(core), "O", 1), "contains"+ g(), this_core_id))
            #Connect core to socket
            
            #add metrics as telemetry
            my_metrics = get_my_metrics(["uncore"])
            for count, metric in enumerate(my_metrics):
                m_name = "metric" + str(count)
                this_core["contents"].append(get_telemetry(hostname, m_name, metric, core_displayName+g(), count, 1))
            #add metrics as telemetry

            ##Add this core to digital twin
            models_dict[this_core_id] = this_core
            ##Add this core to digital twin

            ##Now this core's threads
            for thread in _sys_dict["affinity"]["socket"][socket]["cores"][core]:

                thread_displayName = "thread" + str(thread)
                this_thread_id = get_id(hostname, "thread", thread, "T", 1)
                this_thread = get_interface(this_thread_id, displayname = thread_displayName)

                ##Connect thread to core
                models_dict[this_core_id]["contents"].append(get_relationship(get_id(hostname, "ownership", thread_displayName+g(), "O", 1), "contains"+g(), this_thread_id))
                ##Connect thread to core
                
                ##add metrics as telemetry
                my_metrics = get_my_metrics(["percpu", "perfevent.hwcounters"])
                for count, metric in enumerate(my_metrics):
                    m_name = "metric" + str(count)
                    this_thread["contents"].append(get_telemetry(hostname, m_name, metric[:64], "THREAD"+g(), count, 1))
                ##add metrics as telemetry

            
                ##MIND THAT:
                ##Every different component type need their own global counter like
                ##instead of g() we need
                ##g_contains()
                ##g_thread()
                ##g_cache()
                ##g_tlb()
                ##Later, this information will be used to model these digital twins separately
                
                
                ##Add this thread to digital twin
                models_dict[this_thread_id] = this_thread
                print("Thread id:", this_thread_id, "added")
                ##Add this thread to digital twin

        ##adding caches after sockets are done
    for cache in _sys_dict["cpu"]["cache"]:
        for group in _sys_dict["cpu"]["cache"][cache]["cache_groups"]:
            cache_id = get_id(hostname, "cache", g() , "C" + g(), 1)
            this_cache = get_interface(cache_id, displayname = cache)

            models_dict[cache_id] = this_cache
            models_dict[cache_id]["contents"].append(get_property(get_id(hostname, "cache", g(), "C" + g(), 1), "associativity", description = _sys_dict["cpu"]["cache"][cache]["associativity"]))
            models_dict[cache_id]["contents"].append(get_property(get_id(hostname, "cache", g(), "C" + g(), 1), "cache_line_size", description = _sys_dict["cpu"]["cache"][cache]["cache_line_size"]))
            models_dict[cache_id]["contents"].append(get_property(get_id(hostname, "cache", g(), "C" + g(), 1), "no_sets", description = _sys_dict["cpu"]["cache"][cache]["no_sets"]))
            models_dict[cache_id]["contents"].append(get_property(get_id(hostname, "cache", g(), "C" + g(), 1), "size", description = _sys_dict["cpu"]["cache"][cache]["size"]))

            for thread in group:
                that_thread_id = get_id(hostname, "thread", thread, "T", 1)
                models_dict[that_thread_id]["contents"].append(get_relationship(get_id(hostname, "ownership", g(), "O", 1), "contains"+g(), cache_id))
        ##adding caches after sockets are done
                
        
        
        
    return models_dict
    


def main():

    models_dict = {}
    _sys_dict = probe.main()

    pprint(_sys_dict)

    ##Top level arrangements
    hostname = _sys_dict["hostname"]
    os = _sys_dict["os"]

    top_id = get_id(hostname, "system", 1, "S", 1)
    top = get_interface(top_id, hostname)

    models_dict[top_id] = top ##models_dict[top_id] is a pointer to main system now
    models_dict[top_id]["contents"].append(get_property(get_id(hostname, "os", 1, "O", 1),
                                                        "os", description = _sys_dict["os"]))
    models_dict[top_id]["contents"].append(get_property(get_id(hostname, "arch", 1, "A",1),
                                                        "arch", description = _sys_dict["arch"]))
    models_dict[top_id]["contents"].append(get_property(get_id(hostname, "kernel", 1, "K",1),
                                                        "kernel", description = _sys_dict["system"]["kernel"]["version"]))
    ##Top level arrangements



    models_dict = add_cpus(models_dict, _sys_dict, top_id, hostname)
    
    
    pprint(models_dict)

    #Because digital twin is a set of interfaces
    models_list = []
    for key in models_dict:
        models_list.append(models_dict[key])


    with open("dt.json", "w") as outfile:
        json.dump(models_list, outfile)

    
if __name__ == "__main__":

    main()



