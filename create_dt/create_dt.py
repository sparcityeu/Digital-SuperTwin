import sys
sys.path.append("../system_query")

import probe
import detect_utils

from pprint import pprint
import json

context = "dtmi:dtdl:context;2"

relationvar = -1
componentvar = -1
propertyvar = -1
telemetryvar = -1
cachevar = -1

metrics = detect_utils.output_lines('pmprobe')                                                  
metrics = [x.split(" ")[0] for x in metrics]

##Enumerate relations
def r():

    global relationvar
    relationvar = relationvar + 1

    return str(relationvar)

def c():
    global componentvar
    componentvar = componentvar + 1

    return str(componentvar)

def cc():
    global cachevar
    cachevar = cachevar + 1

    return str(cachevar)

def p():
    global propertyvar
    propertyvar = propertyvar + 1

    return str(propertyvar)

def t():
    global telemetryvar
    telemetryvar = telemetryvar + 1

    return str(telemetryvar)
    

##g_contains()
                ##g_thread()
                ##g_cache()
                ##g_tlb()


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

##Need category here
def get_uid(hostname, component, _type, version): 

    _id = ""
    
    if(_type != ""):
        _id = "dtmi:dt" + ":" + hostname + ":" + component + ":" + _type +";" + str(version)
    else:
        _id = "dtmi:dt" + ":" + hostname + ":" + component + ";" + str(version)
        
    return _id


def get_telemetry(hostname, name, displayname, comp, version, description = "db pointer"):

    telemetry = {}

    telemetry["@id"] = get_uid(hostname, comp, "telemetry" + t() , 1)
    telemetry["@type"] = "Telemetry"
    telemetry["schema"] = "string" #For now
    telemetry["name"] = name
    
    telemetry["description"] = description
    telemetry["displayName"] = displayname[:63]

    return telemetry

def get_telemetry_mapped(hostname, name, field_key, measurement, comp, version):

    telemetry = {}

    telemetry["@id"] = get_uid(hostname, comp , "telemetry" + t(), 1)
    telemetry["@type"] = "Telemetry"
    telemetry["schema"] = "string"
    telemetry["name"] = name

    telemetry["displayName"] = field_key
    telemetry["description"] = measurement

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
        _type = 'network.interface'                                                                        
    elif(metric.find('network') != -1 and metric.find("network.interface") == -1): #Only top level metrics
        _type = 'network.top'                                                                           
    elif(metric.find('disk.dev') != -1):
        _type = 'disk.dev'
    elif(metric.find('disk.all') != -1):
        _type = 'disk.all'
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

def add_my_metrics(models_dict, this_comp_id, hostname, displayname, my_categories):

    my_metrics = get_my_metrics(my_categories)
    
    for count, metric in enumerate(my_metrics):
        m_name = "metric" + str(count)
        models_dict[this_comp_id]["contents"].append(get_telemetry(hostname, m_name, metric, displayname, 1))

    return models_dict

def add_my_metrics_mapped(models_dict, this_comp_id, hostname, displayname, field_key, my_categories):

    my_metrics = get_my_metrics(my_categories)
    my_metrics = my_metrics[:250] #Only until migrate to RDF
    
    for count, metric in enumerate(my_metrics):
        m_name = "metric" + str(count)
        measurement = metric.replace(".", "_")
        models_dict[this_comp_id]["contents"].append(get_telemetry_mapped(hostname, m_name, field_key, measurement, displayname, 1))

    return models_dict


def add_sockets(models_dict, _sys_dict, top_id, hostname, socket):


    displayName = "socket" + str(socket)
    field_key = "_node" + str(socket) 
    this_socket_id = get_uid(hostname, displayName, "", 1)
    this_socket = get_interface(this_socket_id, displayname = displayName)

    #################################
    ##Add this socket to digital twin
    models_dict[this_socket_id] = this_socket
    ##Add this socket to digital twin
    #################################
    
    ##############################
    ##Connect socket to the system
    contains = c()
    models_dict[top_id]["contents"].append(get_relationship(get_uid(hostname, "system", "ownership" + contains, 1),  "contains" + contains, this_socket_id))
    ##Connect socket to the system
    ##############################
    
    #######################
    ##Add chosen properties
    ##Assumes every node have same CPU
    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property0", 1),
                                                "model", description = _sys_dict["cpu"]["specs"]["model"]))
    
    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property1", 1),
                                                "cores", description = _sys_dict["cpu"]["specs"]["cores"]))
    
    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property2", 1),
                                                "threads", description = _sys_dict["cpu"]["specs"]["threads"]))
    
    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property3", 1),
                                                "threads_per_core", description = _sys_dict["cpu"]["specs"]["threads_per_core"]))

    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property4", 1),
                                                "hyperthreading", description = _sys_dict["cpu"]["specs"]["hyperthreading"]))
    
    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property5", 1),
                                                "max_mhz", description = _sys_dict["cpu"]["specs"]["max_mhz"]))
    
    this_socket["contents"].append(get_property(get_uid(hostname, displayName, "property6", 1),
                                                "min_mhz", description = _sys_dict["cpu"]["specs"]["min_mhz"]))
    
    ##Add chosen properties
    #######################

    ##########################
    ##add metrics as telemetry
    models_dict = add_my_metrics_mapped(models_dict, this_socket_id, hostname, displayName, field_key, ["pernode", "energy"])
    ##add metrics as telemetry
    ##########################
    
    return models_dict, this_socket_id


def add_cores(models_dict, _sys_dict, top_id, hostname, socket_id, socket_num, core):

    socket_displayName = "socket" + str(socket_num)
    core_displayName = "core" + str(core)
    this_core_id = get_uid(hostname, core_displayName, "", 1)
    this_core = get_interface(this_core_id, displayname = core_displayName)

    ###############################
    ##Add this core to digital twin
    models_dict[this_core_id] = this_core
    ##Add this core to digital twin
    ###############################
    
    ########################
    ##Connect core to socket
    contains = c()
    models_dict[socket_id]["contents"].append(get_relationship(get_uid(hostname, socket_displayName, "contains" + contains , 1),  "contains" + contains, this_core_id))
    ##Connect core to socket
    ########################

    ##########################
    ##add metrics as telemetry
    #models_dict = add_my_metrics(models_dict, this_core_id, hostname, core_displayName, ["uncore"])
    ##Uncores are also moved to threads since values reported for them are per thread
    ##add metrics as telemetry
    ##########################

    return models_dict, this_core_id
    

def add_threads(models_dict, _sys_dict, top_id, hostname, socket_id, socket_num, core_id, core_num, thread):

    socket_displayName = "socket" + str(socket_num)
    core_displayName = "core" + str(core_num)
    thread_displayName = "thread" + str(thread)
    field_key = "_core" + str(thread) 
    this_thread_id = get_uid(hostname, thread_displayName, "", 1)
    this_thread = get_interface(this_thread_id, displayname = thread_displayName)

    ###############################
    ##Add this thread to digital twin
    models_dict[this_thread_id] = this_thread
    ##Add this thread to digital twin
    ###############################
    
    ########################
    ##Connect thread to core
    contains = c()
    models_dict[core_id]["contents"].append(get_relationship(get_uid(hostname, core_displayName, "contains" + contains, 1),  "contains" + contains, this_thread_id))
    ##Connect thread to core
    ########################

    ##########################
    ##add metrics as telemetry
    models_dict = add_my_metrics_mapped(models_dict, this_thread_id, hostname, thread_displayName, field_key, ["percpu", "perfevent.hwcounters", "uncore"])
    ##add metrics as telemetry
    ##########################

    return models_dict, this_thread_id


def add_caches(models_dict, _sys_dict, top_id, hostname, cache):

    for group in _sys_dict["cpu"]["cache"][cache]["cache_groups"]:

        cache_enum = cc()
        cache_displayName = cache
        _type = "cc" + cache_enum
        _added = cache_displayName + ":" + _type
        cache_id = get_uid(hostname, cache_displayName, _type, 1)
        this_cache = get_interface(cache_id, displayname = cache_displayName)

        ################################
        ##Add this cache to digital twin
        models_dict[cache_id] = this_cache
        ##Add this cache to digital twin
        ################################
        
        ######################
        ##Add cache properties
        models_dict[cache_id]["contents"].append(get_property(get_uid(hostname, _added, "property0", 1), "associativity", description = _sys_dict["cpu"]["cache"][cache]["associativity"]))
        models_dict[cache_id]["contents"].append(get_property(get_uid(hostname, _added, "property1", 1), "cache_line_size", description = _sys_dict["cpu"]["cache"][cache]["cache_line_size"]))
        models_dict[cache_id]["contents"].append(get_property(get_uid(hostname, _added, "property2", 1), "no_sets", description = _sys_dict["cpu"]["cache"][cache]["no_sets"]))
        models_dict[cache_id]["contents"].append(get_property(get_uid(hostname, _added, "property3", 1), "size", description = _sys_dict["cpu"]["cache"][cache]["size"]))
        ##Add cache properties
        ######################

        ############################
        ##Add caches to it's threads
        for thread in group:
            that_thread_displayName = "thread" + str(thread)
            print("group: ", group, "thread:", that_thread_displayName)
            that_thread_id = get_uid(hostname, that_thread_displayName, "", 1)
            contains = c()
            models_dict[that_thread_id]["contents"].append(get_relationship(get_uid(hostname, that_thread_displayName, "contains" + contains, 1),  "contains" + contains, cache_id))
        ##Add caches to it's threads
        ############################

    return models_dict
        
    
def add_cpus(models_dict, _sys_dict, top_id, hostname):


    for socket in _sys_dict["affinity"]["socket"]:
        
        models_dict, this_socket_id = add_sockets(models_dict, _sys_dict, top_id, hostname, socket)

        for core in _sys_dict["affinity"]["socket"][socket]["cores"]:

            models_dict, this_core_id = add_cores(models_dict, _sys_dict, top_id, hostname, this_socket_id, socket, core)

            for thread in _sys_dict["affinity"]["socket"][socket]["cores"][core]:
                
                models_dict, this_thread_id = add_threads(models_dict, _sys_dict, top_id, hostname, this_socket_id, socket, this_core_id, core, thread)
                
                
    ##adding caches after sockets are done
    for cache in _sys_dict["cpu"]["cache"]:
        add_caches(models_dict, _sys_dict, top_id, hostname, cache)            
        
        
    return models_dict


def add_memory_banks(models_dict, _sys_dict, top_id, hostname, top_memory):

    for bank in _sys_dict["memory"]["banks"]:

        displayName = bank.replace(":", "")
        this_bank_id = get_uid(hostname, displayName, "", 1)
        this_bank = get_interface(this_bank_id, displayname = displayName)

        ###############################
        ##Add this bank to digital twin
        models_dict[this_bank_id] = this_bank
        ##Add this bank to digital twin
        ###############################
        
        
        #######################################
        ##Connect this bank to top level memory
        contains = c()
        models_dict[top_memory]["contents"].append(get_relationship(get_uid(hostname, "memory", "contains" + contains, 1), "contains" + contains, this_bank_id))
        ##Connect this bank to top level memory
        #######################################

        #######################
        ##Add chosen properties
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property0", 1), "id", description = str(_sys_dict["memory"]["banks"][bank]["id"])))
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property1", 1), "size", description = str(_sys_dict["memory"]["banks"][bank]["size"])))
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property2", 1), "slot", description = str(_sys_dict["memory"]["banks"][bank]["slot"])))
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property3", 1), "clock", description = str(_sys_dict["memory"]["banks"][bank]["clock"])))
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property4", 1), "description", description = str(_sys_dict["memory"]["banks"][bank]["description"])))
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property6", 1), "vendor", description = str(_sys_dict["memory"]["banks"][bank]["vendor"])))
        this_bank["contents"].append(get_property(get_uid(hostname, displayName, "property7", 1), "model", description = str(_sys_dict["memory"]["banks"][bank]["model"])))
        ##Add chosen properties
        #######################

    return models_dict

def add_memory(models_dict, _sys_dict, top_id, hostname):

    displayName = "memory"
    top_memory_id = get_uid(hostname, displayName, "", 1)
    top_memory = get_interface(top_memory_id, displayname = displayName)

    ######################################
    ##Add top level memory to digital twin
    models_dict[top_memory_id] = top_memory
    ##Add top level memory to digital twin
    ######################################

    ########################################
    ##Connect top level memory to the system
    contains = c()
    models_dict[top_id]["contents"].append(get_relationship(get_uid(hostname, "system", "ownership" + contains, 1), "contains" + contains, top_memory_id))
    ##Connect top level memory to the system
    ########################################

    #######################
    ##Add chosen properties
    top_memory["contents"].append(get_property(get_uid(hostname, displayName, "property0", 1),
                                               "totalsize", description = str(_sys_dict["memory"]["total"]["size"])))
    top_memory["contents"].append(get_property(get_uid(hostname, displayName, "property1", 1),
                                               "totalbanks", description = str(_sys_dict["memory"]["total"]["banks"])))
    ##Add chosen properties
    #######################

    ##################
    ##Add memory banks
    models_dict = add_memory_banks(models_dict, _sys_dict, top_id, hostname, top_memory_id)
    ##Add memory banks
    ##################

    return models_dict

def add_phy_disks(models_dict, _sys_dict, top_id, hostname, top_disk_id):

    for disk in _sys_dict["disk"]:

        ##Avoid non-disk top level properties
        if type(_sys_dict["disk"][disk]) is dict:

            disk_displayName = disk
            field_key = "_" + disk
            this_disk_id = get_uid(hostname, "disk:" + disk_displayName, "", 1)
            this_disk = get_interface(this_disk_id, displayname = disk_displayName)

            ########################################
            ##Add this physical disk to digital twin
            models_dict[this_disk_id] = this_disk
            ##Add this physical disk to digital twin
            ########################################

            ###########################
            ##Connect to top level disk
            contains = c()
            models_dict[top_disk_id]["contents"].append(get_relationship(get_uid(hostname, disk_displayName, "contains" + contains, 1), "contains" + contains, this_disk_id))
            ##Connect to top level disk
            ###########################

            #######################
            ##Add chosen properties
            this_disk["contents"].append(get_property(get_uid(hostname, disk_displayName, "property0", 1), "size", description = str(_sys_dict["disk"][disk]["size"])))
            this_disk["contents"].append(get_property(get_uid(hostname, disk_displayName, "property1", 1), "model", description = str(_sys_dict["disk"][disk]["model"])))
            this_disk["contents"].append(get_property(get_uid(hostname, disk_displayName, "property2", 1), "rotational", description = str(_sys_dict["disk"][disk]["rotational"])))
            ##Add chosen properties
            #######################

            ##########################
            ##add metrics as telemetry
            models_dict = add_my_metrics_mapped(models_dict, this_disk_id, hostname, disk_displayName, field_key, ["disk.dev"])
            ##add metrics as telemetry
            ##########################

    return models_dict

            
def add_disk(models_dict, _sys_dict, top_id, hostname):

    top_disk_displayName = "disk"
    field_key = "_value"
    top_disk_id = get_uid(hostname, top_disk_displayName, "", 1)
    top_disk = get_interface(top_disk_id, displayname = top_disk_displayName)

    ##############################
    ##Add top disk to digital twin
    models_dict[top_disk_id] = top_disk
    ##Add top disk to digital twin
    ##############################

    ######################################
    ##Connect top level disk to the system
    contains = c()
    models_dict[top_id]["contents"].append(get_relationship(get_uid(hostname, "system", "ownership" + contains, 1), "contains" + contains, top_disk_id))
    ##Connect top level disk to the system
    ######################################
    
    #######################
    ##Add chosen properties
    top_disk["contents"].append(get_property(get_uid(hostname, top_disk_displayName, "property0", 1), "no_disks", description = str(_sys_dict["disk"]["no_disks"])))
    ##Add chosen properties
    #######################

    ##########################
    ##add metrics as telemetry
    models_dict = add_my_metrics_mapped(models_dict, top_disk_id, hostname, top_disk_displayName, field_key, ["disk.all"])
    ##add metrics as telemetry
    ##########################

    add_phy_disks(models_dict, _sys_dict, top_id, hostname, top_disk_id)

    return models_dict


def add_subnets(models_dict, _sys_dict, top_id, hostname, top_network_id):

    for network_key in _sys_dict["network"]:
        network = _sys_dict["network"][network_key]
        ##For now, ignore networks that are down and virtual networks
        if(network["link"] == "yes" and network["virtual"] == "no"):

            network_displayName = network_key
            field_key = "_" + network_key
            this_network_id = get_uid(hostname, "network:" + network_displayName, "", 1)
            this_network = get_interface(this_network_id, displayname = network_displayName)

            ##################################
            ##Add this network to digital twin
            models_dict[this_network_id] = this_network
            ##Add this network to digital twin
            ##################################

            ###########################################
            ##Connect this network to top level network
            contains = c()
            models_dict[top_network_id]["contents"].append(get_relationship(get_uid(hostname, network_displayName, "contains" + contains, 1), "contains" + contains, this_network_id))
            ##Connect this network to top level network
            ###########################################

            #######################
            ##Add chosen properties
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property0", 1), "ipv4", description = str(network["ipv4"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property1", 1), "businfo", description = str(network["businfo"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property2", 1), "vendor", description = str(network["vendor"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property3", 1), "model", description = str(network["model"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property4", 1), "firmware", description = str(network["firmware"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property5", 1), "virtual", description = str(network["virtual"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property6", 1), "speed", description = str(network["speed"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property7", 1), "serial", description = str(network["serial"])))
            this_network["contents"].append(get_property(get_uid(hostname, network_displayName, "property8", 1), "link", description = str(network["link"])))
            ##Add chosen properties
            #######################
            
            ##########################
            ##Add metrics as telemetry
            models_dict = add_my_metrics_mapped(models_dict, this_network_id, hostname, network_displayName, field_key, ["network.interface"])
            ##Add metrics as telemetry
            ##########################

    return models_dict
            
        

def add_network(models_dict, _sys_dict, top_id, hostname):

    displayName = "network"
    field_key = "_value"
    top_network_id = get_uid(hostname, displayName, "", 1)
    top_network = get_interface(top_network_id, displayname = displayName)

    #################################
    ##Add top network to digital twin
    models_dict[top_network_id] = top_network
    ##Add top network to digital twin
    #################################

    ###################################
    ##Connect top network to the system
    contains = c()
    models_dict[top_id]["contents"].append(get_relationship(get_uid(hostname, "system", "ownership" + contains, 1), "contains" + contains, top_network_id))
    ##Connect top network to the system
    ###################################

    ##########################
    ##Add metrics as telemetry
    models_dict = add_my_metrics_mapped(models_dict, top_network_id, hostname, displayName, field_key, ["network.top"])
    ##Add metrics as telemetry
    ##########################

    add_subnets(models_dict, _sys_dict, top_id, hostname, top_network_id)

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
    models_dict = add_memory(models_dict, _sys_dict, top_id, hostname)
    models_dict = add_disk(models_dict, _sys_dict, top_id, hostname)
    models_dict = add_network(models_dict, _sys_dict, top_id, hostname)
    
    
    pprint(models_dict)

    #Because digital twin is a set of interfaces
    models_list = []
    for key in models_dict:
        models_list.append(models_dict[key])


    # now write output to a file
    with open("dt.json", "w") as outfile:
        json.dump(models_list, outfile)

    
        
    #wdict = open("sys_dict.json", "w")
    #wdict.write(json.dumps(_sys_dict, indent=2))
    #wdict.close()        
    
if __name__ == "__main__":

    main()



