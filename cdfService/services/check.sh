#!/bin/bash
user= `whoami`
echo 'cdfsvc is running with the following processes'
echo ''
ps -fu $user --forest|grep "gunicorn"|grep -v grep
echo ''
echo ''
echo 'SVN UPDATE WORKER running with the following process'
ps -fu $user --forest|grep "svnUpdate"|grep -v grep
echo ''
