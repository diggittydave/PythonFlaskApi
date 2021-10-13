#/bin/bash
echo 'cdfsvc is running with the following processes'
echo ''
ps -fu $app_user --forest|grep "gunicorn"|grep -v grep
echo ''
echo ''
echo 'SVN UPDATE WORKER running with the following process'
ps -fu $app_user --forest|grep "svnUpdate"|grep -v grep
echo ''
