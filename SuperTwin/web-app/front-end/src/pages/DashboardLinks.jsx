import React, { useEffect, useState } from "react";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";
import axios from "axios";

import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

import AnimatedStatusCard from "../components/StatusCard";

const DashboardLinks = () => {
  const [dashboards, setDashboards] = useState(undefined);
  const [daemonStatus, setDaemonStatus] = useState(true);

  const getDashboards = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:5000/api/getDashboards");
      console.log(res.data);
      setDashboards(res.data["dashboards"]);
      return res.data;
    } catch (err) {}
  };

  useEffect(() => {
    getDashboards();
  }, []);

  const columnDefs = [
    { headerName: "Dashboard", field: "dashboard_name" },
    { headerName: "Link", field: "dashboard_link", maxWidth: 150 },
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

  return dashboards !== [] ? (
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
            rowData={dashboards}
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
              mongodbID: "id312312412312",
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
