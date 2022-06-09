echo 'WARNING! Run this script as super user'

##Get keys and such
#wget -qO - https://pcp.io/GPG-KEY-PCP | sudo apt-key add -
#echo 'deb https://performancecopilot.jfrog.io/artifactory/pcp-deb-release focal main' | sudo tee -a /etc/apt/sources.list
#sudo apt-get update

#Install pcp
apt-get install pcp
. /etc/pcp.env


##Somewhere here, probe evtinfo and generate xxxconfig.dstconf
cd $PCP_PMDAS_DIR
cd xfs
./Remove


cd $PCP_PMDAS_DIR
cd perfevent
./Install
