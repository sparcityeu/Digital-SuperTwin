import sys
import glob


def pretty_binding(ugly_binding):

    pretty_binding = ""

    fields = ugly_binding.split("|")

    for item in fields:
        pretty_binding += item
        pretty_binding += " "

    pretty_binding = pretty_binding[:-1]
    return pretty_binding
    

def parse_one_file(adcarm_res, fname):

    fields = fname.strip(".out").split("__")
    #print("fields:", fields)

    fields_keep = []
    for i in range(1, len(fields)):
        sep = fields[i].split("_")
        fields_keep.append(sep)

    thread = fields_keep[5][1]
    this_run_dict = {}
    
    for item in fields_keep:
        if(item[0] != "threads"):
            if(item[0] == "binding"):
                item[1] = pretty_binding(item[1])
            if(item[1] != '0' or item[1] != '1'):
                try:
                    this_run_dict[item[0]] = int(item[1])
                except:
                    this_run_dict[item[0]] = item[1]
            else:
                this_run_dict[item[0]] = bool(int(item[1]))
        
    reader = open(fname, "r")
    lines = reader.readlines()
    reader.close()

    for line in lines:
        fields = line.strip("\n").split(":")
        this_run_dict[fields[0]] = float(fields[1])

    adcarm_res["threads"][thread].append(this_run_dict)
    
    return adcarm_res


def get_threads(files):

    threads = []
    
    for item in files:
        fields = item.split("__")
        thread = fields[6].split("_")[1]
        if thread not in threads:
            threads.append(thread)
            
    return threads

def main():

    files = glob.glob("adCARM_RES/*.out")
    #print("files:", files)
    
    adcarm_res = {}
    adcarm_res["threads"] = {}
    
    threads = get_threads(files)

    for thread in threads:
        adcarm_res["threads"][thread] = []
    
    for fname in files:
        adcarm_res = parse_one_file(adcarm_res, fname)
        

    print("adcarm_res:", adcarm_res)

    return adcarm_res
    
if __name__ == "__main__":

    main()
    
