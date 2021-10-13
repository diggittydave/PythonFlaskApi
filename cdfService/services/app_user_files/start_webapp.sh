#/bin/bash
#start script for dev server
#check if app is already running
pid=`cat $appdir/pid.status`
webapp_pid=`ps -fu $app_user|grep "gunicorn"|head -1|awk '{print $2}'`
#test the pid
if [ $pid ] and [ $pid -ne $webapp_pid ];
then
    echo 'There is a stale pid file.'
    echo 'removing the stale pid file'
    rm $appdir/pid.status
fi
if [ $pid ] and [ $pid -eq $webapp_pid ];
then
    #if already running, and the status matches the file, the webapp startup skips
    echo 'THE WEBAPP IS ALREADY RUNNING WITH PID ' $pid
    echo 'MOVING ON TO THE SVN WORKER'
    pid2=`cat $appdir/pid.status`
    sleep 2
else
    #if not running the webapp starts
    echo 'STARTING CDF SERVICE WORKERS'
    # change do the app directory
    cd $appdir
    # start the virtual environment
    . ./venv/bin/activate
    # start the webapp
    gunicorn -c config.py run:app > /dev/null 2>&1 &
    # sleep to allow startup.
    sleep 5
    pid2=`cat $appdir/pid.status`
    if [ $pid2 ];
    then
        echo 'WEBAPP STARTUP COMPLETE'
    else
        $pid2='STARTUP FAILED. PLEASE CHECK THE LOGS FOR ERRORS.'
    fi
fi
#show the webapp primary pid
echo 'WEBAPP PRIMARY PROCESS ID:'
echo $pid2
echo 'WEBAPP LOGS: '
echo "$appdir/logs/worker_logs.log"
