import React, { useEffect, useState } from "react";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";

import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

import AnimatedCard from "../components/Card";

const MonitoringMetrics = () => {
  const [x, setX] = useState(mockAPICall());

  const columnDefs = [
    { headerName: "Metric", field: "MetricName" },
    {
      headerName: "Metric Type",
      field: "metric_type",
      maxWidth: 200,
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
    console.log(event.api.getSelectedRows());
  };

  return metricData !== undefined && x !== undefined ? (
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
          backgroundColor: "#F6DDCC",
          borderRadius: "3%",
          marginLeft: "6%",
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
            rowData={metricData}
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
          backgroundColor: "#F6DDCC",
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
          }}
        >
          Recommended Metric Packages
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
          {x.map((group) => {
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
              class="bg-white hover:bg-gray-100 text-gray-800 py-3 px-5 text-xl border border-gray-400 rounded shadow"
              style={{
                marginTop: "7%",
              }}
            >
              Start Monitoring
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

const mockAPICall = () => {
  var mockData = [
    [
      1,
      "To monitor network traffic",
      [
        "Metric-1",
        "Metric-2",
        "Metric-3",
        "Metric-1",
        "Metric-2",
        "Metric-3",
        "Metric-1",
        "Metric-2",
        "Metric-3",
        "Metric-1",
        "Metric-2",
        "Metric-3",
        "Metric-1",
        "Metric-2",
        "Metric-3",
      ],
    ],
    [2, "To monitor CPU load", ["Metric-2", "Metric-3"]],
    [3, "Number of NUMA access", ["Metric-1", "Metric-3"]],
    [4, "....", ["Metric-3"]],
    [5, "....", ["Metric-1", "Metric-2", "Metric-3"]],
    [6, "....", ["Metric-1", "Metric-2", "Metric-3"]],
  ];

  return mockData;
};

const metricData = [
  {
    metric_type: "CPU",
    MetricName: "CPU Metric-1",
  },
  {
    metric_type: "Network",
    MetricName: "Network Metric-1",
  },
  {
    metric_type: "NUMA",
    MetricName: "NUMA Metric-1",
  },
  {
    metric_type: "GPU",
    MetricName: "GPU Metric-1",
  },
  {
    metric_type: "Disk",
    MetricName: "Disk Metric-1",
  },
  {
    metric_type: "CPU",
    MetricName: "CPU Metric-2",
  },
  {
    metric_type: "Network",
    MetricName: "Network Metric-2",
  },
  {
    metric_type: "NUMA",
    MetricName: "NUMA Metric-2",
  },
  {
    metric_type: "GPU",
    MetricName: "GPU Metric-2",
  },
  {
    metric_type: "Disk",
    MetricName: "Disk Metric-2",
  },
  {
    metric_type: "CPU",
    MetricName: "CPU Metric-3",
  },
  {
    metric_type: "Network",
    MetricName: "Network Metric-3",
  },
  {
    metric_type: "NUMA",
    MetricName: "NUMA Metric-3",
  },
  {
    metric_type: "GPU",
    MetricName: "GPU Metric-3",
  },
  {
    metric_type: "Disk",
    MetricName: "Disk Metric-3",
  },
  {
    metric_type: "CPU",
    MetricName: "CPU Metric-4",
  },
  {
    metric_type: "Network",
    MetricName: "Network Metric-4",
  },
  {
    metric_type: "NUMA",
    MetricName: "NUMA Metric-4",
  },
  {
    metric_type: "GPU",
    MetricName: "GPU Metric-4",
  },
  {
    metric_type: "Disk",
    MetricName: "Disk Metric-4",
  },
  {
    metric_type: "CPU",
    MetricName: "CPU Metric-5",
  },
  {
    metric_type: "Network",
    MetricName: "Network Metric-5",
  },
  {
    metric_type: "NUMA",
    MetricName: "NUMA Metric-5",
  },
  {
    metric_type: "GPU",
    MetricName: "GPU Metric-5",
  },
  {
    metric_type: "Disk",
    MetricName: "Disk Metric-5",
  },
  {
    metric_type: "CPU",
    MetricName: "CPU Metric-6",
  },
  {
    metric_type: "Network",
    MetricName: "Network Metric-6",
  },
  {
    metric_type: "NUMA",
    MetricName: "NUMA Metric-6",
  },
  {
    metric_type: "GPU",
    MetricName: "GPU Metric-6",
  },
  {
    metric_type: "Disk",
    MetricName: "Disk Metric-6",
  },
];