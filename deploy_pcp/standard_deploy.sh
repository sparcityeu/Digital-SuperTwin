echo 'Run this script as super user'

apt-get install pcp
. /etc/pcp.env

cd $PCP_PMDAS_DIR
cd xfs
./Remove



