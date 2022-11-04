import React, { useEffect, useState } from "react";
import { Route, useNavigate } from "react-router-dom";
import axios from "axios";

import { TooltipComponent } from "@syncfusion/ej2-react-popups";

import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

import AnimatedCard from "../components/Card";

const MonitoringMetrics = () => {
  const [monitoringMetrics, setmonitoringMetrics] = useState(undefined);
  const [container, setContainer] = useState([]);
  const navigate = useNavigate();

  const getMonitoringMetrics = async () => {
    try {
      const res = await axios.get(
        "http://127.0.0.1:5000/api/getMetrics/monitoring"
      );
      console.log(res.data);
      setmonitoringMetrics(res.data["monitoringMetrics"]);
      return res.data;
    } catch (err) {}
  };

  async function startMonitor(e) {
    e.preventDefault();
    await axios
      .post("http://127.0.0.1:5000/api/appendMetrics/monitoring", {
        monitoringMetrics: container,
      })
      .then((response) => this.myFunction(response.status))
      .catch(function (error) {
        if (error.response) {
        }
      });
    console.log("aaaaa");
    navigate("/DashboardLinks");
  }

  useEffect(() => {
    getMonitoringMetrics();
  }, []);

  const columnDefs = [
    { headerName: "Metric", field: "metric" },
    {
      headerName: "Metric Type",
      field: "type",
      maxWidth: 130,
    },
  ];

  const defaultColDef = {
    sortable: true,
    editable: false,
    flex: 1,
    filter: true,
  };
  //define selection type single or multiple
  const rowSelectionType = "multiple";

  //function will trigger once selection changed
  const onSelectionChanged = (event) => {
    setContainer(event.api.getSelectedRows());
    console.log(container);
  };

  return monitoringMetrics !== [] ? (
    <div
      className="grid grid-cols-11"
      style={{
        columnGap: "2%",
      }}
    >
      <div
        class="col-span-6"
        style={{
          height: "100vh",
          backgroundColor: "#4A235A",
          borderRadius: "3%",
          marginLeft: "6%",
          marginBottom: "7%",
          paddingTop: "3%",
          paddingLeft: "3%",
          paddingRight: "3%",
          paddingBottom: "6%",
        }}
      >
        <p
          className="text-xl"
          style={{
            textAlign: "left",
            fontWeight: "bold",
            marginTop: "",
            marginBottom: "3%",
            color: "white",
          }}
        >
          Available Monitoring Metrics
        </p>
        <div
          className="ag-theme-alpine"
          style={{ height: "95%", width: "100%" }}
        >
          <AgGridReact
            masterDetail={true}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            rowData={monitoringMetrics}
            rowSelection={rowSelectionType}
            onSelectionChanged={onSelectionChanged}
            rowMultiSelectWithClick={true}
            pagination={true}
          ></AgGridReact>
        </div>
      </div>

      <div
        class="col-span-5"
        style={{
          height: "100vh",
          backgroundColor: "#4A235A",
          borderRadius: "3%",
          marginRight: "6%",
          marginBottom: "7%",
          padding: "3%",
        }}
      >
        <p
          className="text-xl"
          style={{
            textAlign: "left",
            fontWeight: "bold",
            marginTop: "",
            marginBottom: "3%",
            color: "white",
          }}
        >
          Pre-Selected Metrics
        </p>
        <div
          className="ag-theme-alpine"
          style={{
            height: "83%",
            width: "100%",
            textAlign: "center",
            overflowY: "scroll",
          }}
        >
          {mockData.map((group) => {
            return AnimatedCard(group[0], group[1], group[2]);
          })}
        </div>
        <div
          style={{
            textAlign: "center",
          }}
        >
          <TooltipComponent content="Submit" position="BottomCenter">
            <button
              type="submit"
              onClick={(e) => startMonitor(e)}
              class="bg-white hover:bg-gray-100 text-gray-800 py-3 px-5 text-xl border border-gray-400 rounded shadow"
              style={{
                marginTop: "7%",
              }}
            >
              Add Metrics
            </button>
          </TooltipComponent>
        </div>
      </div>
    </div>
  ) : (
    <p>Loading</p>
  );
};
export default MonitoringMetrics;

var mockData = [
  [
    1,
    "Kernel metrics",
    [
      "kernel.all.pressure.cpu.some.total",
      "hinv.cpu.clock",
      "kernel.percpu.cpu.idle",
      "kernel.pernode.cpu.idle",
      "disk.dev.read",
      "disk.dev.write",
      "disk.dev.total",
      "disk.dev.read_bytes",
      "disk.dev.write_bytes",
      "disk.dev.total_bytes",
      "disk.all.read",
      "disk.all.write",
      "disk.all.total",
      "disk.all.read_bytes",
      "disk.all.write_bytes",
      "disk.all.total_bytes",
      "mem.util.used",
      "mem.util.free",
      "swap.pagesin",
      "mem.numa.util.free",
      "mem.numa.util.used",
      "mem.numa.alloc.hit",
      "mem.numa.alloc.miss",
      "mem.numa.alloc.local_node",
      "mem.numa.alloc.other_node",
      "network.all.in.bytes",
      "network.all.out.bytes",
      "kernel.all.nusers",
      "kernel.all.nprocs",
      "lmsensors.coretemp_isa_0000.package_id_0",
      "lmsensors.coretemp_isa_0001.package_id_1",
    ],
  ],
  [2, "Hardware Metrics", ["RAPL_ENERGY_PKG", "RAPL_ENERGY_DRAM"]]
];

// const metricData = [
//   {
//     metric_type: "CPU",
//     MetricName: "CPU Metric-1",
//   },
//   {
//     metric_type: "Network",
//     MetricName: "Network Metric-1",
//   },
//   {
//     metric_type: "NUMA",
//     MetricName: "NUMA Metric-1",
//   },
//   {
//     metric_type: "GPU",
//     MetricName: "GPU Metric-1",
//   },
//   {
//     metric_type: "Disk",
//     MetricName: "Disk Metric-1",
//   },
//   {
//     metric_type: "CPU",
//     MetricName: "CPU Metric-2",
//   },
//   {
//     metric_type: "Network",
//     MetricName: "Network Metric-2",
//   },
//   {
//     metric_type: "NUMA",
//     MetricName: "NUMA Metric-2",
//   },
//   {
//     metric_type: "GPU",
//     MetricName: "GPU Metric-2",
//   },
//   {
//     metric_type: "Disk",
//     MetricName: "Disk Metric-2",
//   },
//   {
//     metric_type: "CPU",
//     MetricName: "CPU Metric-3",
//   },
//   {
//     metric_type: "Network",
//     MetricName: "Network Metric-3",
//   },
//   {
//     metric_type: "NUMA",
//     MetricName: "NUMA Metric-3",
//   },
//   {
//     metric_type: "GPU",
//     MetricName: "GPU Metric-3",
//   },
//   {
//     metric_type: "Disk",
//     MetricName: "Disk Metric-3",
//   },
//   {
//     metric_type: "CPU",
//     MetricName: "CPU Metric-4",
//   },
//   {
//     metric_type: "Network",
//     MetricName: "Network Metric-4",
//   },
//   {
//     metric_type: "NUMA",
//     MetricName: "NUMA Metric-4",
//   },
//   {
//     metric_type: "GPU",
//     MetricName: "GPU Metric-4",
//   },
//   {
//     metric_type: "Disk",
//     MetricName: "Disk Metric-4",
//   },
//   {
//     metric_type: "CPU",
//     MetricName: "CPU Metric-5",
//   },
//   {
//     metric_type: "Network",
//     MetricName: "Network Metric-5",
//   },
//   {
//     metric_type: "NUMA",
//     MetricName: "NUMA Metric-5",
//   },
//   {
//     metric_type: "GPU",
//     MetricName: "GPU Metric-5",
//   },
//   {
//     metric_type: "Disk",
//     MetricName: "Disk Metric-5",
//   },
//   {
//     metric_type: "CPU",
//     MetricName: "CPU Metric-6",
//   },
//   {
//     metric_type: "Network",
//     MetricName: "Network Metric-6",
//   },
//   {
//     metric_type: "NUMA",
//     MetricName: "NUMA Metric-6",
//   },
//   {
//     metric_type: "GPU",
//     MetricName: "GPU Metric-6",
//   },
//   {
//     metric_type: "Disk",
//     MetricName: "Disk Metric-6",
//   },
// ];
