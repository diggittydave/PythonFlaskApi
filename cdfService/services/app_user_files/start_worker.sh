#/bin/bash
#svnWorker start script
svnWorker=`ps -ef|grep $app_user|grep "cdfService.svnServices.svnUpdate"|grep -v "grep"|awk '{print $2}'`
if [ $svnWorker ];then
    #if already running return warning
    echo 'SVN WORKER IS ALREADY RUNNING WITH PID ' $svnWorker
    # set variable for later return
    svnWorker2=`ps -ef|grep $app_user|grep "cdfService.svnServices.svnUpdate"|grep -v "grep"|awk '{print $2}'`
    sleep 2
else
    # if not running start the worker
    echo 'STARTING SVN UPDATE WORKER'
    #change to the app directory
    cd $appdir
    #start the virtual environment
    . ./venv/bin/activate
    # start the update module
    python -m cdfService.svnServices.svnUpdate > /dev/null 2>&1 &
    #sleep to allow startup time.
    sleep 5
    #check if its running.
    svnWorker2=`ps -ef|grep cdfsvc|grep "cdfService.svnServices.svnUpdate"|grep -v "grep"|awk '{print $2}'`
    if [ $svnWorker2 ];then
        #if running return success
        echo 'SVN WORKER STARTUP COMPLETE'
    else
        #if not running return failure
        svnWorker2='SVN WORKER FAILED TO START. PLEASE CHECK THE LOGS'
    fi
fi
#show the svn worker process.
echo 'SVNWORKER PROCESS ID:'
echo $svnWorker2
echo 'SVN WORKER LOGS:'
echo "$appdir/logs/dblog.log"
