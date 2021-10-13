#/bin/bash
#stop script for dev server
pid=`cat /prod/svc/$app_user/cdfservice/pid.status`
echo 'Master PID is' $pid
echo 'Child processes:'
ps -fu $app_user --forest|grep gunicorn|grep -v grep|awk '{print $2}'|grep -v $pid
echo ''
read -p "Are you sure you wish to kill the service? (y/n) " command1
if [ $command1 == 'y' ]
then
        echo 'killing master' $pid
        kill $pid
        echo 'removing old PID status files'
        rm /prod/svc/$app_user/cdfservice/pid.status
        echo "Process complete"
else
        echo 'not killing master'
fi