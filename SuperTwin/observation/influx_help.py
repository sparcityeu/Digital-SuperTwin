from influxdb import InfluxDBClient
from influxdb import SeriesHelper

import pandas as pd
from datetime import datetime
import time

import sys
sys.path.append("../")

import utils

def parse_nanodate(s):
  """
  parse date, ignore nanoseconds
  sample input: 2020-12-31T16:20:00.000000123Z
  --> 123ns will be ignored
  """
  if s[-1] == 'Z':
    # add explicit UTC timezone, to make strptime happy
    s += '+0000'
  return datetime.datetime.strptime(
    s[0:26]+s[29:], '%Y-%m-%dT%H:%M:%S.%fZ%z')

def query_string(metric, tagkey):
  
  return 'SELECT * FROM ' + metric + ' where "tag"'+ "=" +  "'" + tagkey + "'"

'''
def normalized(to_normal, normal): ##First observation first timestamp vs other o. first timestamp

  t0 = int(time.mktime(time.strptime(to_normal, "%Y-%m-%dT%H:%M:%S.%fZ")))
  t1 = int(time.mktime(time.strptime(normal, "%Y-%m-%dT%H:%M:%S.%fZ")))
  
  t0 -= (t1 - t0)
  t0 = datetime.fromtimestamp(t0)
  t0 = str(t0)
  
  return t0.split(" ")[0] + "T" + t0.split(" ")[1] + ".000000Z"
'''

def difference(to_normal, normal):
    
  t0 = int(time.mktime(time.strptime(to_normal, "%Y-%m-%dT%H:%M:%S.%fZ")))
  t1 = int(time.mktime(time.strptime(normal, "%Y-%m-%dT%H:%M:%S.%fZ")))

  return (t1 - t0) * -1
  
def normalized(to_normal, difference): ##Other observation, vs. itself

  t0 = int(time.mktime(time.strptime(to_normal, "%Y-%m-%dT%H:%M:%S.%fZ")))
  t0 -= difference
  t0 = datetime.fromtimestamp(t0)
  t0 = str(t0)
  
  return t0.split(" ")[0] + "T" + t0.split(" ")[1] + ".000000Z"

def normalize_tag(SuperTwin, _tag, no_subtags):

    db = utils.get_influx_database(SuperTwin.influxdb_addr, SuperTwin.influxdb_name)
    db.switch_database(SuperTwin.influxdb_name)

    ###Zeroth settings
    zero_tagkey = _tag + "_0"
    metrics = SuperTwin.observation_metrics
    metrics = [x.strip(" node") for x in metrics]
    metrics = ["perfevent_hwcounters_" + x.replace(":", "_") + "_value" for x in metrics]

    zero_query_string = query_string(metrics[0], zero_tagkey)
    result = db.query(zero_query_string)
    result = list(result)[0]
    compare_time = result[0]["time"]
    ###Zeroth settings

    
    ##Setback all sets
    for i in range(no_subtags):
        tagkey = _tag + "_" + str(i)
        for metric in metrics:
      
            qs = query_string(metric, tagkey)
            print("Normalize measurement time:", qs)
            result = list(db.query(qs))[0]
            my_difference = difference(result[0]['time'], compare_time)
            my_write = []
            ##Need to write ALL points
            
            for i in range(len(result)):
              time = ""
              if(tagkey.find("_0") != -1):
                n_time = result[i]['time']
              else:
                n_time = normalized(result[i]['time'], my_difference)
                
              to_write = {"measurement": metric,
                          "tags": {"tag": tagkey + "_normalized"},
                          "time": n_time}
              to_write["fields"] = {}
              for key in result[i].keys():
                if(key != "tag" and key != "time"):
                  to_write["fields"][key] = result[i][key]
                  my_write.append(to_write)
            db.write_points(my_write)
    
    #print("result:", result)
    #print("compare_time:", compare_time)
    
    '''
    intime = int(time.mktime(time.strptime("2022-11-02T02:52:09.223856Z", "%Y-%m-%dT%H:%M:%S.%fZ")))

    
    ts1 = datetime.fromtimestamp(intime)
    print("type(ts1):", str(ts1))
    

    
    #sts1 = str(ts1)
    #sts1 = sts1.split(" ")[0] + "T" + sts1.split(" ")[1] + ".000000Z"
    #print("sts1:", sts1)
    

    ##Loop here
    firstStampString = "2022-11-02T02:52:09.223856Z"
    
    to_write = [{"measurement": "L1L10",
                 "tags": {"tag1": "sa" + "_normalized",},
                 "time": "2022-11-02T14:30:05.000000Z",
                 #"time_precision": "ms",
                 "fields": {"_cpu0": 441}}]

    db.write_points(to_write)
    '''
