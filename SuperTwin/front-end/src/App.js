import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { FiSettings } from "react-icons/fi";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";

import { Footer, Navbar, Sidebar } from "./components";
import { CreateSuperTwin, DashboardLinks, MonitoringMetrics } from "./pages";

import { useStateContext } from "./context/ContextProvider";

import "./App.css";
import { Button } from "@syncfusion/ej2/buttons";
import PerformExperiment from "./pages/PerformExperiment";

const App = () => {
  const { activeMenu } = useStateContext();
  return (
    <div>
      <BrowserRouter>
        <div className="flex relative dark:bg-main-dark-bg">
          <div className="fixed right-4 bottom-4" style={{ zIndex: "1000" }}>
            <TooltipComponent content="Settings" position="Top">
              <button>
                <FiSettings />
              </button>
            </TooltipComponent>
          </div>
          {activeMenu ? (
            <div className="w-72 fixed sidebar dark:bg-secondary-dark-bg bg-white ">
              <Sidebar />
            </div>
          ) : (
            <div className="w-0 dark:bg-secondary-dark-bg">
              <Sidebar />
            </div>
          )}
          <div
            className={
              activeMenu
                ? "dark:bg-main-dark-bg  bg-main-bg min-h-screen md:ml-72 w-full  "
                : "bg-main-bg dark:bg-main-dark-bg  w-full min-h-screen flex-2 "
            }
          >
            <div className="fixed md:static bg-main-bg dark:bg-main-dark-bg navbar w-full ">
              <Navbar />
            </div>

            <Routes>
              <Route index element={<CreateSuperTwin />} />
              <Route
                index
                path="/CreateSuperTwin"
                element={<CreateSuperTwin />}
              />
              <Route
                path="/MonitoringMetrics"
                element={<MonitoringMetrics />}
              />
              <Route path="/DashboardLinks" element={<DashboardLinks />} />
              <Route
                path="/PerformExperiment"
                element={<PerformExperiment />}
              />
            </Routes>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
};

export default App;
