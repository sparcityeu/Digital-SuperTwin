echo "Loding custom queries.."
 
function execute_remote_command() {
    local remote_user="$1"
    local remote_passwd="$2"
    local remote_command="$3"
    sshpass -p "$remote_passwd" ssh "$remote_user" "$remote_command"
}

function get_influx_data() {
    local query="$1"
    influx -execute "${query}" -database "${DATABASE_NAME}"
}

function mem_numa_alloc_hit_query() {
    QUERY="SELECT mean(\"_node0\") FROM mem_numa_alloc_hit WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") FROM mem_numa_alloc_hit WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}

function mem_numa_alloc_miss_query() {
    QUERY="SELECT mean(\"_node0\") FROM mem_numa_alloc_miss WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") FROM mem_numa_alloc_miss WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}

function kernel_pernode_cpu_idle_query() {
    QUERY="SELECT mean(\"_node0\") / 440 * -1 + 100 FROM kernel_pernode_cpu_idle WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")">> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    echo "" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") / 440 * -1 + 100 FROM kernel_pernode_cpu_idle WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}

function mem_numa_alloc_other_node_query() { 

    QUERY="SELECT mean(\"_node0\") FROM mem_numa_alloc_other_node WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    echo "" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") FROM mem_numa_alloc_other_node WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    
    echo "" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node0\") FROM mem_numa_alloc_local_node WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    
    echo "" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") FROM mem_numa_alloc_local_node WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}

function mem_numa_util_used_query(){

    QUERY="SELECT mean(\"_node0\")  / 1048576 FROM mem_numa_util_used WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\")  / 1048576 FROM mem_numa_util_used WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}

function mem_numa_util_free_query(){

     QUERY="SELECT mean(\"_node0\")  / 1048576 FROM mem_numa_util_free WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
     echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
     echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
     echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

     QUERY="SELECT mean(\"_node1\")  / 1048576 FROM mem_numa_util_free WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
     echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
     echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
     echo "$(get_influx_data "${QUERY}")" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}
