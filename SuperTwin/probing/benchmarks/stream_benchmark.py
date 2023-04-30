import sys

sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../observation")
sys.path.append("../../sampling")

import utils
import remote_probe
import detect_utils
import observation

import paramiko
from scp import SCPClient

import glob


def vector_flags(max_vector):

    if max_vector == "avx":
        return ["-xAVX"]
    elif max_vector == "avx2":
        return ["-xCORE-AVX2"]
    elif max_vector == "avx512":
        return ["-xCORE-AVX512", "-qopt-zmm-usage=high"]
    else:
        return []


##Can use the same architecture for creating mpi benchmarks
##Note that benchmarks are copied alongside with probing framework beforehand calling
##this function
def generate_stream_bench_sh(SuperTwin):

    modifiers = {}
    modifiers["environment"] = {}

    td = utils.get_twin_description(SuperTwin)
    mt_info = utils.get_multithreading_info(td)

    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    vector = utils.get_biggest_vector_inst(td)
    print("My vector:", vector)
    if vector == None:  ##No vector instructions, so compile with plain gcc
        vector = "gcc"

    thread_set = []
    thr = 1
    while thr < total_threads:
        thread_set.append(thr)
        thr = thr * 2

    if no_cores_per_socket not in thread_set:
        thread_set.append(no_cores_per_socket)

    if no_threads_per_socket not in thread_set:
        thread_set.append(no_threads_per_socket)

    if total_cores not in thread_set:
        thread_set.append(total_cores)

    if total_threads not in thread_set:
        thread_set.append(total_threads)

    print("STREAM Benchmark thread set:", thread_set)

    ##Two possiblities, numa will have two different versions for number of threads that span
    ##multiple numa domains

    is_numa = utils.is_numa_td(td)
    stream_compiler_flags = [
        "-O3",
        "-DNTIMES=100",
        "-DOFFSET=0",
        "-DSTREAM_TYPE=double",
        "-DSTREAM_ARRAY_SIZE=268435456",
        "-Wall",
        "-mcmodel=medium",
        "-qopenmp",
        "-shared-intel",
    ]

    stream_compiler_flags += vector_flags(vector)
    modifiers["environment"]["flags"] = stream_compiler_flags

    base = "/tmp/dt_probing/benchmarks/STREAM"
    make_lines = [
        "#!/bin/bash \n\n\n",
        "source /opt/intel/oneapi/setvars.sh \n",
        "make -C " + base + " " + "stream_" + vector + "\n\n",
        "mkdir /tmp/dt_probing/benchmarks/STREAM_RES_" + SuperTwin.name + "\n",
    ]

    writer = open("probing/benchmarks/compile_stream_bench.sh", "w+")
    for line in make_lines:
        writer.write(line)
    writer.close()
    maker = "bash /tmp/dt_probing/benchmarks/compile_stream_bench.sh"
    runs = {}

    for thread in thread_set:
        thr_name = "t_" + str(thread)
        modif_key = str(thread)
        if thread == 1:  ##Burasını environment'a yazmak lazım
            runs[thr_name] = (
                "likwid-pin -c N:0 ./stream_"
                + vector
                + " &>> ../STREAM_RES_"
                + SuperTwin.name
                + "/"
                + thr_name
                + ".txt"
            )
            try:
                modifiers[modif_key].append("likwid-pin -c N:0")
            except:
                modifiers[modif_key] = []
                modifiers[modif_key].append("likwid-pin -c N:0")
        else:
            pin_and_thread = "likwid-pin "
            if is_numa:
                pin_and_thread += "-m "
            pin_and_thread += "-c N:0-" + str(thread - 1)
            runs[thr_name] = (
                pin_and_thread
                + " ./stream_"
                + vector
                + " &>> ../STREAM_RES_"
                + SuperTwin.name
                + "/"
                + thr_name
                + ".txt"
            )
            try:
                modifiers[modif_key].append(pin_and_thread)
            except:
                modifiers[modif_key] = []
                modifiers[modif_key].append(pin_and_thread)

    for key in runs:
        writer = open(SuperTwin.name + "_STREAM_" + key + ".sh", "w+")
        writer.write("#!/bin/bash" + "\n")
        writer.write("source /opt/intel/oneapi/setvars.sh" + "\n")
        writer.write("cd /tmp/dt_probing/benchmarks/STREAM \n")
        writer.write(runs[key] + "\n")
        writer.close()

    print("STREAM benchmark run scripts generated..")

    return modifiers, maker, runs


def compile_stream_bench(SuperTwin, maker):

    ##This will be common together with hpcg ?
    path = detect_utils.cmd("pwd")[1].strip("\n")
    print("path:", path)
    path += "/probing/benchmarks/STREAM"
    print("path:", path)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass
    )

    scp = SCPClient(ssh.get_transport())

    ##Copy benchmark framework if there is problem
    try:
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )
        remote_probe.run_sudo_command(
            ssh,
            SuperTwin.SSHpass,
            SuperTwin.name,
            "sudo rm -r /tmp/dt_probing/benchmarks/*",
        )
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )
    except:
        remote_probe.run_command(
            ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/"
        )
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )
        remote_probe.run_sudo_command(
            ssh,
            SuperTwin.SSHpass,
            SuperTwin.name,
            "sudo rm -r /tmp/dt_probing/benchmarks/*",
        )
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )

    scp.put(
        "probing/benchmarks/compile_stream_bench.sh",
        remote_path="/tmp/dt_probing/benchmarks/",
    )
    remote_probe.run_sudo_command(
        ssh, SuperTwin.SSHpass, SuperTwin.name, maker
    )


##I need some functions like
##utils.copy_file_to_remote()
##utils.copy_folder_to_remote()


def copy_file_to_remote(SuperTwin, f_name, remote_path="tmp/dt_files/"):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass
    )
    scp = SCPClient(ssh.get_transport())

    try:
        scp.put(f_name, remote_path=remote_path)
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_files/")
        scp.put(f_name, remote_path=remote_path)


def copy_file_to_local(SuperTwin, remote_path, local_path):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass
    )
    scp = SCPClient(ssh.get_transport())
    print("remote_path:", remote_path, "local_path:", local_path)
    try:
        scp.get(recursive=True, remote_path=remote_path, local_path=local_path)
    except:
        print("Can't get remote files..")


def get_benchmark_observation_fields(td, script):

    reader = open(script, "r")
    lines = reader.readlines()
    command = lines[3].strip("\n")
    affinity = command.split("./")[0].strip(" ")
    threads = utils.resolve_likwid_pin(td, affinity)
    thread_count = len(threads)
    observation = {}
    observation["command"] = command
    observation["affinity"] = affinity
    observation["thread_count"] = thread_count
    observation["threads"] = threads

    return observation


def execute_stream_runs(SuperTwin, runs):

    td = utils.get_twin_description(SuperTwin)

    for key in runs:
        script_name = SuperTwin.name + "_STREAM_" + key + ".sh"
        time, uid = observation.observe_script_wrap(SuperTwin, script_name)

        print("Observation", uid, "is completed in", time, "seconds")
        observation_dict = get_benchmark_observation_fields(td, script_name)
        observation_dict["name"] = "STREAM_" + key
        observation_dict["duration"] = time
        observation_dict["uid"] = uid
        observation_dict["metrics"] = {}
        observation_dict["metrics"]["software"] = []
        observation_dict["metrics"]["hardware"] = []
        # observation["report"] = observation_standard.main()
        for metric in SuperTwin.monitor_metrics:
            if (
                metric.find("RAPL") == -1
            ):  ##RAPL is a hardware metric but monitored
                observation_dict["metrics"]["software"].append(metric)
        for metric in SuperTwin.observation_metrics:
            observation_dict["metrics"]["hardware"].append(metric)
        SuperTwin.update_twin_document__add_observation(observation_dict)

    copy_file_to_local(
        SuperTwin,
        "/tmp/dt_probing/benchmarks/STREAM_RES_" + SuperTwin.name,
        "probing/benchmarks/",
    )


def execute_stream_bench(SuperTwin):

    ##This will be common together with hpcg ?
    path = detect_utils.cmd("pwd")[1].strip("\n")
    print("path:", path)
    path += "/probing/benchmarks/STREAM"
    print("path:", path)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass
    )

    scp = SCPClient(ssh.get_transport())

    try:
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )
        remote_probe.run_sudo_command(
            ssh,
            SuperTwin.SSHpass,
            SuperTwin.name,
            "sudo rm -r /tmp/dt_probing/benchmarks/*",
        )
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )
    except:
        remote_probe.run_command(
            ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/"
        )
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )
        remote_probe.run_sudo_command(
            ssh,
            SuperTwin.SSHpass,
            SuperTwin.name,
            "sudo rm -r /tmp/dt_probing/benchmarks/*",
        )
        scp.put(
            path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/"
        )

    remote_probe.run_command(
        ssh,
        SuperTwin.name,
        "mkdir /tmp/dt_probing/benchmarks/STREAM/STREAM_res_" + SuperTwin.name,
    )
    remote_probe.run_sudo_command(
        ssh,
        SuperTwin.SSHpass,
        SuperTwin.name,
        "sh /tmp/dt_probing/benchmarks/STREAM/gen_bench.sh",
    )
    scp.get(
        recursive=True,
        remote_path="/tmp/dt_probing/benchmarks/STREAM/STREAM_RES_"
        + SuperTwin.name,
        local_path="probing/benchmarks/",
    )


def parse_one_stream_res(res_mt_scale, one_res):

    thread = one_res.split("t_")[1]
    thread = int(thread.split(".")[0])
    # print("file:", one_res, "threads:", thread)

    reader = open(one_res, "r")
    lines = reader.readlines()
    reader.close()

    run_max = 0.0
    for line in lines:
        if (
            line.find("Copy") != -1
            or line.find("Scale") != -1
            or line.find("Add") != -1
            or line.find("Triad") != -1
        ):

            fields = line.split(" ")
            fields = [x for x in fields if x != ""]
            fields = [x.strip(":") for x in fields]
            res = float(fields[1])
            # print("file:", one_res, "field:", fields[0], "res:", res)

            res_mt_scale[fields[0]][str(thread)] = res
            if res > run_max:
                run_max = res

    res_mt_scale["Max_Thr"][str(thread)] = run_max

    return res_mt_scale


def parse_stream_bench(SuperTwin):

    res_base = "probing/benchmarks/STREAM_RES_" + SuperTwin.name + "/"
    files = glob.glob(res_base + "*.txt")

    res_mt_scale = {}
    res_mt_scale["Copy"] = {}
    res_mt_scale["Scale"] = {}
    res_mt_scale["Add"] = {}
    res_mt_scale["Triad"] = {}
    res_mt_scale["Max_Thr"] = {}

    for _file in files:
        res_mt_scale = parse_one_stream_res(res_mt_scale, _file)

    max_global = 0
    for key in res_mt_scale["Max_Thr"]:
        if res_mt_scale["Max_Thr"][key] > max_global:
            max_global = res_mt_scale["Max_Thr"][key]

    res_mt_scale["Max_Glob"] = max_global

    return res_mt_scale
