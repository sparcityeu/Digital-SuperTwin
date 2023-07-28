echo "Loding custom queries.."
 
function get_influx_data() {
    local query="$1"
    influx -execute "${query}" -database "${DATABASE_NAME}"
}

function mem_numa_alloc_hit_query() {
    QUERY="SELECT mean(\"_node0\") FROM mem_numa_alloc_hit WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    $(get_influx_data "${QUERY}") >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") FROM mem_numa_alloc_hit WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    $(get_influx_data "${QUERY}") >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}

function mem_numa_alloc_miss_query() {
    QUERY="SELECT mean(\"_node0\") FROM mem_numa_alloc_miss WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    $(get_influx_data "${QUERY}") >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT mean(\"_node1\") FROM mem_numa_alloc_miss WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    $(get_influx_data "${QUERY}") >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}



function kernel_pernode_cpu_idle_query() {
    QUERY="SELECT (mean(\"_node0\") / 440 * -1 + 100) FROM kernel_pernode_cpu_idle WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node0" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    $(get_influx_data "${QUERY}") >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    echo "" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"

    QUERY="SELECT (mean(\"_node1\") / 440 * -1 + 100) FROM kernel_pernode_cpu_idle WHERE time >= now() - ${seconds}s and time <= now() GROUP BY time(1s) fill(null);"
    echo "$QUERY" >> "${BENCHMARK_RESULTS}/${bench}/queries.txt"
    echo "_node1" >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
    $(get_influx_data "${QUERY}") >> "${BENCHMARK_RESULTS}/${bench}/${bench}_${measurement}_data"
}