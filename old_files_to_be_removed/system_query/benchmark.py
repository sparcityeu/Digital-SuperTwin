import detect_utils
import subprocess
import pprint

mt_scale = {}
mt_scale["Copy:"] = {}
mt_scale["Scale:"] = {}
mt_scale["Add:"] = {}
mt_scale["Triad:"] = {}

def get_ridge_point(bw, flop):

    ridge = flop / bw
    print("ridge:", ridge)
    
    return ridge

def peak_theoretical_flop(no_procs, core_per_proc, clock_speed, no_fma_units, max_vector_size):

    peak_gflop_o_s = no_procs * core_per_proc * clock_speed * (2 * no_fma_units) * (max_vector_size / 64)
    #print("Peak flop/s:", peak_flop_o_s)
    print("Peak gflop/s:", peak_gflop_o_s)

    return peak_gflop_o_s 

def parse_one_stream_res(stream_res, threads):

    global mt_scale
    
    
    fname = "STREAM/" + "t" + str(threads) + ".txt"
    reader = open(fname, "r")
    lines = reader.readlines()
    reader.close()

    run_max = 0.0
    
    
    for line in lines:
        if(line.find("Copy") != -1 or
           line.find("Scale") != -1 or
           line.find("Add") != -1 or
           line.find("Triad") != -1):

            fields = line.split(" ")
            fields = [x for x in fields if x != ""]
            res = float(fields[1])

            #print("Thread: ", threads, fields[0], fields[1])
            mt_scale[fields[0]][threads] = fields[1]
            
            if(res > run_max):
                run_max = res

    stream_res[str(threads)] = run_max
    pprint.pprint(mt_scale)
    return stream_res

def start_bench():

    detect_utils.cmd("cd STREAM;sh clean.sh")
    detect_utils.cmd("cd STREAM;sh bench.sh")


def get_roof_values(max_bw, peak_g_flop, ridge_point):

    
    #AIs = sorted([0.0625, 0.125, 0.25, 0.50, 1, 2, 4, 8, 16, 32, ridge_point])
    AIs = []
    for i in range(-6, 11):
        AIs.append(2**i)
    AIs.append(ridge_point)
    AIs = sorted(AIs)
    print("AIs:", AIs)
    Y = []
    
    for AI in AIs:
        print("AI:", AI, "max_bw*AI:", max_bw*AI, "peak_g_flop:", peak_g_flop)
        Y.append(round(min((max_bw * AI), peak_g_flop), 2))

    print("##############")
    #print("Y:", Y)
    #print("AIs:", AIs)
    for i in range(len(Y)):
        print(AIs[i], "->", Y[i])
    print("##############")
        

def main():

    #start_bench()
    
    stream_res = {}
    stream_res = parse_one_stream_res(stream_res, 1)
    stream_res = parse_one_stream_res(stream_res, 2)
    stream_res = parse_one_stream_res(stream_res, 4)
    stream_res = parse_one_stream_res(stream_res, 8)
    stream_res = parse_one_stream_res(stream_res, 16)
    stream_res = parse_one_stream_res(stream_res, 22)
    stream_res = parse_one_stream_res(stream_res, 32)
    stream_res = parse_one_stream_res(stream_res, 44)
    stream_res = parse_one_stream_res(stream_res, 64)
    stream_res = parse_one_stream_res(stream_res, 88)
    

    #print(stream_res)
    max_bw = 0
    for key in stream_res:
        if(stream_res[key] > max_bw):
            max_bw = stream_res[key]

    max_bw /= 1000
    print("max_bw:", max_bw)
    
    
    peak_g_flop = peak_theoretical_flop(44, 2, 2.1, 2, 512)
    ridge_point = round(get_ridge_point(max_bw, peak_g_flop), 1)
    get_roof_values(max_bw, peak_g_flop, ridge_point)

if __name__ == "__main__":

    main()

    
