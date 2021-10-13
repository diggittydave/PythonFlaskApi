# User specific aliases and functions

export PATH=$PATH:/opt
export PATH=$PATH:/opt/python-3.6.9/bin
export PATH=$PATH:/prod/svc/cdfsvc/app
export FLASK_APP=app.py

# primary application location
appdir='/prod/svc/$app_user/cdfservice'

# primary application account home directory
# homedir='/export/home/$app_user'

# change to the logs directory for the app
alias logs='cd $appdir/logs'

# quickly open and follow the weblogs to see service calls
alias weblogs='tail -100f $appdir/logs/worker_logs.log'

# change to the app directory
alias app='cd $appdir'

# change to the repository directory
alias repo='cd $appdir/repository'

# start the webapp server
alias start='$homedir/start'

# stop the webapp server
alias stop='$homedir/stop'

# check the processes of the app server.
alias check='$homedir/check'

# start the virtual environment
alias venv='. $appdir/venv/bin/activate'

# change to the database directory
alias data='cd $appdir/cdfService/database'

#restart both webapp and svn update worker
alias restart='$homedir/stop;sleep 5;$homedir/start'

#stop only the svn update worker
alias stop_worker='$homedir/stop_worker'


#start the svn update worker only
alias start_worker='$homedir/start_worker'

#restart the worker only.
alias restart_worker='$homedir/stop_worker;echo "worker stopped";sleep 5:echo "starting worker";$homedir/start_worker'

#stop only the webapp.
alias stop_webapp='$homedir/stop_webapp'

#start the webapp only.
alias start_webapp='$homedir/start_webapp'

#restart the webapp only
alias restart_webapp='$homedir/stop_webapp;sleep 5;$homedir/start_webapp'
