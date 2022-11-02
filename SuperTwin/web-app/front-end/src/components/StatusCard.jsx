import * as React from "react";
import { useState, useEffect } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Checkbox from "@mui/material/Checkbox";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { border } from "@mui/system";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";
import CardMedia from "@material-ui/core/CardMedia";
import Collapse from "@material-ui/core/Collapse";
import IconButton from "@material-ui/core/IconButton";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import OnlinePredictionIcon from "@mui/icons-material/OnlinePrediction";
import { TooltipComponent } from "@syncfusion/ej2-react-popups";

import styled from "styled-components";

const CardWrapper = styled.div`
  justify-content: center;
  padding: 2rem 1rem 2rem 1rem;
  background: #4a235a;
`;

const useStyles = makeStyles((theme) => ({
  root: {
    background: "black",
    color: "#black",
  },

  expand: {
    transform: "rotate(0deg)",
    marginLeft: "auto",
    transition: theme.transitions.create("transform", {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: "rotate(180deg)",
  },
}));

const AnimatedStatusCard = (sampler_id, process_id, status, extra_info) => {
  const classes = useStyles();
  const [expanded, setExpanded] = useState(true);
  const [probingStatus, setProbingStatus] = useState(status);
  useEffect(() => {
    console.log(probingStatus);
  }, [probingStatus]);

  const handleClick = (e) => {
    e.preventDefault();
    var x = "";
    if (probingStatus === "Monitoring") {
      x = "Disconnected";
    } else {
      x = "Monitoring";
    }

    setProbingStatus(x);
  };

  const handleExpandClick = (id) => {
    setExpanded(!expanded);
  };

  return (
    <div>
      <CardWrapper>
        <Card
          className={classes.root}
          variant="outlined"
          style={{
            borderColor: "#4A235A",
            backgroundColor: "whitesmoke",
            display: "block",
          }}
        >
          <CardContent>
            <div
              className="grid grid-cols-11"
              style={{
                marginBottom: "5%",
              }}
            >
              <div class="col-span-5">
                <Typography
                  component="p"
                  variant="body2"
                  style={{
                    textAlign: "left",
                  }}
                >
                  Digital Twin ID
                </Typography>
              </div>
              <div class="col-span-6">
                <Typography
                  variant="body2"
                  style={{
                    textalign: "left",
                  }}
                >
                  {sampler_id}
                </Typography>
              </div>
            </div>
            <div
              className="grid grid-cols-11"
              style={{
                marginBottom: "5%",
              }}
            >
              <div class="col-span-5">
                <Typography
                  component="p"
                  variant="body2"
                  style={{
                    textAlign: "left",
                  }}
                >
                  Monitoring PID
                </Typography>
              </div>
              <div class="col-span-6">
                <Typography
                  variant="body2"
                  style={{
                    textalign: "left",
                  }}
                >
                  {process_id}
                </Typography>
              </div>
            </div>
            <div className="grid grid-cols-11">
              <div class="col-span-5">
                <Typography
                  component="p"
                  variant="body2"
                  style={{
                    textAlign: "left",
                  }}
                >
                  Status
                </Typography>
              </div>
              <div class="col-span-6">
                <Typography
                  variant="body2"
                  style={{
                    textalign: "left",
                  }}
                >
                  {probingStatus}
                </Typography>
              </div>
            </div>
          </CardContent>
          <CardActions
            disableSpacing
            style={{
              backgroundColor: "#212329 ",
              height: "80px",
            }}
          >
            <Typography color="common.white">Status Information</Typography>

            <IconButton
              style={{ color: "black", height: "100px" }}
              className={clsx(classes.expand, {
                [classes.expandOpen]: expanded,
              })}
              onClick={(id) => handleExpandClick(sampler_id)}
              aria-expanded={expanded}
              aria-label="show more"
            >
              <ExpandMoreIcon />
            </IconButton>
          </CardActions>
          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <CardContent
              style={{
                backgroundColor: "#212329",
              }}
            >
              {probingStatus === "Disconnected" ? (
                <Typography paragraph>
                  <Typography
                    varian="body1"
                    color="common.white"
                    key={probingStatus}
                  >
                    There is no SuperTwin currently
                  </Typography>
                </Typography>
              ) : (
                <div>
                  <div className="grid grid-cols-11">
                    <div class="col-span-5">
                      <Typography
                        component="p"
                        variant="body2"
                        style={{
                          textAlign: "left",
                          color: "white",
                        }}
                      >
                        Machine Address
                      </Typography>
                    </div>
                    <div class="col-span-6">
                      <Typography
                        variant="body2"
                        style={{
                          textalign: "left",
                          color: "white",
                        }}
                      >
                        {extra_info.machineAddress}
                      </Typography>
                    </div>
                  </div>

                  <div className="grid grid-cols-11">
                    <div class="col-span-5">
                      <Typography
                        component="p"
                        variant="body2"
                        style={{
                          textAlign: "left",
                          color: "white",
                        }}
                      >
                        User
                      </Typography>
                    </div>
                    <div class="col-span-6">
                      <Typography
                        variant="body2"
                        style={{
                          textalign: "left",
                          color: "white",
                        }}
                      >
                        {extra_info.userName}
                      </Typography>
                    </div>
                  </div>

                  <div className="grid grid-cols-11">
                    <div class="col-span-5">
                      <Typography
                        component="p"
                        variant="body2"
                        style={{
                          textAlign: "left",
                          color: "white",
                        }}
                      >
                        MongoDB ID
                      </Typography>
                    </div>
                    <div class="col-span-6">
                      <Typography
                        variant="body2"
                        style={{
                          textalign: "left",
                          color: "white",
                        }}
                      >
                        {extra_info.mongodbID}
                      </Typography>
                    </div>
                  </div>
                  <div
                    style={{
                      textAlign: "left",
                    }}
                  >
                    <TooltipComponent content="Submit" position="BottomLeft">
                      <button
                        type="Disconnect"
                        onClick={(e) => handleClick(e)}
                        class="bg-white hover:bg-gray-100 text-gray-800 py-3 px-5 text-s border border-gray-400 rounded shadow"
                        style={{
                          textAlign: "left",
                          marginTop: "10%",
                        }}
                      >
                        Disconnect
                      </button>
                    </TooltipComponent>
                  </div>
                </div>
              )}
            </CardContent>
          </Collapse>
        </Card>
      </CardWrapper>
    </div>
  );
};

export default AnimatedStatusCard;
