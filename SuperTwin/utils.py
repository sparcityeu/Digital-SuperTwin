from influxdb import InfluxDBClient
import pymongo
from pymongo import MongoClient

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

import datetime
import json
import uuid
import requests

from grafanalib.core import Dashboard
from grafanalib._gen import DashboardEncoder

import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

ALWAYS_EXISTS_MONITOR = ["kernel.all.pressure.cpu.some.total",
                         "hinv.cpu.clock",
                         "lmsensors.coretemp_isa_0000.package_id_0",
                         "kernel.pernode.cpu.idle",
                         "kernel.percpu.cpu.idle",
                         "disk.dev.read",
                         "disk.dev.write",
                         "disk.dev.total",
                         "disk.dev.read_bytes",
                         "disk.dev.write_bytes",
                         "disk.dev.total_bytes",
                         "disk.all.read",
                         "disk.all.write",
                         "disk.all.total",
                         "disk.all.read_bytes",
                         "disk.all.write_bytes",
                         "disk.all.total_bytes",
                         "swap.pagesin",
                         "kernel.all.nusers",
                         "kernel.all.nprocs",
                         "network.all.in.bytes",
                         "network.all.out.bytes"]

ALWAYS_HAVE_MONITOR_NUMA = ALWAYS_EXISTS_MONITOR + ["lmsensors.coretemp_isa_0001.package_id_1",
                                                    "mem.numa.util.free",
                                                    "mem.numa.util.used",
                                                    "mem.numa.alloc.hit",
                                                    "mem.numa.alloc.miss",
                                                    "mem.numa.alloc.local_node",
                                                    "mem.numa.alloc.other_node",
                                                    "perfevent.hwcounters.RAPL_ENERGY_PKG.value",
                                                    "perfevent.hwcounters.RAPL_ENERGY_DRAM.value"]

ALWAYS_HAVE_MONITOR_SINGLE_SOCKET = ALWAYS_EXISTS_MONITOR + ["mem.util.used",
                                                             "mem.util.free",
                                                             "perfevent.hwcounters.RAPL_ENERGY_PKG.value",
                                                             "perfevent.hwcounters.RAPL_ENERGY_DRAM.value"]

SKL_DONT_HAVE = ["perfevent.hwcounters.RAPL_ENERGY_DRAM.value"]
ICL_DONT_HAVE = ["perfevent.hwcounters.RAPL_ENERGY_DRAM.value",
                 "perfevent.hwcounters.RAPL_ENERGY_PKG.value"] ##RAPL is not currenty available on Icelake
ALWAYS_HAVE_MONITOR_SKL = [x for x in ALWAYS_HAVE_MONITOR_SINGLE_SOCKET if x not in SKL_DONT_HAVE]
ALWAYS_HAVE_MONITOR_ICL = [x for x in ALWAYS_HAVE_MONITOR_SINGLE_SOCKET if x not in ICL_DONT_HAVE]


ALWAYS_HAVE_OBSERVATION = ["RAPL_ENERGY_PKG",
                           "RAPL_ENERGY_DRAM"]
ALWAYS_HAVE_OBSERVATION_SKL = ["RAPL_ENERGY_PKG"]
ALWAYS_HAVE_OBSERVATION_ICL = [] ##RAPL is not currently available on Icelake

##
met = {
        'monitor':{
            'general_single': ALWAYS_HAVE_MONITOR_SINGLE_SOCKET,
            'general_numa': ALWAYS_HAVE_MONITOR_NUMA,
            'skl': ALWAYS_HAVE_MONITOR_SKL,
            'icl': ALWAYS_HAVE_MONITOR_ICL
        },
        'observation': {
            'general': ALWAYS_HAVE_OBSERVATION,
            'skl': ALWAYS_HAVE_OBSERVATION_SKL,
            'icl': ALWAYS_HAVE_OBSERVATION_ICL
        }
    }
##

def get_mongo_database(mongodb_name, CONNECTION_STRING):

    ##Create a connection for mongodb
    client = MongoClient(CONNECTION_STRING)
    ##Create the database for this instance(s)

    return client[mongodb_name]


def get_influx_database(address, influxdb_name):

    fields = address.split("//")[1]
    #print("fields:", fields)
    fields = fields.split(":")
    host = fields[0]
    port = fields[1]
    #print("host:", host, "port:", port)
    influxdb = InfluxDBClient(host=host, port=port)

    return influxdb

def read_env():
    reader = open("env.txt", "r")
    lines = reader.readlines()
    reader.close()

    mongodb_addr = lines[0].split("=")[1].strip("\n")
    influxdb_addr = lines[1].split("=")[1].strip("\n")
    grafana_addr = lines[2].split("=")[1].strip("\n")
    grafana_token = lines[3].split("=")[1].strip("\n")
    
    #print("mongodb_addr:", mongodb_addr)
    #print("influxdb_addr:", influxdb_addr)
    #print("grafana_addr:", grafana_addr)
    #print("grafana_token:", grafana_token)
    
    return mongodb_addr, influxdb_addr, grafana_addr, grafana_token

def read_monitor_metrics():

    reader = open("monitor_metrics.txt", "r")
    lines = reader.readlines()
    reader.close()

    metrics = []

    for line in lines:
        if(line.find("#") == -1):
            if(line.find("perfevent.hwcounter") == -1):
                metrics.append(line.strip("\n"))
            if(line.find("perfevent.hwcounter") != -1):
                metrics.append(line.strip("\n") + ".value")
                metrics.append(line.strip("\n") + ".dutycycle")
                
    return metrics

def read_observation_metrics():

    reader = open("last_observation_metrics.txt", "r")
    lines = reader.readlines()
    reader.close()

    metrics = []

    for line in lines:
        if(line.find("#") == -1):
            metrics.append(line.strip("\n"))
                            
    return metrics

def update_state(name, addr, twin_id, collection_id):

    writer = open("supertwin.state", "a")
    #writer.write("#--------------------------------------------------#")
    #writer.write("\n")
    writer.write(name + "|" + addr + "|" + twin_id + "|" + collection_id)
    writer.write("\n")
    writer.close()

def check_state(addr):

    exist = False
    name = None
    twin_id = None
    collection_id = None

    try:
        reader = open("supertwin.state", "r")
        lines = reader.readlines()

    except:
        lines = []


    #print("check_state: lines:", lines)
    for line in lines:
        #if(line.find("#---") == -1):
        fields = line.strip("\n").split("|")
        
        if(addr == fields[1]):
            exist = True
            name = fields[0]
            addr = fields[1]
            twin_id = fields[2]
            collection_id = fields[3]
            #return exist, name, twin_id, collection_id
            
    return exist, name, twin_id, collection_id


#Hyperthreading, on-off?
def get_multithreading_info(data):
    '''
    @param data: digital twin description
    '''
    mt_info = {}
    mt_info["no_sockets"] = 0

    for key in data:
        
        if(key.find("socket") != -1):
            subdata = data[key]["contents"]
            mt_info["no_sockets"] = mt_info["no_sockets"] + 1
            
            for content in subdata:
                if(content["name"] == "cores"):
                    mt_info["no_cores_per_socket"] = int(content["description"])
                if(content["name"] == "threads"):
                    mt_info["no_threads_per_socket"] = int(content["description"])
                    

    mt_info["total_cores"] = mt_info["no_cores_per_socket"] * mt_info["no_sockets"]
    mt_info["total_threads"] = mt_info["no_threads_per_socket"] * mt_info["no_sockets"]
            

    return mt_info

def create_grafana_datasource(hostname, uid, api_key, grafana_server, influxdb_server, verify=True):

    headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}
    data = {
        "name": hostname + "_" + uid + "_influx_datasource",
        "type":"influxdb",
        "url":influxdb_server,
        "database": hostname,
        "access":"proxy",
        "basicAuth":False
    }
    r = requests.post(f"http://{grafana_server}/api/datasources", data=json.dumps(data), headers=headers, verify=verify)
    #print(f"{r.status_code} - {r.content}")

    return dict(r.json())


def upload_to_grafana(json, server, api_key, verify=True):
    
    '''
    upload_to_grafana tries to upload dashboard to grafana and prints response    
    :param json - dashboard json generated by grafanalib
    :param server - grafana server name
    :param api_key - grafana api key with read and write privileges
    '''
    
    headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}
    r = requests.post(f"http://{server}/api/dashboards/db", data=json, headers=headers, verify=verify)
    # TODO: add error handling
    # TODO: return and read uid and url, add it to observation digital twin
    print(f"{r.status_code} - {r.content}")
    return dict(r.json())

def get_dashboard_json(dashboard, overwrite, message="Updated by grafanalib"):
    '''
    get_dashboard_json generates JSON from grafanalib Dashboard object
    :param dashboard - Dashboard() created via grafanalib
    '''

    # grafanalib generates json which need to pack to "dashboard" root element
    return json.dumps(
        {
            "dashboard": dashboard,
            "overwrite": overwrite,
            "message": message
        }, sort_keys=True, indent=2, cls=DashboardEncoder)


def get_empty_dashboard(title):

    _template = {}

    _template["id"] = None ##to_get: id
    #_template["id"] = next_dash_id() ##to_get: id
    _template["timepicker"] = {}
    _template["timezone"] = ""
    _template["title"] = title
    _template["uid"] = None ##to_get: uid
    _template["version"] = 0
    _template["weekStart"] = ""
    _template["schemaVersion"] = 37
    _template["style"] = "dark"
    _template["tags"] = []
    _template["editable"] = True
    _template["graphTooltip"] = 0
    _template["links"] = []
    _template["fiscalYearStartMonth"] = 0
    _template["liveNow"] = False
    #_template["refresh"] = "1s" ##Not exist in example
    
    _template["templating"] = {}
    _template["templating"]["list"] = []

    _template["time"] = {}
    _template["time"]["from"] = "now-5m" ##param: time-from
    _template["time"]["to"] = "now"      ##param: time-to

    
    _template["annotations"] = {}
    _template["annotations"]["list"] = []
    lzd = {} ##list zero dict, default list
    lzd["builtIn"] = 1
    lzd["enable"] = True
    lzd["hide"] = True
    lzd["iconColor"] = "rgba(0, 211, 255, 1)"
    #lzd["name"] = "Annotations & Alerts"
    lzd["name"] = str(uuid.uuid4())
    lzd["type"] = "dashboard"
    
    lzd["datasource"] = {}
    lzd["datasource"]["type"] = "grafana"
    lzd["datasource"]["uid"] = "-- Grafana --"

    lzd["target"] = {}
    lzd["target"]["limit"] = 100
    lzd["target"]["matchAny"] = False
    lzd["target"]["tags"] = []
    lzd["target"]["type"] = "dashboard"
    _template["annotations"]["list"].append(lzd)

    _template["panels"] = []

    return _template

def fill_data(data, hostname, hostip):
    '''
    Fills necessary system information by looking up twin description
    :param data - is a digital twin description
    :param hostname - remote host name
    :param hostip - remote host ip
    '''
    system_hostname = hostname
    system_ip = hostip
    system_os = ""
    system_no_numa_nodes = 0
    system_no_disks = 0

    cpu_model = ""
    cpu_cores = 0
    cpu_threads = 0
    cpu_threads_per_core = 0
    cpu_hyperthreading = ""
    cpu_maxmhz = 0
    cpu_minmhx = 0
    
    
    l1dcache_size = 0
    l1dcache_associativity = 0
    l1dcache_linesize = 0
    l1dcache_nosets = 0

    l2cache_size = 0 ##MegaBytes
    l2cache_associativity = 0 
    l2cache_linesize = 0 ##Bytes
    l2cache_nosets = 0

    l3cache_size = 0
    l3cache_associativity = 0
    l3cache_linesize = 0
    l3cache_nosets = 0

    cpu = True
    l1d_cache = True
    l2_cache = True
    l3_cache = True

    sse_vector = []
    avx_vector = []
    
    #Get all data in one loop, using 'cases'
    for key in data:
        #print("key:", key)

        ##SYSTEM
        if(key.find("system") != -1):
            subdata = data[key]["contents"]
            #print("subdata:", subdata)

            for content in subdata:
                if(content["@id"].find("os") != -1):
                    system_os = content["description"]

        ##CPU
        if(key.find("socket") != -1 and cpu):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "model"):
                    cpu_model = content["description"]
                if(content["name"] == "cores"):
                    cpu_cores = int(content["description"])
                if(content["name"] == "threads"):
                    cpu_threads = int(content["description"])
                if(content["name"] == "threads_per_core"):
                    cpu_threads_per_core = int(content["description"])
                if(content["name"] == "hyperthreading"):
                    cpu_hyperthreading = content["description"]
                if(content["name"] == "max_mhz"):
                    cpu_maxmhz = float(content["description"])
                if(content["name"] == "min_mhz"):
                    cpu_minmhz = float(content["description"])
                
            cpu = False


        #l1dcache
        if(key.find("L1D") != -1 and l1d_cache):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "associativity"):
                    l1dcache_associativity = content["description"]
                if(content["name"] == "size"):
                    l1dcache_size = content["description"]
                if(content["name"] == "no_sets"):
                    l1dcache_nosets = content["description"]
                if(content["name"] == "cache_line_size"):
                    l1dcache_linesize = content["description"]

            l1d_cache = False


        #l2cache
        if(key.find("L2") != -1 and l2_cache):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "associativity"):
                    l2cache_associativity = content["description"]
                if(content["name"] == "size"):
                    l2cache_size = content["description"]
                if(content["name"] == "no_sets"):
                    l2cache_nosets = content["description"]
                if(content["name"] == "cache_line_size"):
                    l2cache_linesize = content["description"]

            l2_cache = False



        #l3cache
        if(key.find("L3") != -1 and l3_cache):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "associativity"):
                    l3cache_associativity = content["description"]
                if(content["name"] == "size"):
                    l3cache_size = content["description"]
                if(content["name"] == "no_sets"):
                    l3cache_nosets = content["description"]
                if(content["name"] == "cache_line_size"):
                    l3cache_linesize = content["description"]

            l3_cache = False


        ##vector extensions
        if(key.find("socket") != -1):
            contents = data[key]["contents"]
            for content in contents:
                if(content["name"] == "flags"):
                    flags = content["description"]
                    for item in flags.split(" "):
                        if(item.find("sse") != -1):
                            if(item not in sse_vector):
                                sse_vector.append(item)
                        if(item.find("avx") != -1):
                            if(item not in avx_vector):
                                avx_vector.append(item)
                            
                        
        ##NO_NUMA_NODES
        if(key.find("socket") != -1):
            system_no_numa_nodes += 1
            
            
        ##disks
        if(key.find("disk;1") != -1):
            system_no_disks = int(data[key]["contents"][0]["description"])

            
    cpu_ghz = float(cpu_model.split("@")[1].strip("GHz"))

    
    #print("sse_vector:", sse_vector)
    #print("avx_vector:", avx_vector)
    
    data = {"system_hostname": system_hostname,
            "system_ip": system_ip,
            "system_os": system_os,
            "system_no_numa_nodes": system_no_numa_nodes,
            "system_no_disks": system_no_disks,
            "cpu_model" : cpu_model,
            "cpu_cores": cpu_cores,
            "cpu_threads": cpu_threads,
            "cpu_threads_per_core": cpu_threads_per_core,
            "cpu_hyperthreading": cpu_hyperthreading,
            "cpu_ghz": cpu_ghz,
            "cpu_maxmhz": cpu_maxmhz,
            "cpu_minmhz": cpu_minmhz,
            "l1dcache_size": l1dcache_size,
            "l1dcache_associativity": l1dcache_associativity,
            "l1dcache_linesize": l1dcache_linesize,
            "l1dcache_nosets": l1dcache_nosets,
            "l2cache_size": l2cache_size,
            "l2cache_associativity": l2cache_associativity,
            "l2cache_linesize": l2cache_linesize,
            "l2cache_nosets": l2cache_nosets,
            "l3cache_size": l3cache_size,
            "l3cache_associativity": l3cache_associativity,
            "l3cache_linesize": l3cache_linesize,
            "l3cache_nosets": l3cache_nosets,
            "sse_vector": sse_vector,
            "avx_vector": avx_vector}
            #"no_fma_units": 2, ##change this with fma_number_benchmark
            #"max_vector_size": 512} ##change this with vector extension look-up
    
    return data


def obscure(data: bytes) -> bytes:
    return b64e(zlib.compress(data, 9))

def unobscure(obscured: bytes) -> bytes:
    return zlib.decompress(b64d(obscured))


def get_twin_with_meta(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]

    return meta_with_twin

def get_twin_description(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]
    twin = meta_with_twin["twin_description"]

    return twin

def get_observations(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["observations"]

    return db


def get_system_dict_from_td(td):

    for key in td:
        if(key.find("system") != -1):
            return td[key]


def get_selected_from_dict(_dict, selected):
    
    
    for content in _dict["contents"]:
        if(content["@id"].find(selected) != -1):
            return content
    

def get_msr(SuperTwin):

    td = get_twin_description(SuperTwin)
    _system = get_system_dict_from_td(td)
    msr = get_selected_from_dict(_system, "MSR")["description"]

    return msr

def get_msr_td(td):

    _system = get_system_dict_from_td(td)
    msr = get_selected_from_dict(_system, "MSR")["description"]

    return msr

def is_numa(SuperTwin):

    td = get_twin_description(SuperTwin)
    mt = get_multithreading_info(td)

    if(mt["no_sockets"] == 1):
        return False
    else:
        return True

def is_numa_td(td): ##td versions are actually same with SuperTwin versions but avoids time of asking twin description to database, therefore much faster

    mt = get_multithreading_info(td)

    if(mt["no_sockets"] == 1):
        return False
    else:
        return True

##always have metrics adjusted to msrs
def always_have_metrics(purpose, SuperTwin):

    numa = is_numa(SuperTwin)
    msr = get_msr(SuperTwin)
    
    if(msr != "icl" and msr != "skl"):
        msr = "general"
        
    if(purpose == "monitor"):
        if(numa):
            msr = "general_numa"
        else:
            if(msr != "icl" and msr != "skl"):
                msr = "general_single"

    return met[purpose][msr]

##always have metrics adjusted to msrs
def always_have_metrics_td(purpose, td):

    numa = is_numa_td(td)
    msr = get_msr_td(td)
    
    if(msr != "icl" and msr != "skl"):
        msr = "general"
        
    if(purpose == "monitor"):
        if(numa):
            msr = "general_numa"
        else:
            if(msr != "icl" and msr != "skl"):
                msr = "general_single"

    return met[purpose][msr]


def get_biggest_vector_inst(td):

    avx = False
    avx2 = False
    avx512 = False
    
    for key in td:
        if(key.find("socket") != -1):
            contents = td[key]["contents"]

            for content in contents:
                if(content["name"].find("flags") != -1):
                    for flag in content["description"].split(" "):
                        if(flag.find("avx512") != -1):
                            avx512 = True
                        if(flag.find("avx2") != -1):
                            avx2 = True
                        if(flag.find("avx") != -1):
                            avx = True


    if(avx512):
        return "avx512"
    if(avx2):
        return "avx2"
    if(avx):
        return "avx"

    return None



##It would be much if contents will be dictionary instead of list. Require big refactorization. Fix this later.
def find_component(td, _id):

    for item in td:
        if(td[item]["@id"] == _id):
            return td[item]
        
    return None
        

def find_first(td, socket_content):

    for c_content in socket_content:
        if (c_content["@type"] == "Relationship"):
            core = find_component(td, c_content["target"]) ##First core
            
            for t_content in core["contents"]:
                if(t_content["@type"] == "Relationship"):
                    thread = find_component(td, t_content["target"]) ##First thread
                    break
            break

    return int(thread["displayName"].strip("thread"))



def first_thread_of_sockets(td):

    first = {}
    sock = 0 
    for key in td:
        if(key.find("socket") != -1):
            contents = td[key]["contents"]
            first[str(sock)] = find_first(td, contents)
            sock += 1
            

    return first

def find_socket_threads_td(td):

    ts = {}
    socket = -1
    for key in td:
        if(key.find("socket") != -1):
            socket += 1
            str_socket = str(socket)
            ts[str_socket] = []
            socket_content = td[key]["contents"]
            for c_content in socket_content:
                if (c_content["@type"] == "Relationship"):
                    core = find_component(td, c_content["target"]) ##First core
            
                    for t_content in core["contents"]:
                        if(t_content["@type"] == "Relationship"):
                            thread = int(find_component(td, t_content["target"])["displayName"].strip("thread"))
                            ts[str_socket].append(thread)


    for key in ts:
        ts[key] = list(sorted(ts[key]))
        
    return ts


def prepare_st_likwid_pin(td, st_affinity):
    
    ret_str = ""
    
    is_numa = is_numa_td(td)
    mt_info = get_multithreading_info(td)

    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]

    topology = find_socket_threads_td(td)
    if(st_affinity.find("S") != -1): ##Socket
               
        sockets = st_affinity.split("@")

        for idx, one_socket in enumerate(sockets):
            socket_name = "S" + str(idx)
            socket_idx = str(idx)
            is_strided = bool(one_socket.count(":") > 1)
            requested_threads = int(one_socket.split(":")[1])
            ret_str += socket_name + ":"
            
            if(is_strided):
                for i in range(requested_threads):
                    if(i > no_cores_per_socket - 1):
                        ret_str += str(topology[socket_idx][(i*2) - no_threads_per_socket - 1]) + ","
                    else:
                        ret_str += str(topology[socket_idx][i * 2]) + ","
                ret_str = ret_str[:-1]
            else:
                for i in range(requested_threads):
                    ret_str += str(topology[socket_idx][i]) + ","
                ret_str = ret_str[:-1]
            ret_str += "@"
        ret_str = ret_str[:-1]

    return ret_str ##(+likwid-pin -m -c)?
            
def resolve_st_likwid_pin(td, st_affinity):

    resolved_threads = []
    
    is_numa = is_numa_td(td)
    mt_info = get_multithreading_info(td)

    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    topology = find_socket_threads_td(td)
    
    if(st_affinity.find("S") != -1): ##Socket
               
        sockets = st_affinity.split("@")

        for idx, one_socket in enumerate(sockets):
            socket_name = "S" + str(idx)
            socket_idx = str(idx)
            is_strided = bool(one_socket.count(":") > 1)
            requested_threads = int(one_socket.split(":")[1])

            if(is_strided):
                for i in range(requested_threads):
                    if(i > no_cores_per_socket - 1):
                        resolved_threads.append(topology[socket_idx][(i*2) - no_threads_per_socket - 1])
                    else:
                        resolved_threads.append(topology[socket_idx][i * 2])
            else:
                for i in range(requested_threads):
                    resolved_threads.append(topology[socket_idx][i])

    return list(sorted(resolved_threads)) ##(+likwid-pin -m -c)?
    
    
def resolve_likwid_pin(td, affinity):

    print("Affinity:", affinity)
    
    first = first_thread_of_sockets(td)
    resolved_threads = []

    if(affinity.find("N") == -1): ##Socket notation
    
        sockets = affinity.strip("likwid-pin -c ")
        sockets = sockets.split("@")

        for socket_str in sockets:
            socket,threads = socket_str.split(":")
            socket = socket.strip("S")
            first_thr = first[socket]
            
            all_threads = threads.split(",")
            for thread in all_threads:
                if(thread.find("-") == -1):
                    resolved_threads.append(first[socket] + int(thread))
                else:
                    range_start, range_end = thread.split("-")
                    for i in range(int(range_start), int(range_end)):
                        resolved_threads.append(first[socket] + i)

    else: ##Thread notation

        _all = affinity.strip("likwid-pin -c N:")
        _all_threads = _all.split(",")
        for thread in _all_threads:
            if(thread.find("-") == -1):
                resolved_threads.append(int(thread))
            else:
                range_start, range_end = thread.split("-")
                for i in range(int(range_start), int(range_end)):
                    resolved_threads.append(i)

    print("resolved threads:", resolved_threads)
    resolved_threads = list(sorted(resolved_threads))
    return resolved_threads
