import os
import sys
import pprint
import parse_evtinfo



def main():

    reader = open("perfevent.conf", "r")
    conf_prelines = reader.readlines()
    reader.close()

    PMUs = parse_evtinfo.main()
    #pprint.pprint(PMUs)
    keys = list(PMUs.keys())

        
    for key, value in PMUs[key][events].items():
        if(key != "perf"):
            for item in value:
                conf_prelines.append(item[0] + "\n")


    for i in range(200):
        print(conf_prelines[i])

    writer = open("reconfigured.conf", "w")
    for item in conf_prelines:
        writer.write(item)

    pprint.pprint(PMUs["skx"])
    print("skx:", len(PMUs["skx"]))

if __name__ == "__main__":

    main()
