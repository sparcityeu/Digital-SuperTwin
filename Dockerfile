FROM ubuntu:22.04

#Optional - rather can clone repo in the container
COPY ./*/ root/Digital-SuperTwin/

#Run with "docker run -it --privileged --network="host" <image-name>" settings

RUN apt update
RUN apt-get -y install sudo
RUN apt-get -y install python3
RUN apt-get -y install pip
RUN pip install influxdb
RUN pip install pymongo
RUN pip install paramiko
RUN pip install scp
RUN pip install flask
RUN pip install grafanalib
RUN pip install plotly
RUN pip install flask_cors
RUN pip install pandas

RUN apt-get -y install pcp
RUN apt-get -y install ssh
RUN apt-get -y install firewalld
RUN apt-get -y install pcp-export-pcp2influxdb
RUN apt-get -y install vim

EXPOSE 5000 8086 27017 3000

CMD /etc/init.d/pmcd start && /etc/init.d/pmlogger start && /etc/init.d/pmie start && /etc/init.d/pmproxy start /etc/init.d/ssh start && bash
