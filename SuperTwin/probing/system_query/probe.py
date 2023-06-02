import system
import diskinfo
import detect_utils
import parse_cpuid
import parse_likwid_topology
import parse_lshw
import json

import sys

sys.path.append("/tmp/dt_probing/pmu_event_query")  ##For remote probing
sys.path.append("../pmu_event_query")  ##For local structure
import parse_evtinfo


def choose_info(
    hostname,
    system,
    cache_info,
    socket_groups,
    domains,
    cache_topology,
    affinity,
    gpu_info,
    PMUs,
    pmprobe,
):
    ##Chosen info to generate dtdl twin
    chosen_info = {}
    chosen_info["hostname"] = hostname
    chosen_info["os"] = (
        system.get("system", {}).get("os", {}).get("version", "")
    )
    chosen_info["arch"] = (
        system.get("system", {}).get("kernel", {}).get("arch", "")
    )
    chosen_info["uuid"] = system.get("uuid", "")

    chosen_info["system"] = {}

    chosen_info["system"]["motherboard"] = {}
    chosen_info["system"]["motherboard"]["name"] = (
        system.get("system", {}).get("motherboard", {}).get("name", "")
    )
    chosen_info["system"]["motherboard"]["vendor"] = (
        system.get("system", {}).get("motherboard", {}).get("vendor", "")
    )

    chosen_info["system"]["bios"] = {}
    chosen_info["system"]["bios"]["version"] = (
        system.get("firmware", {}).get("bios", {}).get("version", "")
    )
    chosen_info["system"]["bios"]["date"] = (
        system.get("firmware", {}).get("bios", {}).get("date", "")
    )
    chosen_info["system"]["bios"]["vendor"] = (
        system.get("firmware", {}).get("bios", {}).get("vendor", "")
    )

    chosen_info["system"]["kernel"] = {}
    chosen_info["system"]["kernel"]["version"] = (
        system.get("system", {}).get("kernel", {}).get("version", "")
    )

    chosen_info["memory"] = {}
    chosen_info["memory"]["total"] = {}
    chosen_info["memory"]["total"]["size"] = int(
        system.get("memory", {}).get("total", {}).get("size", 0)
    )
    chosen_info["memory"]["total"]["banks"] = int(
        system.get("memory", {}).get("total", {}).get("banks", 0)
    )

    chosen_info["memory"]["banks"] = {}
    # for bank
    _id = 0
    for key in system.get("memory", {}):
        if key.find("bank:") != -1:
            ident = key
            temp_bank = {}
            temp_bank["id"] = _id
            _id += 1

            try:
                temp_bank["size"] = int(
                    system["memory"].get(ident, {}).get("size", 0)
                )
                temp_bank["slot"] = (
                    system["memory"].get(ident, {}).get("slot", "")
                )
                temp_bank["clock"] = int(
                    system["memory"].get(ident, {}).get("clock", "")
                )
                temp_bank["description"] = (
                    system["memory"].get(ident, {}).get("description", "")
                )
                temp_bank["vendor"] = (
                    system["memory"].get(ident, {}).get("vendor", "")
                )
                temp_bank["model"] = (
                    system["memory"].get(ident, {}).get("product", "")
                )
                chosen_info["memory"]["banks"][ident] = temp_bank
            except:
                _id -= 1

    chosen_info["network"] = {}
    for key in system.get("network", {}):
        chosen_info["network"][key] = {}
        try:
            chosen_info["network"][key]["ipv4"] = system["network"][key].get(
                "ipv4", ""
            )
        except:
            chosen_info["network"][key]["ipv4"] = ""

        try:
            chosen_info["network"][key]["businfo"] = system["network"][
                key
            ].get("businfo", "")
            chosen_info["network"][key]["vendor"] = system["network"][key].get(
                "vendor", ""
            )
            chosen_info["network"][key]["model"] = system["network"][key].get(
                "product", ""
            )
            chosen_info["network"][key]["firmware"] = system["network"][
                key
            ].get("firmware", "")
            chosen_info["network"][key]["virtual"] = "no"
        except:
            chosen_info["network"][key]["businfo"] = "virtual"
            chosen_info["network"][key]["vendor"] = "virtual"
            chosen_info["network"][key]["model"] = "virtual"
            chosen_info["network"][key]["firmware"] = "virtual"
            chosen_info["network"][key]["virtual"] = "yes"

        try:
            chosen_info["network"][key]["speed"] = system["network"][key].get(
                "speed", ""
            )
        except:
            chosen_info["network"][key]["speed"] = "no-link"

        chosen_info["network"][key]["serial"] = system["network"][key].get(
            "serial", ""
        )
        chosen_info["network"][key]["link"] = system["network"][key].get(
            "link", ""
        )

    ##ugly workaround for windows ruined partition
    if system.get("disk", {}).get("logical", {}).get("count", 0) == 1:
        system["disk"]["nvme0n1"] = {
            "model": "KINGSTON SKC2000M8500G",
            "size": 500107862016,
            "units": "bytes",
        }
        system["disk"]["logical"]["count"] = 2
    ##ugly workaround for windows ruined partition

    chosen_info["disk"] = {}
    chosen_info["disk"]["no_disks"] = system["disk"]["logical"]["count"]
    for key in system.get("disk", {}):
        if key != "logical":
            chosen_info["disk"][key] = {}
            chosen_info["disk"][key]["size"] = system["disk"][key]["size"]
            chosen_info["disk"][key]["model"] = system["disk"][key]["model"]
            # chosen_info['disk'][key]['rotational'] = int(disk['disk'][key]['rotational'])

    ##Note that this info here is "to be expanded" for all cpus, all includes all specs and events
    chosen_info["cpu"] = {}
    chosen_info["cpu"]["specs"] = {}
    chosen_info["cpu"]["specs"]["sockets"] = int(
        system.get("cpu", {}).get("physical", {}).get("number", 0)
    )
    ##From there, assumes all cpus will be identical on the same machine
    chosen_info["cpu"]["specs"]["model"] = (
        system.get("cpu", {}).get("physical_0", {}).get("product", "")
    )
    chosen_info["cpu"]["specs"]["type"] = (
        system.get("cpu", {}).get("physical_0", {}).get("architecture", "")
    )
    chosen_info["cpu"]["specs"]["cores"] = int(
        system.get("cpu", {}).get("physical_0", {}).get("cores", 0)
    )
    chosen_info["cpu"]["specs"]["threads"] = int(
        system.get("cpu", {}).get("physical_0", {}).get("threads", 0)
    )
    chosen_info["cpu"]["specs"]["threads_per_core"] = int(
        system.get("cpu", {}).get("physical_0", {}).get("threads_per_core", 0)
    )
    chosen_info["cpu"]["specs"]["hyperthreading"] = (
        system.get("cpu", {}).get("physical", {}).get("smt", "")
    )
    chosen_info["cpu"]["specs"]["min_mhz"] = (
        system.get("cpu", {}).get("physical_0", {}).get("min_Mhz", "")
    )
    chosen_info["cpu"]["specs"]["max_mhz"] = (
        system.get("cpu", {}).get("physical_0", {}).get("max_Mhz", "")
    )
    # chosen_info['cpu']['specs']['bus_mhz'] = system['cpu']['physical_0']['bus_mhz']
    chosen_info["cpu"]["specs"]["flags"] = (
        system.get("cpu", {}).get("physical_0", {}).get("flags", "")
    )

    chosen_info["cpu"]["tlb"] = cache_info["tlb"]
    chosen_info["cpu"]["cache"] = cache_topology

    chosen_info["numa"] = domains
    chosen_info["affinity"] = affinity

    chosen_info["gpus"] = gpu_info
    chosen_info["PMUs"] = PMUs
    chosen_info["metrics_avail"] = pmprobe

    return chosen_info

    ##tlb from cpuid
    ##performance counters from cpuid
    ##gpu(s) from likwid-topology


def generate_hardware_dict(to_gen, info_list):

    for item in info_list:

        try:
            to_gen[item[0]]
        except:
            to_gen[item[0]] = {}

        try:
            to_gen[item[0]][item[1]]
        except:
            to_gen[item[0]][item[1]] = {}

        try:
            to_gen[item[0]][item[1]][item[2]]
        except:
            to_gen[item[0]][item[1]][item[2]] = {}

    for item in info_list:
        to_gen[item[0]][item[1]][item[2]] = item[3]

    return to_gen


def print_hardware_dict(hw_dict):

    print("##################")
    for key in hw_dict:
        print("### key:", key)
        for inner in hw_dict[key]:
            print("### inner:", inner)
            print(hw_dict[key][inner])


def get_pmprobe():

    metrics_avail = []

    metric_lines = detect_utils.output_lines("pmprobe")
    metric_lines = [x.strip("\n") for x in metric_lines]

    for metric_line in metric_lines:

        fields = metric_line.split(" ")
        metric = fields[0]
        instances = int(fields[1])

        if instances > 0:  ##Do not include metrics that are not available
            metrics_avail.append(metric)

    return metrics_avail


def main():

    hostname = detect_utils.cmd("hostname")[1].strip("\n")
    system_list = system.detect()
    diskinfo_list = diskinfo.detect()

    system_hw = parse_lshw.parse_lshw()
    cache_info = parse_cpuid.parse_cpuid()
    (
        socket_groups,
        domains,
        cache_topology,
        gpu_info,
    ) = parse_likwid_topology.parse_likwid()
    affinity = parse_likwid_topology.parse_affinity()

    ## where we get PMY's
    PMUs = parse_evtinfo.main()
    pmprobe = get_pmprobe()

    info = choose_info(
        hostname,
        system_hw,
        cache_info,
        socket_groups,
        domains,
        cache_topology,
        affinity,
        gpu_info,
        PMUs,
        pmprobe,
    )

    print("Will write to file")
    with open("/tmp/dt_probing/system_query/probing.json", "w") as outfile:
        json.dump(info, outfile)
    print("Should have write to file")
    print("Probing done succesfuly..")
    return info


if __name__ == "__main__":

    main()
