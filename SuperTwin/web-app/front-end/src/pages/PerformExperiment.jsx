import React, { useEffect, useState } from "react";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

const PerformExperiment = () => {
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

  return x !== undefined && x !== undefined ? (
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
          Setup the experiment
        </p>
        <div
          style={{
            textAlign: "center",
            height: "80%",
          }}
        >
          <label
            for="message"
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-400"
          ></label>
          <textarea
            id="none"
            rows="20"
            class="block p-2.5 w-full h-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            placeholder="Input the experimental code block"
            style={{
              height: "100%",
              resize: "none",
            }}
          ></textarea>

          <TooltipComponent content="Submit" position="BottomCenter">
            <button
              type="submit"
              class="bg-white hover:bg-gray-100 text-gray-800 py-3 px-5 text-xl border border-gray-400 rounded shadow"
              style={{
                textAlign: "center",
                marginTop: "7%",
              }}
            >
              Submit
            </button>
          </TooltipComponent>
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
          Experiment Metrics
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
    </div>
  ) : (
    <p>Loading</p>
  );
};
export default PerformExperiment;

const mockAPICall = () => {
  var mockData = [
    {
      ID: 1,
      DashboardName: "CPU Monitoring Dashboard",
      DashboardLink: "Link",
    },
    {
      ID: 2,
      DashboardName: "GPU Monitoring Dashboard",
      DashboardLink: "Link",
    },
    {
      ID: 3,
      DashboardName: "NUMA Monitoring Dashboard",
      DashboardLink: "Link",
    },
    {
      ID: 4,
      DashboardName: "Network Traffic Dashboard",
      DashboardLink: "Link",
    },
    {
      ID: 5,
      DashboardName: ".........",
      DashboardLink: "Link",
    },
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
