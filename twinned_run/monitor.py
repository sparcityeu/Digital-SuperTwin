import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
import create_dt
import generate_dt
import remote_probe
import initiate
import instantiate







def main():

    hostName, hostIP, hostProbFile = remote_probe.main()
    #print("in m: ", "hostname:", hostName, "hostIP:", hostIP, "hostProbFile:", hostProbFile)

    monitoringMetricsConf = input("Monitoring metrics configuration: ")
    monitorPID = initiate.main(hostName, hostIP, hostProbFile, monitoringMetricsConf)
    print("A daemon is sampling", hostName, "with PID", monitorPID)


if __name__ == "__main__":

    main()
