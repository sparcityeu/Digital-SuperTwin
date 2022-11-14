import collections
import sys
import subprocess
from subprocess import Popen, PIPE
import shlex
import time

from flask import Flask, jsonify, make_response, request
from pymongo import MongoClient
from flask_cors import CORS

from bson.objectid import ObjectId
from bson import json_util
from bson.json_util import dumps
from bson.json_util import loads

sys.path.append("../../probing")
sys.path.append("../../probing/benchmarks")
sys.path.append("../../observation")
sys.path.append("../../twin_description")
sys.path.append("../../sampling")
sys.path.append("../../dashboards")
import supertwin
#from supertwin import callSuperTwin
import utils
import remote_probe
import detect_utils
import generate_dt
import sampling
import stream_benchmark
import hpcg_benchmark
import adcarm_benchmark
import observation
#import roofline_dashboard

import static_data


app = Flask(__name__)
db_client = MongoClient('host.docker.internal', 27017)
CORS(app)



@app.route('/api/setDB', methods=['GET', 'POST'])
def setDB():
    try:
        global collection
        global obs_collection
        db = db_client[twin.name]

        collection = db['twin']
        obs_collection = db['observations']
        response = dumps((collection.find({})), default=json_util.default)
        a = loads(response)

        ids = []

        for doc in a:
            doc['_id'] = str(ObjectId(doc['_id']))
            ids.append(doc['_id'])

        return make_response(jsonify({"unique_supertwins" : ids}), 200)

    except Exception as error:
        return make_response(jsonify({'error': error}), 400)

@app.route('/api/startSuperTwin', methods=['POST'])
def startSuperTwin():
    time.sleep(1)
    try:
        global twin

        data = request.get_json()
        info = data['registration']

        addr = info["remoteAddress"]["remoteAddress"]
        user_name = info["username"]["username"]
        password = info["password"]["password"]
        reader = open("supertwin.state", "r")
        lines = reader.readlines()
        reader.close()
        
        twin = supertwin.SuperTwin(addr, user_name, password)

        return make_response(jsonify({'OK': "OK"}), 200)

    except Exception as error:
        return make_response(jsonify({'error': error}), 400)


@app.route('/api/getMetrics/monitoring', methods=['GET'])
def getMonitoringMetrics():
    time.sleep(1)
    try:
        #replace with twin.ObjectID
        twin_data = loads(dumps((collection.find({"_id": ObjectId(twin.mongodb_id)})), default=json_util.default))
        dtdl_twin = twin_data[0]['twin_description']

        raw_metrics = []
        thread_count_flag = False
        core_count_flag = False
        L1D_count_flag = False
        L2_count_flag = False
        L3_count_flag = False
        bank_count_flag = False

        for key, values in dtdl_twin.items():
            if values['@id'].find("thread") != -1:
                if thread_count_flag == False:
                    thread_count_flag = True
                    for metric in values['contents']:

                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])

            elif values['@id'].find("core") != -1:
                if core_count_flag == False:
                    core_count_flag = True
                    for metric in values['contents']:

                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])



            elif values['@id'].find("L1D") != -1:
                if L1D_count_flag == False:
                    L1D_count_flag = True
                    for metric in values['contents']:
                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])


            elif values['@id'].find("L2") != -1:
                if L2_count_flag == False:
                    L2_count_flag = True
                    for metric in values['contents']:
                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])

            elif values['@id'].find("L3") != -1:
                if L3_count_flag == False:
                    L3_count_flag = True
                    for metric in values['contents']:
                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])


            elif values['@id'].find("bank") != -1:
                if bank_count_flag == False:
                    bank_count_flag = True
                    for metric in values['contents']:

                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])

            else:
                for metric in values['contents']:

                        if metric['@type'] == "SWTelemetry":
                            raw_metrics.append(metric['SamplerName'])
        

        metrics = []

        for metric in raw_metrics:
            metric_type = get_type(metric)
            metric_with_type = {"metric": metric, "type": metric_type}
            metrics.append(metric_with_type)


        return make_response(jsonify({"monitoringMetrics":metrics}), 200)

    except Exception as error:
        return make_response(jsonify({'error': error}), 400)



@app.route('/api/getMetrics/experiment', methods=['GET'])
def getExperimentalMetrics():
    time.sleep(1)
    try:
        #replace with twin.ObjectID
        twin_data = loads(dumps((collection.find({"_id": ObjectId(twin.mongodb_id)})), default=json_util.default))
        dtdl_twin = twin_data[0]['twin_description']

        raw_metrics = []
        thread_count_flag = False
        core_count_flag = False
        L1D_count_flag = False
        L2_count_flag = False
        L3_count_flag = False
        bank_count_flag = False

        for key, values in dtdl_twin.items():
            if values['@id'].find("thread") != -1:
                if thread_count_flag == False:
                    thread_count_flag = True
                    for metric in values['contents']:

                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])

            elif values['@id'].find("core") != -1:
                if core_count_flag == False:
                    core_count_flag = True
                    for metric in values['contents']:

                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])



            elif values['@id'].find("L1D") != -1:
                if L1D_count_flag == False:
                    L1D_count_flag = True
                    for metric in values['contents']:
                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])


            elif values['@id'].find("L2") != -1:
                if L2_count_flag == False:
                    L2_count_flag = True
                    for metric in values['contents']:
                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])

            elif values['@id'].find("L3") != -1:
                if L3_count_flag == False:
                    L3_count_flag = True
                    for metric in values['contents']:
                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])


            elif values['@id'].find("bank") != -1:
                if bank_count_flag == False:
                    bank_count_flag = True
                    for metric in values['contents']:

                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])

            else:
                for metric in values['contents']:

                        if metric['@type'] == "HWTelemetry":
                            raw_metrics.append(metric['PMUName'])
        metrics = []

        for metric in raw_metrics:
            metric_type = get_type(metric)
            metric_with_type = {"metric": metric, "type": metric_type}
            metrics.append(metric_with_type)

        return make_response(jsonify({"experimentMetrics":metrics}), 200)

    except Exception as error:
        return make_response(jsonify({'error': error}), 400)



@app.route('/api/appendMetrics/monitoring', methods=['POST'])
def appendMonitoringMetrics():
    time.sleep(1)
    try:
        
        data = request.get_json()
        metric_list = data['monitoringMetrics']
        '''
        file_object = open('monitor_metrics.txt', 'a')
        file_object.write("\n##USER METRICS##\n")


        x = 0
        for metric in metric_list:
            file_object.write(metric['metric'])
            if x != len(metric_list) -1:
                file_object.write("\n")


        file_object.close()
        '''
        print(metric_list)
        for _d in metric_list:
            twin.monitor_metrics.append(_d["metric"])
        twin.update_twin_document__assert_new_monitor_pid()
        twin.update_twin_document__add_monitoring_dashboard("http://host.docker.internal/d/wa83tmD4z/dolap-monitor_1")
        return "OK"
    except Exception as error:
        return make_response(jsonify({'error': error}), 400)
    


@app.route('/api/appendMetrics/experiment', methods=['POST'])
def appendExperimentalMetrics():
    time.sleep(1)
    try:
        data = request.get_json()
        metric_list = data['experimentMetrics']
        metric_list = [x['metric'] for x in metric_list]
        print("metric_list:", metric_list)
                
        #file_object = open('perfevent.conf', 'a')
        twin.observation_metrics = metric_list
        twin.reconfigure_perfevent()

        return "OK"

    except Exception as error:
        return make_response(jsonify({'error': error}), 400)


@app.route('/api/getMonitoringStatus', methods=['GET'])
def getMonitoringStatus():
    time.sleep(1)
    try:
        p0_command = 'ps aux | grep pcp2influxdb'

        cmd_output = output_lines(p0_command)
        cmd_output = cmd_output[1].split()
        status = cmd_output[1]

        monitor_info ={
            "address":twin.addr,
            "mongodb": twin.mongodb_id,
            "grafana": twin.grafana_token,
            "user": twin.SSHuser,
            "uid": twin.uid,
            "pid":status,
        }
        #time.sleep(1)
        return make_response(monitor_info, 200)
    except Exception as error:
        return make_response(jsonify({'error': error}), 400)


@app.route('/api/getDashboards', methods=['GET'])
def getDashboards():
    time.sleep(1)
    try:
        dashborads = []

        twin_data = loads(dumps((collection.find({"_id": ObjectId(twin.mongodb_id)})), default=json_util.default))
        
        monitoring_dashboard_link = twin_data[0]['roofline_dashboard']
        roofline_dashboard_name = twin.name +" roofline dashboard"

        roofline_dashboard_link = twin_data[0]['monitoring_dashboard']
        monitoring_dashboard_name = twin.name +" monitoring dashboard"

                
        dashborads.append({"dashboard_name":roofline_dashboard_name, "dashboard_link": roofline_dashboard_link})
        dashborads.append({"dashboard_name":monitoring_dashboard_name, "dashboard_link": monitoring_dashboard_link})

        #observationCollection = db_client['observation']
        observation_data = loads(dumps((obs_collection.find()), default=json_util.default))
        for obs in observation_data:
            observation_name = twin.name + "_" +str(obs['_id'])
            observation_link = obs['report']
            dashborads.append({"dashboard_name":observation_name, "dashboard_link": observation_link})

        #time.sleep(1)
        
        return make_response(jsonify({"dashboards":dashborads}), 200)


    except Exception as error:
        return make_response(jsonify({'error': error}), 400)


@app.route('/api/runExperiment', methods=['POST'])
def sendCommands():
    time.sleep(1)
    try:
        data = request.get_json()
        print("data:", data)
        cmd = data['cmd']
        cmd = cmd.split("\n")
        affinity = data['affinity']
        path = data['path']

        print(cmd, affinity, path)
        
        twin.execute_observation_batch_parameters(path, affinity, cmd)
        
        return "OK"
    except Exception as error:
        return make_response(jsonify({'error': error}), 400)


def get_type(param_metric):
    
    _type = ''

    f_metric = ''
    if(type(param_metric) == list):
        f_metric = param_metric[0]
    else:
        f_metric = param_metric


    if(f_metric.find('percpu') != -1):                                                                
        _type = 'percpu'                                                                            
    elif(f_metric.find('pernode') != -1):                                                             
        _type = 'pernode'                                                                           
    elif(f_metric.find('kernel') != -1 and f_metric.find("kernel.all") == -1):                                                              
        _type = 'kernel'
    elif(f_metric.find('kernel.all') != -1):
        _type = 'kernel.all'
    elif(f_metric.find('numa') != -1):                                                                
        _type = 'pernode'                                                                           
    elif(f_metric.find('mem') != -1):                                                                 
        _type = 'mem'                                                                               
    elif(f_metric.find('network.interface') != -1):                                                   
        _type = 'network.interface'   
    elif(f_metric.find('network') != -1 and f_metric.find("network.interface") == -1): #Only top level metrics
        _type = 'network.top'    
    elif(f_metric.find('disk.dev') != -1):
        _type = 'disk.dev'
    elif(f_metric.find('disk.all') != -1):
        _type = 'disk.all'
    elif(f_metric.find('UNC') != -1):                                                      
        _type = 'uncore PMU'
    elif(f_metric.find('OFFC') != -1):                                                      
        _type = 'offcore PMU'                                                                            
    elif(f_metric.find('ENERGY') != -1):                                                              
        _type = 'energy'                                                                           
    elif(f_metric.find(':') != -1 and f_metric.find('UNC') == -1 and f_metric.find('OFFC') == -1):                                               
        _type = 'core PMU'
    elif(f_metric.find('proc.') != -1):
        _type = 'proc'
    return _type


def output_lines(cmdline):
    """Run a shell command and returns the output as lines."""
    proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE,
                            universal_newlines=True)
    stdout = proc.communicate()[0]
    return stdout.splitlines()
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=False)
