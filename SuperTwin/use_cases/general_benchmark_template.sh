#!/bin/bash

if  [[ "$1" == "--help" ]]; then
    echo "Usage: $(basename "$0") [OPTIONS] [QUERIES]"
    echo ""
    echo "This template is used for automatic benchmarking"
    echo "Takes database name, a program to execute, and some additional queries that you'd like to run"
    echo "Execeutes the program and dumps influxdb measurements for given database to benchmark_results/<benchmark_name>"
    echo "Allows you to see what changed during the 'program' execution"
    echo ""
    echo "Options:"
    echo "  --help     Display this help message."
    echo "  <database_name>"
    echo "  <program> to be executed"
    
    echo "QUERIES:"
    echo "  general_benchmark_template.sh "query1" "query2" "query3""
    echo '  general_benchmark_template.sh "SELECT * FROM XXX WHERE time >= now() - (seconds)s" ...'
    exit 0
fi

INFLUXDB_HOST="localhost"
INFLUXDB_PORT="8086"

## DONT MODIFY!! THESE ARE ALTERED BY UTILS.PY
SSH_NAME=""
SSH_PASSWD=""

DATABASE_NAME="" # "user-AS-4023S-TRT" 

MONITORING_URL="" # http://localhost:3000/d/wYVoa13Vz/pmus-rt7-laptop-vivo-monitor-438a34b4-4162-4127-8b9f-8122207fd642?orgId=1&from=1690569527000&to=1690569827000
MONITORING_DASHBOARD_URL=""
 
ROOFLINE_URL="" # http://localhost:3000/d/wYVoa13Vz/pmus-rt7-laptop-vivo-monitor-438a34b4-4162-4127-8b9f-8122207fd642?orgId=1&from=1690569527000&to=1690569827000
ROOFLINE_DASHBOARD_URL="" 
## end DONT MODIFY!! 


echo "entered database name :$DATABASE_NAME"


## LOAD CUSTOM QUERIES 
source custom_queries.sh
 
# benchmark names
BENCHMARK_ORDERED_SPMV="SPMV_ordered"
BENCHMARK_UNORDERED_SPMV="SPMV_unordered"
BENCHMARK_BFS="BFS"


#create folders
BENCHMARK_RESULTS="benchmark_results/${DATABASE_NAME}"

ORDERED_SPMV="${BENCHMARK_RESULTS}/${BENCHMARK_ORDERED_SPMV}/"
UNORDERED_SPMV="${BENCHMARK_RESULTS}/${BENCHMARK_UNORDERED_SPMV}/"
BFS="${BENCHMARK_RESULTS}/${BENCHMARK_BFS}/"

mkdir -p ${BENCHMARK_RESULTS}
mkdir -p ${ORDERED_SPMV}
mkdir -p ${UNORDERED_SPMV}
mkdir -p ${BFS}


BENCHMARK_NAMES_LIST=("${BENCHMARK_ORDERED_SPMV}" "${BENCHMARK_UNORDERED_SPMV}" "${BENCHMARK_BFS}")

# Define the associative array to map benchmarks to programs
declare -A BENCHMARK_PROGRAMS
BENCHMARK_PROGRAMS["${BENCHMARK_ORDERED_SPMV}"]="sleep 5"
BENCHMARK_PROGRAMS["${BENCHMARK_UNORDERED_SPMV}"]="stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 10s"
BENCHMARK_PROGRAMS["${BENCHMARK_BFS}"]="sleep 5"


bench_start_time=$(date +%s)
for bench in "${BENCHMARK_NAMES_LIST[@]}"
do  
	# BENCHMARK EXECUTION PART
	start_time=$(date +%s)
	echo "executing benchmark ${bench} program:${BENCHMARK_PROGRAMS[$bench]}"
	execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "${BENCHMARK_PROGRAMS[$bench]}" 
	end_time=$(date +%s) 
	seconds=$((end_time - start_time)) ## seconds
	echo -e "Benchmark took: ${seconds} seconds. start:${start_time} end:${end_time}\n"
	
	EXTRA_SECONDS=5 ## take into account the execution time of following codes
    seconds=$((seconds + EXTRA_SECONDS))
    
    MONITORING_DASHBOARD_URL="${MONITORING_URL}&from=${start_time}000&to=${end_time}000"  
    ROOFLINE_DASHBOARD_URL="${ROOFLINE_URL}&from=${start_time}000&to=${end_time}000"  
     

	### REPORTING PART 
    set -f  # Disable globbing
    ## DUMPS DEFAULT MEASUREMENT RESULTS
	QUERY="SHOW MEASUREMENTS"
	measurements_result="$(get_influx_data "$QUERY" | tr ' ' '\n' | tail -n +5)"
    #echo "$measurements_result" 
	for measurement in $measurements_result   #  <-- Note: Added "" quotes.
	do  
		# maybe repeat this part in python for each queries?
		#echo "$measurement"
		QUERY="SELECT mean(*) FROM ${measurement} WHERE time >= now() - ${seconds}s GROUP BY time(1s) fill(null);"
		
		if [[ "$measurement" == "mem_numa_alloc_hit" ]]; then
    		$(mem_numa_alloc_hit_query)
  		
  		elif [[ "$measurement" == "mem_numa_alloc_miss" ]]; then
      		$(mem_numa_alloc_miss_query)

    	elif [[ "$measurement" == "kernel_pernode_cpu_idle" ]]; then
    		$(kernel_pernode_cpu_idle_query)
    		
      	elif [[ "$measurement" == "mem_numa_alloc_other_node" ]]; then
      		$(mem_numa_alloc_other_node_query)
        
      	elif [[ "$measurement" == "mem_numa_util_used" ]]; then
      		$(mem_numa_util_used_query)
      		
      	elif [[ "$measurement" == "mem_numa_util_used" ]]; then
      		$(mem_numa_util_free_query)
        else    	
    		echo ${QUERY} >> ${BENCHMARK_RESULTS}/${bench}/queries.txt  
    		echo "$(get_influx_data "$QUERY")" >> ${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data 
		fi
	done
	set +f  # Re-enable globbing   
	echo -e "------------------------\n" >> ${BENCHMARK_RESULTS}/${bench}/queries.txt   
	
	echo "Benchmark ${bench} execution dashboard links added... from: bench_start_time to bench_end_time "
	echo "${MONITORING_DASHBOARD_URL}" >> ${BENCHMARK_RESULTS}/${bench}/dashboard_url.txt   
	echo "${ROOFLINE_DASHBOARD_URL}" >> ${BENCHMARK_RESULTS}/${bench}/dashboard_url.txt   
	
	
	echo "------------------------"
	
done
bench_end_time=$(date +%s) 

MONITORING_DASHBOARD_URL="${MONITORING_URL}&from=${bench_start_time}000&to=${bench_end_time}000"  # start time - end time for all benchmarks
ROOFLINE_DASHBOARD_URL="${ROOFLINE_URL}&from=${bench_start_time}000&to=${bench_end_time}000" # start time - end time for all benchmarks

echo "overall monitoring: ${MONITORING_DASHBOARD_URL}" >> ${BENCHMARK_RESULTS}/dashboard_url.txt   
echo "overall roofline-pmu: ${ROOFLINE_DASHBOARD_URL}" >> ${BENCHMARK_RESULTS}/dashboard_url.txt   


echo -e "Benchmarks took: $((bench_end_time - bench_start_time)) sec."

## OPEN DASHBOARD FOR STATIC DATA
xdg-open "${MONITORING_DASHBOARD_URL}"
xdg-open "${ROOFLINE_DASHBOARD_URL}"
 