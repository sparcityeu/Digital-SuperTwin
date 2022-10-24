import React, { useEffect, useState } from "react";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

const DashboardLinks = () => {
  const [x, setX] = useState(mockAPICall());

  const columnDefs = [
    {
      headerName: "#",
      field: "ID",
      maxWidth: 150,
    },
    { headerName: "Dashboard", field: "DashboardName" },
    { headerName: "Link", field: "DashboardLink", maxWidth: 400 },
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
          Send Command to the Remote Machine
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
          <textarea
            id="message"
            rows="20"
            class="block p-2.5 w-full h-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            placeholder="Enter a shell command"
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
              Send
            </button>
          </TooltipComponent>
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
