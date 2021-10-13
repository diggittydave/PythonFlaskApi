#/bin/bash
#stop script for dev server
svn=`ps -fu $app_user --forest|grep svnUpdate|grep -v grep|awk '{print $2}'`
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
        fi
else
        echo 'The SVN Process is not currently running'
fi

