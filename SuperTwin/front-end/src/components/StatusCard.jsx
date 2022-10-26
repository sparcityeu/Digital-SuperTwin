import * as React from "react";
import { useState } from "react";
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

const AnimatedStatusCard = (group_id, extra_info, status) => {
  const classes = useStyles();
  const [expanded, setExpanded] = useState(false);
  const [checked, setChecked] = useState(false);

  const handleChange = (e) => {
    setChecked(e.target.checked);
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
          }}
        >
          <CardContent>
            <Typography style={{ paddingBottom: "1rem", color: "#212329" }}>
              Metric Group-{group_id}
            </Typography>
            <Typography variant="body2" component="p">
              {extra_info}
            </Typography>
          </CardContent>
          <CardActions
            disableSpacing
            style={{
              backgroundColor: "#212329 ",
            }}
          >
            <Typography color="common.white">Metric</Typography>

            <IconButton
              style={{ color: "black" }}
              className={clsx(classes.expand, {
                [classes.expandOpen]: expanded,
              })}
              onClick={(id) => handleExpandClick(group_id)}
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
              <Typography paragraph>
                <Typography varian="body1" color="common.white" key={status}>
                  {status}
                </Typography>
              </Typography>
            </CardContent>
          </Collapse>
        </Card>
      </CardWrapper>
    </div>
  );
};

export default AnimatedStatusCard;
