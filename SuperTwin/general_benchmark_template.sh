#!/bin/bash

if  [[ $# -eq 0 ]] || [[ "$1" == "--help" ]]; then
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
DATABASE_NAME="$1" #"user-AS-4023S-TRT" 
echo "entered database name :$DATABASE_NAME"

function get_influx_data() {
    local query="$1"
    influx -execute "${query}" -database "${DATABASE_NAME}"
}

# benchmark names
BENCHMARK_ORDERED_SPMV="SPMV_ordered"
BENCHMARK_UNORDERED_SPMV="SPMV_unordered"
BENCHMARK_BFS="BFS"


#create folders
BENCHMARK_RESULTS="benchmark_results"
ORDERED_SPMV=${BENCHMARK_RESULTS}/"${BENCHMARK_ORDERED_SPMV}"/
UMORDERED_SPMV=${BENCHMARK_RESULTS}/"${BENCHMARK_UNORDERED_SPMV}"/
BFS=${BENCHMARK_RESULTS}/"${BENCHMARK_BFS}/"

mkdir -p ${BENCHMARK_RESULTS}
mkdir -p ${ORDERED_SPMV}
mkdir -p ${UMORDERED_SPMV}
mkdir -p ${BFS}


BENCHMARK_NAMES_LIST=("${BENCHMARK_ORDERED_SPMV}" "${BENCHMARK_UNORDERED_SPMV}" "${BENCHMARK_BFS}")

# Define the associative array to map benchmarks to programs
declare -A BENCHMARK_PROGRAMS
BENCHMARK_PROGRAMS["${BENCHMARK_ORDERED_SPMV}"]="sleep 2"
BENCHMARK_PROGRAMS["${BENCHMARK_UNORDERED_SPMV}"]="sleep 5"
BENCHMARK_PROGRAMS["${BENCHMARK_BFS}"]="sleep 10"


for bench in "${BENCHMARK_NAMES_LIST[@]}"
do  
	# BENCHMARK EXECUTION PART
	start_time=$(date +%s)
	echo "executing benchmark ${bench} program ${BENCHMARK_PROGRAMS[$bench]}"
	${BENCHMARK_PROGRAMS[$bench]} 
	end_time=$(date +%s)
	seconds=$((end_time - start_time)) ## seconds
	echo -e "Benchmark took: ${seconds} seconds.\n"
	
	EXTRA_SECONDS=5 ## take into account the execution time of following codes
    seconds=$((seconds + EXTRA_SECONDS))
	echo "------------------------"

	### REPORTING PART 
    set -f  # Disable globbing
    for param in "${@:2}"; do
        QUERY=$(sed -E "s/now\(\) *- *[0-9a-zA-Z]*m/now() - ${seconds}s/" <<< "${param}")
        echo "${QUERY}"
		echo "${QUERY}" >> ${BENCHMARK_RESULTS}/${bench}/queries.txt  
		echo "$(get_influx_data "$QUERY")" >> ${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data 
    done
    exit 0
    
	QUERY="SHOW MEASUREMENTS"
	measurements_result="$(get_influx_data "$QUERY" | tr ' ' '\n' | tail -n +5)"
    echo "$measurements_result"
    exit 0
	for measurement in $measurements_result   #  <-- Note: Added "" quotes.
	do  
		# maybe repeat this part in python for each queries?
		#echo "$measurement"
		QUERY="SELECT * FROM ${measurement} WHERE time >= now() - ${seconds}s"
		echo ${QUERY} >> ${BENCHMARK_RESULTS}/${bench}/queries.txt  
		echo "$(get_influx_data "$QUERY")" >> ${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data 
	done
	set +f  # Re-enable globbing   
	echo -e "------------------------\n" >> ${BENCHMARK_RESULTS}/${bench}/queries.txt   
done
  
