# **Digital SuperTwin**
SuperTwin creates a structured data representation over an HPC system, **manages data input from a collection of tools and enable reasonings** among them. Current capabilities of SuperTwin are; 
- Monitoring
- Automated PMU configuration
- Automated profiling
- Modelling
- Knowledge retrieval
 ---
 ## Overview
 SuperTwin creates a Digital Twin Description **(DTD)** of a target system. It could be used to model, monitor and/or observe both a remote system or local system. However, since large amounts of data are sampled and visualized during the process best use case is to model a remote system.  
 Since SuperTwin leverages a large collection of tools; it has a large dependency list. Installation of these dependencies are left to the user.    

--- 
---

## Requirements
---
### On remote host
- Performance Co-Pilot (PCP)
    - pmdas
        - perfevent pmda
        - proc pmda
        - linux pmda
        - lmsensors pmda    
*This pmdas are not required to be installed but their metrics are main interest of SuperTwin*  
*PCP components other than pmcd, pmproxy and pmdas could be disabled. They will be automatically disabled in the upcoming versions*
- perf
- likwid
- lshw
- libpfm4
- cpuid
- pciutils
- ethtool
 ---
 ### On local host
 - InfluxDB 1.8
 - MongoDB
 - Grafana 9+
    - Plugins
        - [JSON](https://grafana.com/grafana/plugins/simpod-json-datasource/)
        - [Node Graph API](https://grafana.com/grafana/plugins/simpod-json-datasource/)
        - [Plotly panel](https://grafana.com/grafana/plugins/ae3e-plotly-panel/)
- [pcp-export-pcp2influxdb](https://packages.debian.org/sid/utils/pcp-export-pcp2influxdb)
- Python 3.7+   

## Directory Structure

    .
    ├── ...
    ├── SuperTwin                     
    │   ├── supertwin.py             # Entry point of the framework, SuperTwin class
    │   ├── utils.py                 # Common functions used by all modules
    │   ├── env.txt                  # Configuration for 3rd party tools
    |   ├── monitor_metrics.txt      # Metrics to continuosly monitor
    |   ├── probing
    |       ├── remote_probe.py      # Copy probing code to remote, execute, get results 
    |       ├── detect_utils.py      # Common functions used by probing modules
    |       ├── system_query         # Probe hardware and topology info
    |           ├── system.py
    |           ├── parse_lshw.py
    |           ├── parse_showevtinfo.py
    |           ├── parse_likwid_topology.py
    |           ├── parse_cpuid.py
    |           ├── probe.py         # Entry point for probing framework
    |       ├── pmu_event_query
    |       ├── benchmarks
    |           ├── stream_benchmark.py # Execute and parse stream benchmark
    |           ├── hpcg_benchmark.py   # Execute and parse hpcg benchmark
    |           ├── carm_benchmark.py   # Execute and parse cache aware roofline model benchmark
    |               ├── STREAM       # STREAM benchmark
    |               ├── HPCG         # HPCG benchmark
    |               ├── CARM         # Cache aware roofline model benchmark
    |        ├── twin_description  
    |            ├── generate_twin.py # Generate DTD from probed info
    |        ├── dashboards
    |            ├── roofline_dashboard.py # Generate roofline and show in dashboard
    |            ├── monitoring_dashboard.py # Generate monitoring dashboard
    |            ├── observation_standard.py # Generate "observation" dashboard
    |        ├── sampling
    |            ├── sampling.py # Configure and start metric shipment events
    |        ├── observation
    |            ├── observation.py # Configure, start and record observations
    |            ├── influx_help.py # Overlap observations that take place in time temporally
    └── ...

---
## Usage with CLI
After invoking the ``supertwin.py`` metadata, generated digital twin descriptions and dashboards are registered to mongodb database named *hostname*, under collection *twin*. Observations, with their generated dashboards could be found under *observations*. Excepted output for invoking ``supertwin.py`` is as following 
```bash
> sudo python3 supertwin.py
Address of the remote system: 10.36.54.195
Creating a new digital twin with id: 53063c15-5daa-4919-a682-f0d3a97fdbb9
User: ftasyaran
Password: ******
Remote host name: dolap
Executing command on dolap : sudo rm -r /tmp/dt_probing
Executing command on dolap : mkdir /tmp/dt_probing
Copying probing framework to remote system..
Executing command on dolap : sudo rm -r /tmp/dt_probing/*
Probing framework is copied to remote system..
Executing command on dolap : sudo rm /tmp/dt_probing/pmu_event_query/out.txt
Executing command on dolap : sudo rm /tmp/dt_probing/pmu_event_query/out_emp.txt
Executing command on dolap : make -C /tmp/dt_probing/pmu_event_query
Executing command on dolap : sudo /tmp/dt_probing/pmu_event_query/./showevtinfo -L -D &>> /tmp/dt_probing/pmu_event_query/out.txt
Executing command on dolap : sudo /tmp/dt_probing/pmu_event_query/./showevtinfo &>> /tmp/dt_probing/pmu_event_query/out_emp.txt
Executing command on dolap : sudo python3 /tmp/dt_probing/system_query/probe.py
Remote probing is done..
pcp2influxdb configuration: pcp_dolap_monitor.conf generated
A daemon with pid: 2277498 is started monitoring dolap
Using database 'dolap_main' and tags 'tag=_monitor'.
Sending 35 metrics to InfluxDB at http://127.0.0.1:8086 every 1.0 sec...
(Ctrl-C to stop)
Collection id: 634939b2562da7d3f0b47fc9
STREAM Benchmark thread set: [1, 2, 4, 8, 16, 22, 32, 44, 64, 88]
STREAM benchmark script generated..
path: /home/fatih/dt_latest5/Digital-SuperTwin/SuperTwin
path: /home/fatih/dt_latest5/Digital-SuperTwin/SuperTwin/probing/benchmarks/STREAM
Executing command on dolap : sudo rm -r /tmp/dt_probing/benchmarks/*
Executing command on dolap : mkdir /tmp/dt_probing/benchmarks/STREAM/STREAM_res/
Executing command on dolap : sh /tmp/dt_probing/benchmarks/STREAM/gen_bench.sh
STREAM benchmark result added to Digital Twin
HPCG Benchmark thread set: [1, 2, 4, 8, 16, 22, 32, 44, 64, 88]
HPCG benchmark script, with params nx: 104 ny: 104 nz: 104 time: 60 is generated..
Executing command on dolap : sh /tmp/dt_probing/benchmarks/hpcg/bin/gen_bench.sh
STREAM benchmark result added to Digital Twin
CARM config generated..
CARM Benchmark thread set: [1, 2, 4, 8, 16, 22, 32, 44, 64, 88]
CARM benchmark script generated..
CARM benchmark result added to Digital Twin
Roofline dashboard added to Digital Twin
Twin state is registered to db..
```

## Usage with web application
```bash
> cd web-app/front-end
> npm install
> npm start
> cd web-app/backend
> python3 backend.py
```
Web application is available at localhost:3000

## If you want to cite please use:
```
@InProceedings{tasyaran2024_protools,
  author       = "Tasyaran, Fatih and Yasal, Osman and Morgado, José A and Ilic, Aleksandar and Unat, Didem and Kaya, Kamer",
  title        = "P-MOVE: Performance Monitoring and Visualization with Encoded Knowledge",
  year         = "2024",
  booktitle    = {{IEEE/ACM} Workshop on Programming and Performance Visualization Tools,
                  ProTools@SC 2024, Atlanta, GA, USA, November 17-22, 2024},
  publisher    = "IEEE",
}
```

<mark>Warning: This software is under development and may not produce same results on every host</mark>

