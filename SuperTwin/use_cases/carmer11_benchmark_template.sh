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
 
BENCHMARK_SUITE="merge_spmv"
INFLUXDB_HOST="localhost"
INFLUXDB_PORT="8086"

## DONT MODIFY!! THESE ARE ALTERED BY UTILS.PY
SSH_NAME="zemor@127.0.0.1" 
SSH_PASSWD="rinc2b7cf1"

DATABASE_NAME="carmer11"

MONITORING_URL="http://localhost:3000/d/ec3d8c93-1d26-438f-a3b2-54e10307ef53/pmus-carmer11-monitor-8b8c10b0-8a9f-4b5d-add6-224a87851543?orgId=1"
MONITORING_DASHBOARD_URL=""
 
ROOFLINE_URL="http://localhost:3000/d/bd5add05-ade4-4509-9921-056ab13d3d56/pmus-carmer11-roofline-3e055643-96a4-4a90-a99f-138d2a337032?orgId=1"
ROOFLINE_DASHBOARD_URL="" 
## end DONT MODIFY!! 
echo "entered database name :$DATABASE_NAME"


## LOAD CUSTOM QUERIES  
source remote_configuration.sh
 
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
BENCHMARK_PROGRAMS["${BENCHMARK_ORDERED_SPMV}"]="" # --mtx=matrixes/GAP-road/GAP-road.mtx
BENCHMARK_PROGRAMS["${BENCHMARK_UNORDERED_SPMV}"]="cd ${BENCHMARK_SUITE}; . add_dynamic_libs.sh "${SSH_PASSWD}"; ./cpu_spmv " # --mtx=matrixes/GAP-road/GAP-road.mtx ## stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 10s
BENCHMARK_PROGRAMS["${BENCHMARK_BFS}"]=""

bench_start_time=$(date +%s)
for bench in "${BENCHMARK_NAMES_LIST[@]}"
do  
	if [[ "${BENCHMARK_PROGRAMS[$bench]}" == "" ]];then
		echo "EMPTY BENCHMARK SKIPPED !"
		continue
	fi
  
	# BENCHMARK EXECUTION PART
	 
	echo "looking for matrix names \*.mtx"
	result="$(get_suit_matrix_names)"  # Call the function and store the result in 'result' variable.
	echo "$result"

	for MATRIX_NAME in $result
	do
		echo "found -> $MATRIX_NAME"

		mkdir -p ${BENCHMARK_RESULTS}/${bench}/$MATRIX_NAME/

		echo "executing benchmark ${bench} program:${BENCHMARK_PROGRAMS[$bench]} --mtx=\"${MATRIX_NAME}\""

		start_time=$(date +%s) ## BEGIN MEASURING PER MATRICES
		bench_result=$(execute_remote_command ${SSH_NAME} ${SSH_PASSWD} "${BENCHMARK_PROGRAMS[$bench]} --mtx=\"${MATRIX_NAME}\"")
		end_time=$(date +%s) 

		echo "$bench_result"
		seconds=$((end_time - start_time)) ## seconds
		echo -e "Benchmark ${bench} took: ${seconds} seconds. start:${start_time} end:${end_time}\n"

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
				echo ${QUERY} >> ${BENCHMARK_RESULTS}/${bench}/$MATRIX_NAME/queries.txt  
				echo "$(get_influx_data "$QUERY")" >> ${BENCHMARK_RESULTS}/${bench}//$MATRIX_NAME/${measurement}_data 
			fi
		done
		set +f  # Re-enable globbing   
		echo -e "------------------------\n" >> ${BENCHMARK_RESULTS}/${bench}/$MATRIX_NAME/queries.txt   
		
		echo "Benchmark ${bench} execution dashboard links added... from: bench_start_time to bench_end_time "
		echo "${MONITORING_DASHBOARD_URL}" >> ${BENCHMARK_RESULTS}/${bench}/$MATRIX_NAME/dashboard_url.txt   
		echo "${ROOFLINE_DASHBOARD_URL}" >> ${BENCHMARK_RESULTS}/${bench}/$MATRIX_NAME/dashboard_url.txt   
		echo "------------------------"
	done
 
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
 