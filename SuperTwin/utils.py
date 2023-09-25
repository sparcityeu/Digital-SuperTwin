from influxdb import InfluxDBClient
from pymongo import MongoClient

##Cloud database
from pymongo.server_api import ServerApi

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

import datetime
import json
import uuid
import requests

from grafanalib._gen import DashboardEncoder
import generate_dt

from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from gridfs import GridFS
import zlib

import paramiko

import sys
import os

sys.path.append("dashboards")
import observation_standard

## can be listed with pmprobe
ALWAYS_EXISTS_MONITOR = [
    "kernel.all.pressure.cpu.some.total",
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
    "swap.pagesin",
    "kernel.all.nusers",
    "kernel.all.nprocs",
    "network.all.in.bytes",
    "network.all.out.bytes",
]

ALWAYS_HAVE_MONITOR_NUMA = ALWAYS_EXISTS_MONITOR + [
    "lmsensors.coretemp_isa_0001.package_id_1",
    "mem.numa.util.free",
    "mem.numa.util.used",
    "mem.numa.alloc.hit",
    "mem.numa.alloc.miss",
    "mem.numa.alloc.local_node",
    "mem.numa.alloc.other_node",
    "perfevent.hwcounters.RAPL_ENERGY_PKG.value",
    "perfevent.hwcounters.RAPL_ENERGY_DRAM.value",
]

ALWAYS_HAVE_MONITOR_SINGLE_SOCKET = ALWAYS_EXISTS_MONITOR + [
    "mem.util.used",
    "mem.util.free",
    "perfevent.hwcounters.RAPL_ENERGY_PKG.value",
    "perfevent.hwcounters.RAPL_ENERGY_DRAM.value",
]

SKL_DONT_HAVE = ["perfevent.hwcounters.RAPL_ENERGY_DRAM.value"]
ICL_DONT_HAVE = [
    "perfevent.hwcounters.RAPL_ENERGY_DRAM.value",
    "perfevent.hwcounters.RAPL_ENERGY_PKG.value",
]  ##RAPL is not currenty available on Icelake
ALWAYS_HAVE_MONITOR_SKL = [
    x for x in ALWAYS_HAVE_MONITOR_SINGLE_SOCKET if x not in SKL_DONT_HAVE
]
ALWAYS_HAVE_MONITOR_ICL = [
    x for x in ALWAYS_HAVE_MONITOR_SINGLE_SOCKET if x not in ICL_DONT_HAVE
]


ALWAYS_HAVE_OBSERVATION = ["RAPL_ENERGY_PKG", "RAPL_ENERGY_DRAM"]
ALWAYS_HAVE_OBSERVATION_SKL = ["RAPL_ENERGY_PKG"]
ALWAYS_HAVE_OBSERVATION_ICL = []  ##RAPL is not currently available on Icelake

##
met = {
    "monitor": {
        "general_single": ALWAYS_HAVE_MONITOR_SINGLE_SOCKET,  # single sockets
        "general_numa": ALWAYS_HAVE_MONITOR_NUMA,  # multiple sockets
        "skl": ALWAYS_HAVE_MONITOR_SKL,
        "icl": ALWAYS_HAVE_MONITOR_ICL,
    },
    "observation": {
        "general": ALWAYS_HAVE_OBSERVATION,  # general
        "skl": ALWAYS_HAVE_OBSERVATION_SKL,  # skylake
        "icl": ALWAYS_HAVE_OBSERVATION_ICL,  # icelake
    },
}
##


def get_mongo_database(mongodb_name, CONNECTION_STRING):

    ##Create a connection for mongodb
    client = MongoClient(CONNECTION_STRING)
    ##Create the database for this instance(s)

    return client[mongodb_name]

def v2_check_performance_database():
    
    reader = open("cloud_mongo.txt", "r")
    uri = reader.readlines()[0].strip("\n")

    client = MongoClient(uri, server_api=ServerApi("1"))

    try:
        client.admin.command("ping")
        print("Pinged cloud database.. Succesfully connected!")
    except:
        print("Cannot connect cloud database..")



def v2_get_performance_database():

    reader = open("cloud_mongo.txt", "r")
    uri = reader.readlines()[0].strip("\n")

    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client["GlobalPerformanceDatabase"]
    
    return db

def v2_is_inserted_to_gpd(SuperTwin):

    client = v2_get_performance_database()
    collection = client["Twins"]

    twin_with_meta = get_twin_with_meta(SuperTwin)
    uid = twin_with_meta["uid"]
    inserted_twins = collection.find({"uid": uid})

    found = False

    try:
        td = inserted_twins[0]
        found = True
    except:
        found = False

    return found

def v2_insert_twin_to_gpd(SuperTwin):

    if(v2_is_inserted_to_gpd(SuperTwin)):
        print("This SuperTwin Description is already inserted to global performance database..")
    else:
        client = v2_get_performance_database()
        collection = client["Twins"]
        twin_with_meta = get_twin_with_meta(SuperTwin)
        
        to_insert = {"uid": twin_with_meta["uid"], "STD": twin_with_meta["twin_description"]}
        
        collection.insert_one(to_insert)
        print("SuperTwin Description successfuly inserted to global performance database..")


def v2_get_data_for_metric(SuperTwin, ObservationInterface):

    db = get_influx_database(SuperTwin.influxdb_addr)
    db.switch_database(SuperTwin.influxdb_name)

    
def v2_generate_thread_query(metric, displayName, tagkey):

    #all = "SELECT " + displayName + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    min = "SELECT " + "MIN("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    max = "SELECT " + "MAX("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    mean = "SELECT " + "MEAN("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    median = "SELECT " + "MEDIAN("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    mode = "SELECT " + "MODE("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    spread = "SELECT " + "SPREAD("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    stddev = "SELECT " + "STDDEV("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    sum = "SELECT " + "SUM("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"
    integral = "SELECT " + "INTEGRAL("+displayName + ")" + " FROM " + metric + ' where "tag"' + "=" + "'" + tagkey + "'"

    queries = {}
    #queries[displayName] = all
    queries["min"] = min
    queries["max"] = max
    queries["mean"] = mean
    queries["median"] = median
    queries["mode"] = mode
    queries["spread"] = spread
    queries["stddev"] = stddev
    queries["sum"] = sum
    queries["integral"] = integral

    return queries


def v2_return_aggregates(SuperTwin, queries):

    aggregates = {}
    
    db = get_influx_database(SuperTwin.influxdb_addr)
    db.switch_database(SuperTwin.influxdb_name)
    
    for key in queries.keys():
        #print("Running query:", queries[key])
        result = list(db.query(queries[key]))
        #print("result:", result[0][0])
        aggregates[key] = result[0][0][key]

    #print(aggregates)
    return aggregates

def v2_generate_queries_and_aggregate(SuperTwin, ObservationInterface): ##For threads
    ##Need to categorize metrics beforehand this operation and generate queries like
    ##select _cpu2 from, select _socket0 from, select * from, select value from etc.

    print("Involved sw:", ObservationInterface["monitor_metrics"])
    print("Involved hw:", ObservationInterface["observation_metrics"])

    hw_metrics = ObservationInterface["observation_metrics"]
    hw_metrics = [x for x in hw_metrics if x.find("ENERGY") == -1]

    print("new hw metrics:", hw_metrics)

    _td = get_twin_description(SuperTwin)

    threads = ["thread" + str(x) + ";" for x in ObservationInterface["involved_threads"]]
    print("threads interface ids:", threads)
    
    for metric in hw_metrics:
        for thread in threads:
            for key in _td.keys():
                if(key.find(thread) != -1):
                    print("Thread:", thread, "key:", key)
                    contents = _td[key]["contents"]
                    for content in contents:
                        if(content["@type"] == "HWTelemetry"):
                            if(content["PMUName"] == metric):
                                print("dbname:", content["DBName"])
                                queries = v2_generate_thread_query(content["DBName"], content["displayName"], ObservationInterface["observation_db_tag"])
                                aggregates = v2_return_aggregates(SuperTwin, queries)
                    
def v2_insert_observation_to_gpd(SuperTwin, ObservationInterface):

    v2_generate_queries_and_aggregate(SuperTwin, ObservationInterface)
    
    twin_with_meta = get_twin_with_meta(SuperTwin)
    twin_uid = twin_with_meta["uid"]
    
    if(not v2_is_inserted_to_gpd(SuperTwin)):
        v2_insert_twin_to_gpd(SuperTwin)

        
    client = v2_get_performance_database()
    collection = client["Observations"]
    
    to_insert = {"twin_uid": twin_with_meta["uid"], "ObservationInterface": ObservationInterface}
    
    collection.insert_one(to_insert)
    print("Observation", ObservationInterface["uid"], "successfuly inserted to global performance database..")
    
    


def get_influx_database(address):

    fields = address.split("//")[1]
    fields = fields.split(":")
    host = fields[0]
    port = fields[1]
    return InfluxDBClient(host=host, port=port)


def read_env():
    env_variables = {}
    with open("env.txt", "r") as env:
        for x in env.readlines():
            try:
                key, value = x.split("=")
                env_variables[key] = value.strip("\n")
            except:  ##GRAFANA TOKEN MAY INCLUDE ADDITIONAL = SIGNS
                key = "GRAFANA_TOKEN"
                value = x.split("GRAFANA_TOKEN=")[1]
                env_variables[key] = value.strip("\n")

    return (
        env_variables["MONGODB_SERVER"],
        env_variables["INFLUX_1.8_SERVER"],
        env_variables["GRAFANA_SERVER"],
        env_variables["GRAFANA_TOKEN"],
    )


def get_twin_description_from_file(
    hostProbFile, alias, SSHuser, SSHpass, addr
):

    with open(hostProbFile, "r") as j:
        _sys_dict = json.loads(j.read())

    _twin = generate_dt.main(_sys_dict, alias, SSHuser, SSHpass, addr)
    return _twin


def register_twin_state(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]

    meta["twin_state"] = {}
    meta["twin_state"]["SSHuser"] = SuperTwin.SSHuser
    meta["twin_state"]["SSHpass"] = obscure(str.encode(SuperTwin.SSHpass))
    meta["twin_state"]["monitor_tag"] = SuperTwin.monitor_tag
    meta["twin_state"]["benchmarks"] = SuperTwin.benchmarks
    meta["twin_state"]["benchmark_results"] = SuperTwin.benchmark_results
    meta["twin_state"]["monitor_metrics"] = SuperTwin.monitor_metrics
    meta["twin_state"]["observation_metrics"] = SuperTwin.observation_metrics
    meta["twin_state"]["grafana_datasource"] = SuperTwin.grafana_datasource
    meta["twin_state"]["pcp_pids"] = SuperTwin.pcp_pids
    
    db.replace_one({"_id": ObjectId(SuperTwin.mongodb_id)}, meta)

    print("Twin state is registered to db..")


def insert_twin_description(_twin, supertwin):

    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")

    hostname = supertwin.name
    CONNECTION_STRING = supertwin.mongodb_addr

    mongodb = get_mongo_database(hostname, CONNECTION_STRING)
    collection = mongodb["twin"]

    metadata = {
        "uid": supertwin.uid,
        "address": supertwin.addr,
        "hostname": supertwin.name,
        "date": date,
        "twin_description": _twin,
        "influxdb_name": supertwin.influxdb_name,
        "influxdb_tag": supertwin.monitor_tag,
        "monitor_pid": "",
        "prob_file": supertwin.prob_file,
        "roofline_dashboard": "to be added",
        "monitoring_dashboard": "to be added",
    }

    result = collection.insert_one(metadata)
    twin_id = str(result.inserted_id)

    return twin_id

    

def read_monitor_metrics():

    reader = open("monitor_metrics.txt", "r")
    lines = reader.readlines()
    reader.close()

    metrics = []

    for line in lines:
        if line.find("#") == -1:
            if line.find("perfevent.hwcounter") == -1:
                metrics.append(line.strip("\n"))
            if line.find("perfevent.hwcounter") != -1:
                metrics.append(line.strip("\n") + ".value")
                metrics.append(line.strip("\n") + ".dutycycle")

    return metrics


def read_observation_metrics():

    reader = open("last_observation_metrics.txt", "r")
    lines = reader.readlines()
    reader.close()

    metrics = []

    for line in lines:
        if line.find("#") == -1:
            metrics.append(line.strip("\n"))

    return metrics


def update_state(name, addr, twin_id, collection_id):

    writer = open("supertwin.state", "a")
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
    for line in lines:
        fields = line.strip("\n").split("|")

        if addr == fields[1]:
            exist = True
            name = fields[0]
            addr = fields[1]
            twin_id = fields[2]
            collection_id = fields[3]

    return exist, name, twin_id, collection_id


# Hyperthreading, on-off?
def get_multithreading_info(data):
    """
    @param data: digital twin description
    """
    mt_info = {}
    mt_info["no_sockets"] = 0

    for key in data:

        if key.find("socket") != -1:
            subdata = data[key]["contents"]
            mt_info["no_sockets"] = mt_info["no_sockets"] + 1

            for content in subdata:
                if content["name"] == "cores":
                    mt_info["no_cores_per_socket"] = int(
                        content["description"]
                    )
                if content["name"] == "threads":
                    mt_info["no_threads_per_socket"] = int(
                        content["description"]
                    )

    mt_info["total_cores"] = (
        mt_info["no_cores_per_socket"] * mt_info["no_sockets"]
    )
    mt_info["total_threads"] = (
        mt_info["no_threads_per_socket"] * mt_info["no_sockets"]
    )

    return mt_info


def create_influx_database(influx_datasource, db_name):
    influx_datasource.create_database(db_name)


def create_grafana_datasource(
    hostname, uid, api_key, grafana_server, influxdb_server, verify=True
):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "name": hostname + "_" + uid + "_influx_datasource",
        "type": "influxdb",
        "url": influxdb_server,
        "database": hostname,
        "access": "proxy",
        "basicAuth": False,
    }

    r = requests.post(
        f"http://{grafana_server}/api/datasources",
        data=json.dumps(data),
        headers=headers,
        verify=verify,
    )
    print(f"{r.status_code} - {r.content}")
    return dict(r.json())


def upload_to_grafana(json, server, api_key, verify=True):

    """
    upload_to_grafana tries to upload dashboard to grafana and prints response
    :param json - dashboard json generated by grafanalib
    :param server - grafana server name
    :param api_key - grafana api key with read and write privileges
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    r = requests.post(
        f"http://{server}/api/dashboards/db",
        data=json,
        headers=headers,
        verify=verify,
    )
    # TODO: add error handling
    # TODO: return and read uid and url, add it to observation digital twin
    print(f"{r.status_code} - {r.content}")
    return dict(r.json())


def get_dashboard_json(dashboard, overwrite, message="Updated by grafanalib"):
    """
    get_dashboard_json generates JSON from grafanalib Dashboard object
    :param dashboard - Dashboard() created via grafanalib
    """

    # grafanalib generates json which need to pack to "dashboard" root element
    return json.dumps(
        {"dashboard": dashboard, "overwrite": overwrite, "message": message},
        sort_keys=True,
        indent=2,
        cls=DashboardEncoder,
    )


def get_empty_dashboard(title):

    _template = {}

    _template["id"] = None  ##to_get: id
    # _template["id"] = next_dash_id() ##to_get: id
    _template["timepicker"] = {}
    _template["timezone"] = ""
    _template["title"] = title
    _template["uid"] = None  ##to_get: uid
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
    # _template["refresh"] = "1s" ##Not exist in example

    _template["templating"] = {}
    _template["templating"]["list"] = []

    _template["time"] = {}
    _template["time"]["from"] = "now-5m"  ##param: time-from
    _template["time"]["to"] = "now"  ##param: time-to

    _template["annotations"] = {}
    _template["annotations"]["list"] = []
    lzd = {}  ##list zero dict, default list
    lzd["builtIn"] = 1
    lzd["enable"] = True
    lzd["hide"] = True
    lzd["iconColor"] = "rgba(0, 211, 255, 1)"
    # lzd["name"] = "Annotations & Alerts"
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
    """
    Fills necessary system information by looking up twin description
    :param data - is a digital twin description
    :param hostname - remote host name
    :param hostip - remote host ip
    """
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

    l2cache_size = 0  ##MegaBytes
    l2cache_associativity = 0
    l2cache_linesize = 0  ##Bytes
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

    # Get all data in one loop, using 'cases'
    for key in data:
        # print("key:", key)

        ##SYSTEM
        if key.find("system") != -1:
            subdata = data[key]["contents"]
            # print("subdata:", subdata)

            for content in subdata:
                if content["@id"].find("os") != -1:
                    system_os = content["description"]

        ##CPU
        if key.find("socket") != -1 and cpu:
            subdata = data[key]["contents"]

            for content in subdata:
                if content["name"] == "model":
                    cpu_model = content["description"]
                if content["name"] == "cores":
                    cpu_cores = int(content["description"])
                if content["name"] == "threads":
                    cpu_threads = int(content["description"])
                if content["name"] == "threads_per_core":
                    cpu_threads_per_core = int(content["description"])
                if content["name"] == "hyperthreading":
                    cpu_hyperthreading = content["description"]
                if content["name"] == "max_mhz":
                    cpu_maxmhz = float(content["description"])
                if content["name"] == "min_mhz":
                    cpu_minmhz = float(content["description"])

            cpu = False

        # l1dcache
        if key.find("L1D") != -1 and l1d_cache:
            subdata = data[key]["contents"]

            for content in subdata:
                if content["name"] == "associativity":
                    l1dcache_associativity = content["description"]
                if content["name"] == "size":
                    l1dcache_size = content["description"]
                if content["name"] == "no_sets":
                    l1dcache_nosets = content["description"]
                if content["name"] == "cache_line_size":
                    l1dcache_linesize = content["description"]

            l1d_cache = False

        # l2cache
        if key.find("L2") != -1 and l2_cache:
            subdata = data[key]["contents"]

            for content in subdata:
                if content["name"] == "associativity":
                    l2cache_associativity = content["description"]
                if content["name"] == "size":
                    l2cache_size = content["description"]
                if content["name"] == "no_sets":
                    l2cache_nosets = content["description"]
                if content["name"] == "cache_line_size":
                    l2cache_linesize = content["description"]

            l2_cache = False

        # l3cache
        if key.find("L3") != -1 and l3_cache:
            subdata = data[key]["contents"]

            for content in subdata:
                if content["name"] == "associativity":
                    l3cache_associativity = content["description"]
                if content["name"] == "size":
                    l3cache_size = content["description"]
                if content["name"] == "no_sets":
                    l3cache_nosets = content["description"]
                if content["name"] == "cache_line_size":
                    l3cache_linesize = content["description"]

            l3_cache = False

        ##vector extensions
        if key.find("socket") != -1:
            contents = data[key]["contents"]
            for content in contents:
                if content["name"] == "flags":
                    flags = content["description"]
                    for item in flags.split(" "):
                        if item.find("sse") != -1:
                            if item not in sse_vector:
                                sse_vector.append(item)
                        if item.find("avx") != -1:
                            if item not in avx_vector:
                                avx_vector.append(item)

        ##NO_NUMA_NODES
        if key.find("socket") != -1:
            system_no_numa_nodes += 1

        ##disks
        if key.find("disk;1") != -1:
            system_no_disks = int(data[key]["contents"][0]["description"])

    cpu_ghz = (
        float(cpu_model.split("@")[1].strip("GHz"))
        if len(cpu_model.split("@")) > 1
        else cpu_minmhz / 1000.0
    )

    # print("sse_vector:", sse_vector)
    # print("avx_vector:", avx_vector)

    data = {
        "system_hostname": system_hostname,
        "system_ip": system_ip,
        "system_os": system_os,
        "system_no_numa_nodes": system_no_numa_nodes,
        "system_no_disks": system_no_disks,
        "cpu_model": cpu_model,
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
        "avx_vector": avx_vector,
    }
    # "no_fma_units": 2, ##change this with fma_number_benchmark
    # "max_vector_size": 512} ##change this with vector extension look-up

    return data


def obscure(data: bytes) -> bytes:
    return b64e(zlib.compress(data, 9))


def unobscure(obscured: bytes) -> bytes:
    return zlib.decompress(b64d(obscured))


def get_twin_with_meta(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(
        dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)}))
    )[0]

    return meta_with_twin


def get_twin_description(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(
        dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)}))
    )[0]
    twin = meta_with_twin["twin_description"]

    return twin


def get_observations(SuperTwin):

    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)[
        "observations"
    ]

    return db


def get_system_dict_from_td(td):

    for key in td:
        if key.find("system") != -1:
            return td[key]


def get_selected_from_dict(_dict, selected):

    for content in _dict["contents"]:
        if content["@id"].find(selected) != -1:
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

    if mt["no_sockets"] == 1:
        return False
    else:
        return True


def is_numa_td(
    td,
):  ##td versions are actually same with SuperTwin versions but avoids time of asking twin description to database, therefore much faster

    mt = get_multithreading_info(td)

    if mt["no_sockets"] == 1:
        return False
    else:
        return True


##always have metrics adjusted to msrs
def always_have_metrics(purpose, SuperTwin):

    numa = is_numa(SuperTwin)
    msr = get_msr(SuperTwin)

    if msr != "icl" and msr != "skl":
        msr = "general"

    if purpose == "monitor":
        if numa:
            msr = "general_numa"
        else:
            if msr != "icl" and msr != "skl":
                msr = "general_single"

    return met[purpose][msr]


def get_biggest_vector_inst(td):

    avx = False
    avx2 = False
    avx512 = False

    for key in td:
        if key.find("socket") != -1:
            contents = td[key]["contents"]

            for content in contents:
                if content["name"].find("flags") != -1:
                    for flag in content["description"].split(" "):
                        if flag.find("avx512") != -1:
                            avx512 = True
                        if flag.find("avx2") != -1:
                            avx2 = True
                        if flag.find("avx") != -1:
                            avx = True

    if avx512:
        return "avx512"
    if avx2:
        return "avx2"
    if avx:
        return "avx"

    return None

def get_biggest_vector_inst_carm(td):

    sse = False
    avx2 = False
    avx512 = False

    for key in td:
        if key.find("socket") != -1:
            contents = td[key]["contents"]

            for content in contents:
                if content["name"].find("flags") != -1:
                    for flag in content["description"].split(" "):
                        if flag.find("avx512") != -1:
                            avx512 = True
                        if flag.find("avx2") != -1:
                            avx2 = True
                        if flag.find("sse") != -1:
                            sse = True

    if avx512:
        return "avx512"
    if avx2:
        return "avx2"
    if sse:
        return "sse"

    return None

def get_cpu_vendor(td):

    for key in td:
        if(key.find("socket") != -1):
            contents = td[key]["contents"]

            for content in contents:
                if(content["name"] == "model"):
                    string = content["description"]
                    if "intel" in string.lower():
                        return "intel"
                    elif "amd" in string.lower():
                        return "amd"

    return None


##It would be much if contents will be dictionary instead of list. Require big refactorization. Fix this later.
def find_component(td, _id):

    for item in td:
        if td[item]["@id"] == _id:
            return td[item]

    return None


def find_first(td, socket_content):

    for c_content in socket_content:
        if c_content["@type"] == "Relationship":
            core = find_component(td, c_content["target"])  ##First core

            for t_content in core["contents"]:
                if t_content["@type"] == "Relationship":
                    thread = find_component(
                        td, t_content["target"]
                    )  ##First thread
                    break
            break

    return int(thread["displayName"].strip("thread"))


def first_thread_of_sockets(td):

    first = {}
    sock = 0
    for key in td:
        if key.find("socket") != -1:
            contents = td[key]["contents"]
            first[str(sock)] = find_first(td, contents)
            sock += 1

    return first


def find_socket_threads_td(td):

    ts = {}
    socket = -1
    for key in td:
        if key.find("socket") != -1:
            socket += 1
            str_socket = str(socket)
            ts[str_socket] = []
            socket_content = td[key]["contents"]
            for c_content in socket_content:
                if c_content["@type"] == "Relationship":
                    core = find_component(
                        td, c_content["target"]
                    )  ##First core

                    for t_content in core["contents"]:
                        if t_content["@type"] == "Relationship":
                            thread = int(
                                find_component(td, t_content["target"])[
                                    "displayName"
                                ].strip("thread")
                            )
                            ts[str_socket].append(thread)

    for key in ts:
        ts[key] = list(sorted(ts[key]))

    return ts


def prepare_bind(SuperTwin, no_threads, affinity, policy):

    td = get_twin_description(SuperTwin)

    mt_info = get_multithreading_info(td)
    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    support_ht = True

    if total_cores == total_threads:
        support_ht = False

    numa_multip = 1
    is_mnuma = is_numa(SuperTwin)
    if is_mnuma:
        numa_multip *= 2

    base = "likwid-pin -q "
    if policy != -1 and policy == "m":
        base += "-m "
    if policy != -1 and policy == "i":
        base += "-i "
    base += "-c "

    ##edge cases
    ##these are edge cases that are not easily generalized
    ##also catch them in resolve
    if no_threads == 1:
        base += "N:0"
        return base
    if no_threads == 2:
        if affinity == "compact":
            base += "N:0," + str(no_cores_per_socket * numa_multip)
            return base
        if affinity == "balanced":
            base += "N:0-1"
            return base
        if affinity == "compact numa" or affinity == "balanced numa":
            base += "S0:0@S1:0"
            return base
    if no_threads == 4:
        if affinity == "compact":
            base += (
                "N:0-1,"
                + str(no_cores_per_socket * numa_multip)
                + "-"
                + str(no_cores_per_socket * numa_multip + 1)
            )
            return base
        if affinity == "balanced":
            base += "N:0-3"
            return base
        if affinity == "compact numa":
            _per_socket = "0," + str(no_cores_per_socket)
            base += "S0:" + _per_socket + "@" + "S1:" + _per_socket
            return base
        if affinity == "balanced numa":
            base += "S0:0-1@S1:0-1"
            return base

    if affinity == "compact":
        per_comp = int(no_threads / 2)
        if per_comp > 1:
            base += "N:0-" + str(per_comp - 1) + ","
            base += (
                str(no_cores_per_socket * numa_multip)
                + "-"
                + str(no_cores_per_socket * numa_multip + (per_comp - 1))
            )
        if per_comp == 1:
            base += "N:0," + str(no_cores_per_socket)

    elif affinity == "balanced":
        base += "N:0-" + str(no_threads - 1)

    elif affinity == "compact numa":
        per_node = int(no_threads / 2)
        per_comp = int(per_node / 2)

        if per_node == 1:
            base += "S0:0-1@S1:0-1"
            return base
        elif per_comp == 1:
            base += (
                "S0:0,"
                + str(no_cores_per_socket)
                + "@"
                + "S1:0,"
                + str(no_cores_per_socket)
            )
            return base

        comp0_start = 0
        comp1_start = no_cores_per_socket

        # print("comp0_start", comp0_start, "comp1_start", comp1_start, "per_node:", per_node,
        # "per_comp", per_comp)

        _str = (
            str(comp0_start)
            + "-"
            + str(comp0_start + per_comp - 1)
            + ","
            + str(comp1_start)
            + "-"
            + str(comp1_start + per_comp - 1)
        )

        base += "S0:" + _str + "@"
        base += "S1:" + _str

    elif affinity == "balanced numa":
        per_node = int(no_threads / 2)

        if per_node == 1:
            base += "S0:0-1@S1:0-1"
            return base

        base += "S0:0-" + str(per_node - 1) + "@"
        base += "S1:0-" + str(per_node - 1)

    return base


def complete_to_six(pids):

    for key in pids:
        pid = pids[key]
        while len(pid) < 6:
            pid = "0" + pid
        pids[key] = pid

    return pids


def get_pid(line):

    fields = line.split(" ")
    fields = [x for x in fields if x != ""]

    return fields[1]


def get_pcp_pids(SuperTwin):
    return get_pcp_pids_by_credentials(
        SuperTwin.SSHuser, SuperTwin.SSHpass, SuperTwin.addr
    )


def get_pcp_pids_by_credentials(SSHuser, SSHpass, addr):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(addr, username=SSHuser, password=SSHpass)

    stdin, stdout, stderr = ssh.exec_command("ps aux | grep pcp")
    output = stdout.read()
    output = output.decode("utf-8")
    output = output.split("\n")

    pids = {}

    for item in output:

        if item.find("pmproxy") != -1:
            pids["pmproxy"] = get_pid(item)
        if item.find("pmie") != -1:
            pids["pmie"] = get_pid(item)
        if item.find("pmcd") != -1:
            pids["pmcd"] = get_pid(item)
        if item.find("pmdaproc") != -1:
            pids["pmdaproc"] = get_pid(item)
        if item.find("pmdalinux") != -1:
            pids["pmdalinux"] = get_pid(item)
        if item.find("pmdalmsensors") != -1:
            pids["pmdalmsensors"] = get_pid(item)
        if item.find("pmdaperfevent") != -1:
            pids["pmdaperfevent"] = get_pid(item)

    print("pids:", pids)
    pids = complete_to_six(pids)
    print("pids:", pids)
    return pids


def resolve_bind(SuperTwin, bind):

    involved_threads = []

    td = get_twin_description(SuperTwin)
    first_threads = first_thread_of_sockets(td)

    mt_info = get_multithreading_info(td)
    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    support_ht = True

    if total_cores == total_threads:
        support_ht = False

    try:
        bind = bind.strip("likwid-pin -q -m -c ")
    except:
        bind = bind.strip("likwid-pin -q -c ")

    ##edge cases
    ##these are edge cases that are not easily generalized
    if bind == "N:0," + str(no_cores_per_socket):
        return [0, no_cores_per_socket]  ##Two threads compact
    if bind == "N:0," + str(no_cores_per_socket * 2):
        return [
            0,
            no_cores_per_socket * 2,
        ]  ##Two threads compact but machine is numa :)
    if bind == "N:0-1":
        return [0, 1]  ##Two threads balanced
    if bind == "S0:0@S1:0":
        return [0, no_cores_per_socket]  ##Two threads numa balance or compact
    if bind == "N:0-1," + str(no_cores_per_socket) + "-" + str(
        no_cores_per_socket + 1
    ):
        return [
            0,
            1,
            no_cores_per_socket,
            no_cores_per_socket + 1,
        ]  ##Four threads compact
    if bind == "N:0-3":
        return [0, 1, 2, 3]  ##Four threads balanced

    _per_socket = "0," + str(no_cores_per_socket)
    if bind == "S0:" + _per_socket + "@" + "S1:" + _per_socket:
        return [
            0,
            no_cores_per_socket,
            no_cores_per_socket * 2,
            no_cores_per_socket * 3,
        ]  # 4 threads numa compact
    if bind == "S0:0-1@S1:0-1":
        return [
            0,
            1,
            no_cores_per_socket,
            no_cores_per_socket + 1,
        ]  ##4 threads numa balanced

    if (
        bind.find("@") == -1 and bind.find("-") == -1 and bind.find(",") == -1
    ):  ##Single threaded bind
        print("T:Single threaded")
        thread = int(bind.strip("N:"))
        return [thread]

    if (
        bind.find("@") == -1 and bind.find("-") != -1 and bind.find(",") == -1
    ):  ##Single socket balanced
        print("T:Single socket balanced")
        bind = bind.strip("N:")

        _from = int(bind.split("-")[0])
        _to = int(bind.split("-")[1])

        for i in range(_from, _to + 1):
            involved_threads.append(i)

    if (
        bind.find("@") == -1 and bind.find("-") != -1 and bind.find(",") != -1
    ):  ##Single socket compact
        print("T:Single socket compact")
        bind = bind.strip("N:")

        for bind_part in bind.split(","):
            _from = int(bind_part.split("-")[0])
            _to = int(bind_part.split("-")[1])

            for i in range(_from, _to + 1):
                involved_threads.append(i)

    if bind.find("@") != -1 and bind.find(",") == -1:  ##numa balanced

        print("T:Numa balanced")
        first_socket = (
            bind.split("@")[0].strip("S0").strip(":")
        )  ##We know that other socket is identical
        _from_first = int(first_socket.split("-")[0])
        _to_first = int(first_socket.split("-")[1])

        for i in range(_from_first, _to_first + 1):
            if i > no_cores_per_socket - 1:
                i += no_cores_per_socket
            involved_threads.append(i)

        for i in range(_from_first, _to_first + 1):
            if i > no_cores_per_socket - 1:
                i += no_cores_per_socket
            involved_threads.append(
                i + no_cores_per_socket
            )  ##For second socket

    if bind.find("@") != -1 and bind.find(",") != -1:  ##numa compact
        print("T:Numa compact")
        first_socket = (
            bind.split("@")[0].strip("S0").strip(":")
        )  ##We know that other socket is identical
        first_comp = first_socket.split(",")[0]
        second_comp = first_socket.split(",")[1]

        _from_first = int(first_comp.split("-")[0])
        _to_first = int(first_comp.split("-")[1])

        for i in range(_from_first, _to_first + 1):
            if i > no_cores_per_socket - 1:
                i += no_cores_per_socket
            involved_threads.append(i)
        for i in range(_from_first, _to_first + 1):
            if i > no_cores_per_socket - 1:
                i += no_cores_per_socket
            involved_threads.append(
                i + no_cores_per_socket
            )  ##For second socket

        _from_first = int(second_comp.split("-")[0])
        _to_first = int(second_comp.split("-")[1])

        for i in range(_from_first, _to_first + 1):
            if i > no_cores_per_socket - 1:
                i += no_cores_per_socket
            involved_threads.append(i)
        for i in range(_from_first, _to_first + 1):
            if i > no_cores_per_socket - 1:
                i += no_cores_per_socket
            involved_threads.append(
                i + no_cores_per_socket
            )  ##For second socket

    print("len:", len(involved_threads))
    return involved_threads
    # return list(sorted(involved_threads))


def get_specific_observation(st, oid):

    observations = get_observations(st)
    db = get_mongo_database(st.name, st.mongodb_addr)["observations"]
    meta_observations = loads(dumps(db.find({"uid": oid})))[0]
    # print("Name:", st.name, "Observations:", observations)
    # print("meta_observations:", meta_observations)
    return meta_observations


def multinode_comparison(ev1, ev2, ev3, ev4):

    st1 = ev1[0]
    oid1 = ev1[1]

    st2 = ev2[0]
    oid2 = ev2[1]

    st3 = ev3[0]
    oid3 = ev3[1]

    st4 = ev4[0]
    oid4 = ev4[1]

    o1 = get_specific_observation(st1, oid1)
    o2 = get_specific_observation(st2, oid2)
    o3 = get_specific_observation(st3, oid3)
    o4 = get_specific_observation(st4, oid4)

    observation_standard.multinode(st1, o1, st2, o2, st3, o3, st4, o4)


def nested_search(keyword, node):
    for key, val in (
        node.items()
        if isinstance(node, dict)
        else enumerate(node)
        if isinstance(node, list)
        else []
    ):
        if key == keyword:
            yield val
        elif isinstance(val, list):
            for res in nested_search(keyword, val):
                yield res
        elif isinstance(val, dict):
            for res in nested_search(keyword, val):
                yield res


def get_monitoring_metrics(SuperTwin, metric_type):
    """

    Parameters
    ----------
    SuperTwin :
        Created or reconstructed supertwin object
    metric_type : String
        must be HWTelemetry for 'pmu' metrics or SWTelemetry for 'pcp' metrics.

    Returns
    -------
    metrics : dict
        {"metric_name" = '...', "type" = '...'}.

    """
    db = get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    twin_data = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))
    dtdl_twin = twin_data[0]["twin_description"]

    metrics = []
    for key, values in dtdl_twin.items():
        for metric in values["contents"]:
            if metric["@type"] == metric_type:
                metrics.append(
                    {
                        "metric_name": metric["SamplerName"],
                        "type": get_metric_type(metric["SamplerName"]),
                    }
                )
                if "pmu_group" in metric.keys():
                    metrics[-1]["pmu_group"] = metric["pmu_group"]
                if "PMUName" in metric.keys():
                    metrics[-1]["pmu_name"] = metric["PMUName"]

    return metrics


def get_metric_type(param_metric):

    _type = ""

    f_metric = ""
    if type(param_metric) == list:
        f_metric = param_metric[0]
    else:
        f_metric = param_metric

    if f_metric.find("percpu") != -1:
        _type = "percpu"
    elif f_metric.find("pernode") != -1:
        _type = "pernode"
    elif f_metric.find("kernel") != -1 and f_metric.find("kernel.all") == -1:
        _type = "kernel"
    elif f_metric.find("kernel.all") != -1:
        _type = "kernel.all"
    elif f_metric.find("numa") != -1:
        _type = "pernode"
    elif f_metric.find("mem") != -1:
        _type = "mem"
    elif f_metric.find("network.interface") != -1:
        _type = "network.interface"
    elif (
        f_metric.find("network") != -1
        and f_metric.find("network.interface") == -1
    ):  # Only top level metrics
        _type = "network.top"
    elif f_metric.find("disk.dev") != -1:
        _type = "disk.dev"
    elif f_metric.find("disk.all") != -1:
        _type = "disk.all"
    elif f_metric.find("UNC") != -1:
        _type = "uncore PMU"
    elif f_metric.find("OFFC") != -1:
        _type = "offcore PMU"
    elif f_metric.find("ENERGY") != -1:
        _type = "energy"
    elif (
        f_metric.find(":") != -1
        and f_metric.find("UNC") == -1
        and f_metric.find("OFFC") == -1
    ):
        _type = "core PMU"
    elif f_metric.find("proc.") != -1:
        _type = "proc"
    return _type



def generate_specific_benhmark_template(ssh_user,ssh_passwd,database_name, monitoring_url,roofline_url):
    input_file_path = "./use_cases/general_benchmark_template.sh"
    output_file_path = "./use_cases/" + database_name + "_benchmark_template.sh"
    
    ssh_user = ssh_user.replace("@localhost","@127.0.0.1")
    monitoring_url += "?orgId=1"
    roofline_url += "?orgId=1"
    
    if os.path.exists(output_file_path):
        try:
            os.remove(output_file_path)
        except OSError:
            print(f"Error deleting the existing file: {output_file_path}")

    try:
        with open(input_file_path, 'r') as input_file:
            with open(output_file_path, 'a') as output_file:
                for line in input_file:
                    if line.startswith("SSH_NAME"):
                        line = "SSH_NAME=" +"\""  +ssh_user +"\""  +" \n"
                    elif line.startswith("SSH_PASSWD"):
                        line = "SSH_PASSWD=" + "\"" +ssh_passwd +"\""  +"\n"
                    elif line.startswith("MONITORING_URL"):
                        line = "MONITORING_URL=" + "\"" + "http://localhost:3000" +monitoring_url +"\"" + "\n" 
                    elif line.startswith("ROOFLINE_URL"):
                        line = "ROOFLINE_URL=" + "\"" + "http://localhost:3000" +roofline_url +"\"" + "\n"
                    elif line.startswith("DATABASE_NAME"):
                        line = "DATABASE_NAME=" + "\""+database_name +"\"" + "\n"
                    output_file.write(line)
    
        # Add executable permissions to the output_file
        os.chmod(output_file_path, 0o777)
    except FileNotFoundError:
        print(f"File not found: {input_file_path}")
    except IOError:
        print("Error reading or writing the file.")
