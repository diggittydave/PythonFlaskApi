#/bin/bash
#start script for dev server
#check if app is already running
pid=`cat $appdir/pid.status`
webapp_pid=`ps -fu $app_user|grep "gunicorn"|head -1|awk '{print $2}'`
#test the pid
if [ $pid ] and [ $pid -eq $webapp_pid ];
then
    #if already running, and the status matches the file, the webapp startup skips
    echo 'THE WEBAPP IS ALREADY RUNNING WITH PID ' $pid
    echo 'MOVING ON TO THE SVN WORKER'
    pid2=`cat $appdir/pid.status`
    sleep 2
elif [ $pid ] and [ $pid -ne $webapp_pid ];
then
    echo 'There is a stale pid file. Removing and attempting restart'
    rm $appdir/pid.status
    echo "starting..."
    /export/home/cdfsvc/start_webapp
    webapp_pid2=`ps -fu $app_user|grep "gunicorn"|head -1|awk '{print $2}'`
    if [ $webapp_pid2 ];then
        echo 'WEBAPP STARTUP COMPLETE'
    else
        $webapp_pid2='STARTUP FAILED. PLEASE CHECK THE LOGS FOR ERRORS.'
    fi
else
    start_webapp
    pid2=`cat $appdir/pid.status`
    if [ $pid2 ];then
        echo 'WEBAPP STARTUP COMPLETE'
    else
        $pid2='STARTUP FAILED. PLEASE CHECK THE LOGS FOR ERRORS.'
    fi
fi
svnWorker=`ps -ef|grep cdfsvc|grep "cdfService.svnServices.svnUpdate"|grep -v "grep"|awk '{print $2}'`
if [ $svnWorker ];then
    #if already running return warning
    echo 'SVN WORKER IS ALREADY RUNNING WITH PID ' $svnWorker
    # set variable for later return
    svnWorker2=`ps -ef|grep cdfsvc|grep "cdfService.svnServices.svnUpdate"|grep -v "grep"|awk '{print $2}'`
    sleep 2
else
    #check if its running.
    start_worker
    sleep 5
    svnWorker2=`ps -ef|grep cdfsvc|grep "cdfService.svnServices.svnUpdate"|grep -v "grep"|awk '{print $2}'`
    if [ $svnWorker2 ];then
        #if running return success
        echo 'SVN WORKER STARTUP COMPLETE'
    else
        #if not running return failure
        svnWorker2='SVN WORKER FAILED TO START. PLEASE CHECK THE LOGS'
    fi
fi
#show the webapp primary pid
echo 'WEBAPP PRIMARY PROCESS ID:'
echo $pid2
echo 'WEBAPP LOGS: '
echo "/prod/svc/cdfsvc/logs/worker_logs.log"
#show the svn worker process.
echo 'SVNWORKER PROCESS ID:'
echo $svnWorker2
echo 'SVN WORKER LOGS:'
echo "/prod/svc/cdfsvc/logs/dblog.log"
