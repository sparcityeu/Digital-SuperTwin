import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { AiOutlineMenu } from "react-icons/ai";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";

import { useStateContext } from "../context/ContextProvider";

const NavButton = ({ title, customFunc, icon, color, dotColor }) => (
  <TooltipComponent content={title} position="BottomCenter">
    <button
      type="button"
      onClick={() => customFunc()}
      style={{ color }}
      className="relative text-xl rounded-full p-3 hover:bg-light-gray"
    >
      <span
        style={{ background: dotColor }}
        className="absolute inline-flex rounded-full h-2 w-2 right-2 top-2"
      />
      {icon}
    </button>
  </TooltipComponent>
);

function GetLocationName() {
  const location = useLocation();

  var a = [];
  if (
    location.pathname.substring(1, location.pathname.length) !==
      "CreateSuperTwin" &&
    location.pathname !== "/"
  ) {
    a = location.pathname
      .substring(1, location.pathname.length)
      .match(/[A-Z][a-z]+/g);
    console.log(location.pathname);
  } else {
    a = ["Create", "SuperTwin"];
  }

  var returnStr = "";
  for (var i = 0; i < a.length; i++) {
    returnStr += a[i] + " ";
  }

  return returnStr;
}

const Navbar = () => {
  const {
    currentColor,
    activeMenu,
    setActiveMenu,
    handleClick,
    isClicked,
    setScreenSize,
    screenSize,
  } = useStateContext();

  useEffect(() => {
    const handleResize = () => setScreenSize(window.innerWidth);

    window.addEventListener("resize", handleResize);

    handleResize();

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    if (screenSize <= 900) {
      setActiveMenu(false);
    } else {
      setActiveMenu(true);
    }
  }, [screenSize]);

  const handleActiveMenu = () => setActiveMenu(!activeMenu);

  return (
    <div className="flex p-2 md:ml-6 md:mr-6 relative">
      <NavButton
        title="Menu"
        customFunc={handleActiveMenu}
        color={currentColor}
        icon={<AiOutlineMenu />}
      />
      {console.log(activeMenu)}
      {!activeMenu ? (
        <div
          className="title-font sm:text-4xl text-3xl mb-4 font-medium text-italic"
          style={{
            marginLeft: "30px",
            fontSize: "26px",
            color: "white",
          }}
        >
          {GetLocationName()}
        </div>
      ) : undefined}
    </div>
  );
};

export default Navbar;
