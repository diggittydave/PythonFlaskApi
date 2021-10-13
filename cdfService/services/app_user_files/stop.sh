#/bin/bash
#stop script for dev server
pid=`cat /prod/svc/cdfsvc/pid.status`
echo 'PID is' $pid
echo 'Child processes:'
ps -fu cdfsvc --forest|grep gunicorn|grep -v grep|awk '{print $2}'|grep -v $pid
echo ''
read -p "Are you sure you wish to kill the service? (y/n) " command1
if [ $command1 == 'y' ]
then
        echo 'killing master' $pid
        kill $pid
else
        echo 'not killing master'
fi
svn=`ps -fu cdfsvc --forest|grep svnUpdate|grep -v grep|awk '{print $2}'`
if [ $svn ]
then
        echo 'The SVN process is still running.'
        echo $svn
        read -p "Would you like to stop the SVN UPDATE worker? (y/n) " command2
        if [ $command2 == 'y' ]
        then
                echo 'killing SVN Update worker'
                kill $svn
        else
                echo 'not killing SVN Update Worker'
                echo 'you will need to manually kill the process later'
        fi
fi
