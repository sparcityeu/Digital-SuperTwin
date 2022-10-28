import React, { useEffect, useState } from "react";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

import AnimatedStatusCard from "../components/StatusCard";

const DashboardLinks = () => {
  const [x, setX] = useState(mockAPICall());
  const [daemonStatus, setDaemonStatus] = useState(true);

  const columnDefs = [
    { headerName: "Dashboard", field: "DashboardName" },
    {
      headerName: "Dashboard Type",
      field: "dashboard_type",
      maxWidth: 200,
    },
    { headerName: "Link", field: "DashboardLink", maxWidth: 100 },
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
          Dashboard Links
        </p>
        <div
          className="ag-theme-alpine"
          style={{ height: "95%", width: "100%" }}
        >
          <AgGridReact
            masterDetail={true}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            rowData={x}
            rowSelection={rowSelectionType}
            onSelectionChanged={onSelectionChanged}
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
          Monitoring Daemon Status
        </p>
        <div
          style={{
            textAlign: "center",
          }}
        >
          <label
            for="message"
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-400"
            style={{
              height: "70%",
            }}
          ></label>
          {AnimatedStatusCard(
            "abcd-efgh-1234-5678",
            "2576",
            daemonStatus === true && daemonStatus !== false
              ? "Probing"
              : "Not connected",
            {
              machineAddress: "10.36.54.195",
              userName: "mgale",
              grafanaAPIKey: "fasdfasdfasdfasdfadsf",
            }
          )}
        </div>
      </div>
    </div>
  ) : (
    <p>Loading</p>
  );
};
export default DashboardLinks;

const mockAPICall = () => {
  var mockData = [
    {
      ID: 1,
      DashboardName: "CPU Monitoring Dashboard",
      dashboard_type: "Heatmap",
      DashboardLink: "Link",
    },
    {
      ID: 2,
      DashboardName: "GPU Monitoring Dashboard",
      dashboard_type: "Graph",
      DashboardLink: "Link",
    },
    {
      ID: 3,
      DashboardName: "NUMA Monitoring Dashboard",
      dashboard_type: "etc",
      DashboardLink: "Link",
    },
    {
      ID: 4,
      DashboardName: "Network Traffic Dashboard",
      dashboard_type: "....",
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
