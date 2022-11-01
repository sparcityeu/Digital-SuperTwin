import React, { useEffect, useState } from "react";
import { Route, useNavigate } from "react-router-dom";
import axios from "axios";

import { TooltipComponent } from "@syncfusion/ej2-react-popups";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine.css";

const PerformExperiment = () => {
  const [experimentMetrics, setExperimentMetrics] = useState(undefined);
  const [container, setContainer] = useState([]);
  const [cmd, setCMD] = useState(undefined);

  const navigate = useNavigate();

  function handleChange(event) {
    setCMD(event.target.value);
  }

  const getExperimentMetrics = async () => {
    try {
      const res = await axios.get(
        "http://127.0.0.1:5000/api/getMetrics/experiment"
      );
      console.log(res.data);
      setExperimentMetrics(res.data["experimentMetrics"]);
      return res.data;
    } catch (err) {}
  };

  async function sendExperiment(e) {
    e.preventDefault();
    await axios
      .post("http://127.0.0.1:5000/api/appendMetrics/experiment", {
        experimentMetrics: container,
      })
      .then((response) => this.myFunction(response.status))
      .catch(function (error) {
        if (error.response) {
        }
      });
    console.log("Experiment metrics set");

    await axios
      .post("http://127.0.0.1:5000/api/runExperiment", {
        cmd,
      })
      .then((response) => this.myFunction(response.status))
      .catch(function (error) {
        if (error.response) {
        }
      });
    console.log("Experiment has run");

    navigate("/DashboardLinks");
  }

  useEffect(() => {
    getExperimentMetrics();
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

  return getExperimentMetrics !== undefined ? (
    <div
      className="grid grid-cols-11"
      style={{
        columnGap: "2%",
      }}
    >
      <div
        class="col-span-5"
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
            onChange={handleChange}
            style={{
              height: "100%",
              resize: "none",
            }}
          ></textarea>

          <TooltipComponent content="Submit" position="BottomCenter">
            <button
              type="submit"
              onClick={(e) => sendExperiment(e)}
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
        class="col-span-6"
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
            rowData={experimentMetrics}
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
