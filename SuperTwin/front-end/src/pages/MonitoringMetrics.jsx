import React, { useEffect, useState } from "react";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";

import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

import AnimatedCard from "../components/Card";

const MonitoringMetrics = () => {
  const [x, setX] = useState(mockAPICall());

  const columnDefs = [
    {
      headerName: "#",
      field: "ID",
      maxWidth: 150,
    },
    { headerName: "Metric", field: "MetricName" },
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
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
  {
    ID: 1,
    MetricName: "Metric-1",
  },
  {
    ID: 2,
    MetricName: "Metric-2",
  },
  {
    ID: 3,
    MetricName: "Metric-3",
  },
  {
    ID: 4,
    MetricName: "Metric-4",
  },
  {
    ID: 5,
    MetricName: "Metric-5",
  },
];

{
  /*}<GridComponent
          dataSource={metricData}
          width="100%"
          height="100%"
          allowPaging
          allowSorting
          rowSelection={"multiple"}
          rowMultiSelectWithClick={true}
          pageSettings={{ pageCount: 5 }}
          editSettings={editing}
          toolbar={toolbarOptions}
          style={{
            marginBottom: "50%",
          }}
        >
          <ColumnsDirective>
            {employeesGrid.map((item, index) => (
              <ColumnDirective key={index} {...item} />
            ))}
          </ColumnsDirective>
          <Inject
            services={[
              Search,
              Page,
              Resize,
              Sort,
              ContextMenu,
              Filter,
              ExcelExport,
              Edit,
              PdfExport,
            ]}
          />
        </GridComponent>
          {*/
}
