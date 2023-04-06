import sys
sys.path.append("../")
import utils
import observation_standard as obs
import monitoring_panels as mp

import uuid

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

##
##Monitoring dashboard pre-selected metrics
##
##hinv.cpu.clock
##kernel.all.pressure.cpu.some.total
##lmsensors.coretemp_isa_0000.package_id_0 ##This may change with more numa domains
##lmsensors.coretemp_isa_0001.package_id_1
##kernel.percpu.cpu.idle
##kernel.pernode.cpu.idle
##disk.dev.read
##disk.dev.write
##disk.dev.total
##disk.dev.read_bytes
##disk.dev.write_bytes
##disk.dev.total_bytes
##disk.all.read
##disk.all.write
##disk.all.total
##disk.all.read_bytes
##disk.all.write_bytes
##disk.all.total_bytes
##mem.util.used
##mem.util.free
##swap.pagesin
##mem.numa.util.free
##mem.numa.util.used
##mem.numa.alloc.hit
##mem.numa.alloc.miss
##mem.numa.alloc.local_node
##mem.numa.alloc.other_node
##network.all.in.bytes
##network.all.out.bytes
##kernel.all.nusers
##kernel.all.nprocs

color_schemes_clock = ["RdYlGn", "RdYlBu"]
color_schemes_load = ["Greens", "Blues"]

next_id = -1

def get_next_id():

    global next_id
    next_id += 1
    
    return next_id

def get_params(td, measurement):
    
    params = []
    
    for interface in td:
        #print("interface:", interface)
        for content in td[interface]["contents"]:
            if(content["@type"].find("Telemetry") != -1):
                if(content["DBName"] == measurement):
                    params.append({"Alias": td[interface]["displayName"], "Param": content["displayName"]})
                    #print("content: ", content, "measurement:", measurement)
                    

    return params

def get_params_interface_known(td, interface, measurement):
    
    params = {}
    #print("interface:", interface)
    
    for content in td[interface]["contents"]:
        if(content["@type"].find("Telemetry") != -1):
            #print(content["DBName"], "==>", measurement)
            if(content["DBName"] == measurement):
                params = {"Alias": td[interface]["displayName"], "Param": content["displayName"]}
    if(measurement == "hinv_cpu_clock"): ##Small glitch in twin generation
        params = {"Alias": td[interface]["displayName"], "Param": td[interface]["contents"][0]["displayName"]}
    if(params["Alias"].find("thread") != -1):
        params["Alias"] = params["Alias"].strip("thread") ##For a slicker look
        

    return params

def get_topology(td):

    topol = {}
    

    for interface in td:
        if(interface.find("socket") != -1):
            cores = []
            threads = []
            for content in td[interface]["contents"]:
                if(content["@type"] == "Relationship" and content["target"].find("core") != -1):
                    cores.append(content["target"]) ##Get cores

            for core in cores:
                _interface = td[core]
                for content in _interface["contents"]:
                    if(content["@type"] == "Relationship" and content["target"].find("thread") != -1):
                        threads.append(content["target"]) ##Get threads

            topol[interface] = threads

    return topol
    



def stat_panel(SuperTwin, h, w, x, y, color_scheme, metric, empty_dash):

    datasource = SuperTwin.grafana_datasource
    td = utils.get_twin_description(SuperTwin)
    
    ##Mem Numa Alloc Hit
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, h, w, x, y, color_scheme, metric))
    params = get_params(td, metric)
    print("params:", params)
    for param in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], metric, param["Param"]))

    return empty_dash

'''
    ##Numa Load
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 20, 0, "continuous-GrYlRd", "Numa Load"))
    params = get_params(td, "kernel_pernode_cpu_idle")
    for idx, param in enumerate(params):
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "kernel_pernode_cpu_idle", param["Param"]))
        empty_dash["panels"][panel_id]["targets"][idx]["select"][0].append({"params": [" / 440 * -1 + 100"],"type": "math"})
'''

def name_panel(SuperTwin, empty_dash):

    datasource = SuperTwin.grafana_datasource
    
    empty_dash["panels"].append(mp.name_panel(datasource, get_next_id(), SuperTwin.name))

    return empty_dash


def comprehend(topology, wanted, unit):

    ret = []

    for socket in topology:
        contents = topology[socket]
        for x in contents:
            for y in wanted:
                if(x.find(unit + str(y) + ";") != -1):
                    print("appending:", x)
                    ret.append(x)

    return ret

#def stat_panel(SuperTwin, h, w, x, y, color_scheme, metric, empty_dash):
def freq_clock_panel(SuperTwin, h, w, x, y, threads, empty_dash):

    td = utils.get_twin_description(SuperTwin)
    topology = get_topology(td)
    #print("topology:", topology)
    datasource = SuperTwin.grafana_datasource

    ##need threads -> topology conversion
    #threads = ["dtmi:dt:cisec2022-Z490-AORUS-ULTRA:thread" + str(x) + ";1" for x in threads]
    threads = comprehend(topology, threads, "thread")
    print("threads:", threads)
    
    ##cpu frequency
    for idx, socket in enumerate(topology):
        panel_id = get_next_id()
        empty_dash["panels"].append(mp.clock_panel(datasource, panel_id, h, w, x, y, color_schemes_clock[idx], "Thread Frequency - Socket " + str(idx)))
        for thread in topology[socket]: ##Note that, that was a single list
            ##can filter out threads here?
            if(thread in threads):
                param = get_params_interface_known(td, thread, "hinv_cpu_clock")
                empty_dash["panels"][panel_id]["targets"].append(mp.clock_query(datasource, param["Alias"], "hinv_cpu_clock", param["Param"]))
            
    return empty_dash
            
def load_clock_panel(SuperTwin, h, w, x, y, empty_dash):

    td = utils.get_twin_description(SuperTwin)
    topology = get_topology(td)
    datasource = SuperTwin.datasource
    
    ##load per cpu
    for idx2, socket in enumerate(topology):
        panel_id = get_next_id()
        empty_dash["panels"].append(mp.clock_panel(datasource, h, w, x, y, color_schemes_load[idx2], "Thread Load - Socket " + str(idx2)))
        #print("no_panels:", len(empty_dash))
        for idt, thread in enumerate(topology[socket]): ##Note that, that was a single list
            param = get_params_interface_known(td, thread, "kernel_percpu_cpu_idle")
            empty_dash["panels"][panel_id]["targets"].append(mp.clock_query(datasource, param["Alias"], "kernel_percpu_cpu_idle", param["Param"]))
            empty_dash["panels"][panel_id]["targets"][idt]["select"][0].append({"params": [" /10 *-1 +100"],"type": "math"})

    return empty_dash

#def stat_panel(SuperTwin, h, w, x, y, color_scheme, metric, empty_dash):
def small_single_timeserie(SuperTwin, h, w, x, y, metric, empty_dash):

    datasource = SuperTwin.grafana_datasource
    
    ##no_process
    panel_id = get_next_id() ##This is most probably should come from the caller
    empty_dash["panels"].append(mp.small_single_timeseries(datasource, panel_id, h, w, x, y, metric))
    empty_dash["panels"][panel_id]["targets"].append(mp.small_single_query(datasource, metric, metric))

    return empty_dash

def generate_general_panel(SuperTwin, h, w, x, y, metric, empty_dash):

    td = utils.get_twin_description(SuperTwin)
    datasource = SuperTwin.grafana_datasource
    
    panel_id = get_next_id()
    disk_reads = empty_dash["panels"].append(mp.general_panel(datasource, panel_id, 12, 5, 6, 15, metric))
    params = get_params(td, metric)
    for dev in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, dev["Alias"], metric, dev["Param"]))

    return empty_dash

            
def generate_empty_dash(SuperTwin):

    td = utils.get_twin_description(SuperTwin)

    empty_dash = obs.template_dict(SuperTwin.name + " Monitor-" + str(uuid.uuid4()))
    empty_dash["panels"] = []
    
    return empty_dash

##Upload to grafana
def upload_dashboard(SuperTwin, empty_dash):
    json_dash_obj = obs.get_dashboard_json(empty_dash, overwrite = False)
    g_url = obs.upload_to_grafana(json_dash_obj, SuperTwin.grafana_addr, SuperTwin.grafana_token)
    
    print("Generated:", g_url)
    return g_url["url"]


def generate_monitoring_dashboard(SuperTwin):

    td = utils.get_twin_description(SuperTwin)

    empty_dash = obs.template_dict(SuperTwin.name + " Monitor-" + str(uuid.uuid4()))
    empty_dash["panels"] = []
    
    topology = get_topology(td)
    datasource = SuperTwin.grafana_datasource


    ##Hostname
    empty_dash["panels"].append(mp.name_panel(datasource, get_next_id(), SuperTwin.name))


    ##Mem Numa Alloc Hit
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 16, 0, "continuous-GrYlRd", "Mem Numa Alloc Hit"))
    params = get_params(td, "mem_numa_alloc_hit")
    for param in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "mem_numa_alloc_hit", param["Param"]))

    
    ##Numa Load
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 20, 0, "continuous-GrYlRd", "Numa Load"))
    params = get_params(td, "kernel_pernode_cpu_idle")
    for idx, param in enumerate(params):
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "kernel_pernode_cpu_idle", param["Param"]))
        empty_dash["panels"][panel_id]["targets"][idx]["select"][0].append({"params": [" / 440 * -1 + 100"],"type": "math"})

        
    ##Mem Numa Alloc Miss
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 16, 5, "continuous-GrYlRd", "Mem Numa Alloc Miss"))
    params = get_params(td, "mem_numa_alloc_miss")
    for param in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "mem_numa_alloc_miss", param["Param"]))


    ##Socket Energy
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 20, 0, "continuous-GrYlRd", "Socket Energy"))
    params = get_params(td, "perfevent_hwcounters_RAPL_ENERGY_PKG_value")
    try:
        params = [params[1], params[panel_id]] ##small glitch in twin generation
        #print("Params:", params)
        for idx, param in enumerate(params):
            param["Param"] = param["Param"].replace("core", "cpu") ##Small glitch in twin generation
            empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "perfevent_hwcounters_RAPL_ENERGY_PKG_value", param["Param"]))
            empty_dash["panels"][panel_id]["targets"][idx]["select"][0].append({"params": ["* 0.23 * 0.000000001"],"type": "math"})
            empty_dash["panels"][panel_id]["fieldConfig"]["defaults"]["unit"] = "watt"
    except:
        print("RAPL driver can't be accessed for target host. Proceed without power measurement..")

    ##DRAM Energy
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 20, 10, "continuous-GrYlRd", "Socket DRAM Energy"))
    params = get_params(td, "perfevent_hwcounters_RAPL_ENERGY_DRAM_value")
    try:
        params = [params[1], params[3]] ##small glitch in twin generation
        #print("Params:", params)
        for idx, param in enumerate(params):
            param["Param"] = param["Param"].replace("core", "cpu") ##Small glitch in twin generation
            empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "perfevent_hwcounters_RAPL_ENERGY_DRAM_value", param["Param"]))
            empty_dash["panels"][panel_id]["targets"][idx]["select"][0].append({"params": ["* 0.23 * 0.000000001"],"type": "math"})
            empty_dash["panels"][panel_id]["fieldConfig"]["defaults"]["unit"] = "watt"
    except:
        RAPL_NO_ACCESS = 1


    ##Mem Numa Alloc Other Node
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 16, 10, "continuous-GrYlRd", "Mem Numa Alloc Other Node"))
    params = get_params(td, "mem_numa_alloc_other_node")
    for param in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "mem_numa_alloc_other_node", param["Param"]))

    ##Mem Numa Alloc Local Node
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 16, 15, "continuous-GrYlRd", "Mem Numa Alloc Local Node"))
    params = get_params(td, "mem_numa_alloc_other_node")
    for param in params:
        empty_dash["panels"][6]["targets"].append(mp.stat_query(datasource, param["Alias"], "mem_numa_alloc_local_node", param["Param"]))

    ##socket temperature
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 20, 15, "continuous-GrYlRd", "Socket Temperature"))
    params = get_params(td, "lmsensors_coretemp_isa_0000_package_id_0")
    #print("params:", params)
    for idx, param in enumerate(params):
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, "socket" + str(idx), "lmsensors_coretemp_isa_000"+ str(idx) +"_package_id_" + str(idx), "value"))
        #empty_dash["panels"][7]["targets"].append(mp.stat_query(datasource, "socket1", "lmsensors_coretemp_isa_0001_package_id_1", "value"))
        empty_dash["panels"][panel_id]["fieldConfig"]["defaults"]["unit"] = "celsius"

    ##mem numa used
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 16, 15, "continuous-GrYlRd", "Mem Numa Used"))
    params = get_params(td, "mem_numa_util_used")
    for idx, param in enumerate(params):
        empty_dash["panels"][8]["targets"].append(mp.stat_query(datasource, param["Alias"], "mem_numa_util_used", param["Param"]))
        empty_dash["panels"][8]["targets"][idx]["select"][0].append({"params": [" / 1048576"],"type": "math"})
        empty_dash["panels"][8]["fieldConfig"]["defaults"]["unit"] = "decgbytes"

    ##mem numa free
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.stat_panel(datasource, panel_id, 5, 4, 20, 15, "continuous-RdYlGr", "Mem Numa Free"))
    params = get_params(td, "mem_numa_util_free")
    for idx, param in enumerate(params):
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, param["Alias"], "mem_numa_util_free", param["Param"]))
        empty_dash["panels"][panel_id]["targets"][idx]["select"][0].append({"params": [" / 1048576"],"type": "math"})
        empty_dash["panels"][panel_id]["fieldConfig"]["defaults"]["unit"] = "decgbytes"


    #print("topology:", topology)
    
    ##cpu frequency
    for idx, socket in enumerate(topology):
        panel_id = get_next_id()
        empty_dash["panels"].append(mp.clock_panel(datasource, panel_id, 15, 3, 4 + ((idx)*6), 0, color_schemes_clock[idx], "Thread Frequency - Socket " + str(idx)))
        for thread in topology[socket]: ##Note that, that was a single list
            param = get_params_interface_known(td, thread, "hinv_cpu_clock")
            #print("no panels:", len(empty_dash["panels"]), "panel_id:", panel_id, "+idx:", panel_id + idx)
            empty_dash["panels"][panel_id]["targets"].append(mp.clock_query(datasource, param["Alias"], "hinv_cpu_clock", param["Param"]))
            

            
    ##load per cpu
    for idx2, socket in enumerate(topology):
        panel_id = get_next_id()
        empty_dash["panels"].append(mp.clock_panel(datasource, panel_id, 15, 3, 7 + idx2*6, 0, color_schemes_load[idx2], "Thread Load - Socket " + str(idx2)))
        #print("no_panels:", len(empty_dash))
        for idt, thread in enumerate(topology[socket]): ##Note that, that was a single list
            param = get_params_interface_known(td, thread, "kernel_percpu_cpu_idle")
            empty_dash["panels"][panel_id]["targets"].append(mp.clock_query(datasource, param["Alias"], "kernel_percpu_cpu_idle", param["Param"]))
            empty_dash["panels"][panel_id]["targets"][idt]["select"][0].append({"params": [" /10 *-1 +100"],"type": "math"})


    ##no_process
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.small_single_timeseries(datasource, panel_id, 5, 4, 0, 5, "# of processes"))
    empty_dash["panels"][panel_id]["targets"].append(mp.small_single_query(datasource, "# of processes", "kernel_all_nprocs"))

    ##no_users
    panel_id = get_next_id()
    empty_dash["panels"].append(mp.small_single_timeseries(datasource, panel_id, 5, 4, 0, 10, "# of users"))
    empty_dash["panels"][panel_id]["targets"].append(mp.small_single_query(datasource, "# of users", "kernel_all_nusers"))

    ##network top
    empty_dash["panels"].append(mp.all_network_panel(datasource, get_next_id(), 12, 6, 0, 15))

    ##disk reads
    panel_id = get_next_id()
    disk_reads = empty_dash["panels"].append(mp.disk_panel(datasource, panel_id, 12, 5, 6, 15, "Disk Reads"))
    params = get_params(td, "disk_dev_read")
    for dev in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, dev["Alias"], "disk_dev_read", dev["Param"]))

    ##disk writes
    panel_id = get_next_id()
    disk_writes = empty_dash["panels"].append(mp.disk_panel(datasource, panel_id, 12, 5, 11, 15, "Disk Writes"))
    params = get_params(td, "disk_dev_write")
    for dev in params:
        empty_dash["panels"][panel_id]["targets"].append(mp.stat_query(datasource, dev["Alias"], "disk_dev_write", dev["Param"]))
    
    ##Upload to grafana
    json_dash_obj = obs.get_dashboard_json(empty_dash, overwrite = False)
    g_url = obs.upload_to_grafana(json_dash_obj, SuperTwin.grafana_addr, SuperTwin.grafana_token)
    
    print("Generated:", g_url)

    return g_url["url"]
    

    
    
    
    
