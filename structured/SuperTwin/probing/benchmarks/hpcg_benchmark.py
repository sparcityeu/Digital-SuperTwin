import os
import sys
import glob
import pprint

def parse_one(res, _file):

    reader = open(_file, "r")
    lines = reader.readlines()
    reader.close()

    thread = -1
    
    for line in lines:
        if(line.find("Machine Summary::Threads per processes") != -1):
            thread = int(line.strip("\n").split("=")[1])
        if(line.find("GFLOP/s Summary::Raw DDOT") != -1):
            gfps = float(line.strip("\n").split("=")[1])
            res["ddot"][thread] = gfps
        if(line.find("GFLOP/s Summary::Raw WAXPBY") != -1):
            gfps = float(line.strip("\n").split("=")[1])
            res["waxpby"][thread] = gfps
        if(line.find("GFLOP/s Summary::Raw SpMV") != -1):
            gfps = float(line.strip("\n").split("=")[1])
            res["spmv"][thread] = gfps

    return res

def parse():

    res = {}
    res["spmv"] = {}
    res["ddot"] = {}
    res["waxpby"] = {}
    
    files = glob.glob("*.txt")
    
    for _file in files:
        res = parse_one(res, _file)


    pprint.pprint(res)


if __name__ == "__main__":

    
    parse()
