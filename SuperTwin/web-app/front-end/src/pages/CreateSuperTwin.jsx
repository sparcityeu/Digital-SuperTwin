import React, { useState } from "react";
import { Route, useNavigate } from "react-router-dom";
import axios from "axios";
import { FaGithub } from "react-icons/fa";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";

const CreateSuperTwin = () => {
  const [remoteAddress, setAddress] = useState("");
  const [username, setUser] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    const registered = {
      remoteAddress: remoteAddress,
      username: username,
      password: password,
    };

      await axios
      .post("http://127.0.0.1:5000/api/startSuperTwin", {
        registration: registered,
      })
      .then((response) => this.myFunction(response.status))
      .catch(function (error) {
        if (error.response) {
        }
      });

      await axios
	  .get("http://127.0.0.1:5000/api/setDB")
	  .then((response) => this.myFunction(response.status))
	  .catch(function (error) {
              if (error.response) {
              }
	  });

    console.log(registered);
    navigate("/MonitoringMetrics");
  }

  function changeAddress(e) {
    setAddress({
      remoteAddress: e.target.value,
    });
  }
  function changeUsername(e) {
    setUser({
      username: e.target.value,
    });
  }
  function changePassword(e) {
    setPassword({
      password: e.target.value,
    });
  }

  return (
    <div
      className="grid grid-cols-5 gap-1"
      style={{
        columnGap: "3%",
      }}
    >
      <div
        class="col-span-3"
        style={{
          height: "100vh",
          backgroundColor: "#4A235A",
          borderRadius: "3%",
          marginLeft: "10%",
          marginBottom: "10%",
          padding: "12%",
        }}
      >
        <p
          className="text-6xl	centered"
          style={{
            textAlign: "center",
            fontWeight: "bolder",
            marginTop: "3%",
            color: "white",
          }}
        >
          SuperTwin
        </p>
        <div
          class="line-1"
          style={{
            marginTop: "4%",
            height: "3px",
            background: "black",
          }}
        ></div>

        <p
          className="text-3xl	centered"
          style={{
            textAlign: "center",
            fontWeight: "bold",
            marginTop: "5%",
            fontSize: "17px",
            color: "white",
          }}
        >
          Automated Performance Analysis Tool
        </p>
        <div
          style={{
            marginTop: "15%",
            borderStyle: "solid",
            borderWidth: "1px",
            borderColor: "black",
            borderRadius: "10px",
          }}
        >
          <p
            className="text-4xl	centered"
            style={{
              textAlign: "center",
              fontWeight: "lighter",
              fontSize: "15px",
              padding: "30px",
              color: "white",
            }}
          >
            SuperTwin creates a structured data representation over an HPC
            system, manages data input from a collection of tools and enable
            reasonings among them.
          </p>
        </div>

        <div
          style={{
            textAlign: "center",
            marginTop: "20%",
          }}
        >
          <TooltipComponent content="Github Repo" position="BottomCenter">
            <a
              href="https://github.com/SU-HPC/Digital-SuperTwin"
              target="_blank"
              rel="noreferrer"
            >
              <button
                style={{
                  fontSize: "40px",
                }}
              >
                <FaGithub />
              </button>
            </a>
          </TooltipComponent>
          <div
            class="line-1"
            style={{
              marginTop: "5%",
              height: "3px",
              background: "black",
            }}
          ></div>
        </div>
      </div>

      <div
        class="col-span-2"
        style={{
          height: "100vh",
          width: "auto",
          backgroundColor: "#4A235A",
          borderRadius: "3%",
          marginRight: "10%",
          marginBottom: "10%",
          textAlign: "center",
        }}
      >
        <form onSubmit={onSubmit}>
          <p
            className="text-3xl	centered"
            style={{
              textAlign: "center",
              fontWeight: "bolder",
              marginTop: "130px",
              color: "white",
            }}
          >
            Create a SuperTwin
          </p>
          <div
            style={{
              fontWeight: "bolder",
            }}
          >
            <p
              className="text-3xl	centered"
              style={{
                fontWeight: "bold",
                marginTop: "7%",
                fontSize: "15px",
                color: "white",
              }}
            >
              Remote Machine Address
            </p>
            <div style={{}}>
              <div class="form-floating mb-3 items-center ">
                <input
                  type="remoteAddress"
                  class="form-control self-center px-7 py-2.5 dasf text-center font-normal text-gray-700 border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
                  id="floatingInput"
                  placeholder={"xxx.xxx.xxx.xxx"}
                  onChange={changeAddress}
                />
              </div>
            </div>
          </div>
          <div
            style={{
              fontWeight: "bold",
              marginTop: "10%",
            }}
          >
            <p
              className="text-3xl	centered"
              style={{
                fontWeight: "bold",
                marginTop: "7%",
                fontSize: "15px",
                color: "white",
              }}
            >
              User Name
            </p>
            <div style={{}}>
              <div class="form-floating mb-3 items-center ">
                <input
                  type="username"
                  class="form-control self-center px-7 py-2.5 dasf text-center font-normal text-gray-700 border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
                  id="floatingInput"
                  placeholder={"qwerty"}
                  onChange={changeUsername}
                />
              </div>
            </div>
          </div>
          <div
            style={{
              fontWeight: "bold",
              marginTop: "10%",
            }}
          >
            <p
              className="text-3xl	centered"
              style={{
                fontWeight: "bold",
                marginTop: "7%",
                fontSize: "15px",
                color: "white",
              }}
            >
              User Password
            </p>
            <div style={{}}>
              <div class="form-floating mb-3 items-center ">
                <input
                  type="password"
                  class="form-control self-center px-7 py-2.5 dasf text-center font-normal text-gray-700 border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
                  id="floatingInput"
                  placeholder={"123456ab"}
                  onChange={changePassword}
                />
              </div>
            </div>
          </div>

          <TooltipComponent content="Submit" position="BottomCenter">
            <button
              type="submit"
              class="bg-white hover:bg-gray-100 text-gray-800 py-3 px-5 text-xl border border-gray-400 rounded shadow"
              style={{
                marginTop: "60px",
              }}
            >
              Start Probing
            </button>
          </TooltipComponent>
        </form>
      </div>
    </div>
  );
};
export default CreateSuperTwin;
