import sys


def generate(name, reader_lines, start, no_metrics):

    for i in range(1, no_metrics):

        writer = open(name + "_" + str(i) + ".conf", "w")
        for j in range(0, start):
            writer.write(reader_lines[j])
        for j in range(i):
            writer.write(reader_lines[start+j])

        writer.close()
        
if __name__ == "__main__":

    seed = sys.argv[1]
    name = sys.argv[2]
    reader = open(seed, "r")
    reader_lines = reader.readlines()

    start = 0
    no_metrics = 0
    for idx, line in enumerate(reader_lines):
        if(line.find("configured") != -1):
            start = idx + 1
            no_metrics = len(reader_lines) - start
            print("start:", start, "no_metrics:", no_metrics)

    #generate(name, reader_lines, start, no_metrics)
    for i in range(1,26):
        print("i:", i)
