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


def normalize_tag(SuperTwin, _tag, no_subtags):

    db = utils.get_influx_database(SuperTwin.influxdb_addr, SuperTwin.influxdb_name)
    db.switch_database(SuperTwin.influxdb_name)

    tagkey = _tag + "_0"
    
    query_string = 'SELECT * FROM perfevent_hwcounters_MEM_LOAD_RETIRED_L3_MISS_value where "tag"'+ "=" +  "'" + tagkey + "'"
    print("query_string:", query_string)
    result = db.query(query_string)

    print("result:", list(result)[0])

    intime = int(time.mktime(time.strptime("2022-11-02T02:52:09.223856Z", "%Y-%m-%dT%H:%M:%S.%fZ")))
    intime2 = int(time.mktime(time.strptime("2022-11-02T02:52:17.223856Z", "%Y-%m-%dT%H:%M:%S.%fZ")))

    ts1 = datetime.fromtimestamp(intime)
    ts2 = datetime.fromtimestamp(intime2)

    print("type(ts1):", str(ts1))
    print("type(ts2):", str(ts2))
    
    sts1 = str(ts1)
    sts1 = sts1.split(" ")[0] + "T" + sts1.split(" ")[1] + ".000000Z"
    print("sts1:", sts1)
    sts2 = str(ts2)
    sts2 = sts2.split(" ")[0] + "T" + sts2.split(" ")[1] + ".000000Z"
    print("sts2:", sts2)
    
    firstStampString = "2022-11-02T02:52:09.223856Z"
    lastStampString = "2022-11-02T02:52:29.223856Z"
    
    
    to_write1 = [{"measurement": "L1L9",
                 "tags": {"tag1": tagkey + "_normalized",},
                 "time": sts1,
                 #"time_precision": "ms",
                 "fields": {"_cpu0": 441}}]

    to_write2 = [{"measurement": "L1L9",
                 "tags": {"tag1": tagkey + "_normalized",},
                 "time": sts2,
                 #"time_precision": "ms",
                 "fields": {"_cpu0": 441}}]


    print("1:", db.write_points(to_write1))
    print("2:", db.write_points(to_write2))
    

    intime = int(time.mktime(time.strptime("2022-11-02T02:52:09.223856Z", "%Y-%m-%dT%H:%M:%S.%fZ")))
    ts = datetime.fromtimestamp(intime)

    print("intime:", intime, "ts:", ts)
