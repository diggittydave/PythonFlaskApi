***************************************************************************************************
**                                                                                               **
**                                 CDFService v.2021.01.07-master                                **
**                                                                                               **
**                        authored by: David Weber, Systems Analyst II                           **
**                        email: david.weber@expeditors.com                                      **
***************************************************************************************************

The CDF Service is a combination Web site/api service created to ensure data integrity between SVN
repositories and Service Catalog.
The application is written in Python utilizing Flask, SqlLite, and gunicorn.
The primary function is to return up to date valid data to API service calls made by service
catalog. The requests will be for lists of available cdfs, and data relating to a single cdf to
include Name, Service, restrictions, and contents.
Secondary functions are a web interface useable by support personnel to update the restrictions
and maintain accounts. A worker process continuously runs to update the cdf database available.
Future versions will include automation to receive a post request from Service Catalog to
automatically validate and update a cdf based on user input on the service catalog form.



***************************************************************************************************
**                                                                                               **
**                                     PROGRAM DEPENDENCIES                                      **
**                                                                                               **
***************************************************************************************************

1. Operating system:
    A. Linux x86_64 [RHEL image 6.0]
2. Python 3.6.9
    A. This requires python to be installed and fully readable by the app account.
    B. remote repositores set to internal nexus repos:
        i. global.index 'http://nexusrepo.chq.ei:8392/nexus/repository/pypi-proxy/pypi'
        ii. global.index-url 'http://nexusrepo.chq.ei:8392/nexus/repository/pypi-group/simple'
        iii. global.trusted-host 'nexusrepo.chq.ei'
3. Apache SVN.
    A. SVN is the primary cdf repository/version control system.
    B. Two repositories are checked out by the app:
        i. URL: http://edi-repo.chq.ei:8391/svnedi/edirepo/EDIGen/prod/cdfs
            a. location to be set on app server: /prod/svc/cdfsvc/cdfservice/repository/cdfs/cdfs
        ii. URL: http://edi-repo.chq.ei:8391/svnedi/webmethods-resources/resources/prod
            b. location to be set on app serfver: /prod/svc/cdfsvcqa/cdfservice/repository/prod/prod
4. git.
    A. Git houses the app code. A git clone must be used to install the application.
    B. Primary git repository:
        i. git@gitlab.chq.ei:AppSupport/edi-support/cdfservice.git
5. cdfsvc service account.
    A. The service account should be cdfsvc and the primary production partent folder should be
        i. /prod/svc/cdfsvc/
    B. App account should be:
        i. /export/home/cdfsvc
6. Python Sub Packages required in nexus repo and their minimum versions:
    A. aniso8601==8.0.0
    B. astroid==2.2.0
    C. attrs==19.3.0
    D. bcrypt==3.1.7
    E. blinker==1.4
    F. certifi==2019.9.11
    G. cffi==1.13.1
    H. Click==7.0
    I. colorama==0.4.1
    J. cryptography==2.8
    K. dominate==2.4.0
    L. elastic-apm==5.3.2
    M. Flask==1.1.1
    N. Flask-Bcrypt==0.7.1
    O. Flask-Bootstrap==3.3.7.1
    P. Flask-Login==0.4.1
    Q. Flask-Mail==0.9.1
    R. flask-marshmallow==0.10.1
    S. Flask-RESTful==0.3.8
    T. flask-restful-swagger-2==0.35
    U. flask-restplus==0.13.0
    V. Flask-SQLAlchemy==2.4.1
    W. flask-swagger-ui==3.36.0
    X. Flask-WTF==0.14.2
    Y. gunicorn==20.0.4
    Z. importlib-metadata==1.6.1
    AA. inflect==5.0.2
    AB. isort==4.3.9
    AC. itsdangerous==1.1.0
    AD. Jinja2==2.10.3
    AE. jsonschema==3.2.0
    AF. lazy-object-proxy==1.3.1
    AG. MarkupSafe==1.1.1
    AH. marshmallow==3.2.1
    AI. marshmallow-sqlalchemy==0.19.0
    AJ. mccabe==0.6.1
    AK. pipenv==2018.11.26
    AL. pycparser==2.19
    AM. PyJWT==1.7.1
    AN. pylint==2.3.0
    AO. pyrsistent==0.16.0
    AP. pytz==2020.1
    AQ. PyYAML==5.3.1
    AR. safrs==2.10.4
    AS. six==1.12.0
    AT. sqlacodegen==2.3.0
    AU. SQLAlchemy==1.3.10
    AV. typed-ast==1.3.1
    AW. urllib3==1.25.7
    AX. virtualenv==16.7.5
    AY. virtualenv-clone==0.5.3
    AZ. visitor==0.1.3
    BA. Werkzeug==0.16.0
    BB. wrapt==1.11.1
    BC. WTForms==2.2
    BD. zipp==3.4.0




***************************************************************************************************
**                                                                                               **
**                                    Instalation Procedure                                      **
**                                                                                               **
***************************************************************************************************

Current procedures require the creation of a linux server via Service Catalog request.
Once the server is requested and stood up, The requester needs to log a ticket with the BCR Team.
The ticket should include a request to install required dependencies 1-5. The sub packages in
dependency 6 are installed in a later step via virtual environment setup.
Future procedures may change. IF so, when creating the server, ensure the above requirements are
met.

STEPS:
1. log into server using app account and password stored in team-pass.
2. Create ssh pub key to and add to your gitlab.chq.ei account.
    You can use the steps found here:
    https://gitlab.chq.ei/help/ssh/README#generating-a-new-ssh-key-pair
3. Navigate to install folder
    >cd /prod/svc/cdfsvc/cdfservice
4. clone the repository via ssh:
    >git clone git@gitlab.chq.ei:AppSupport/edi-support/cdfservice.git
    >git checkout master
5. Create and navigate into the svn repository folders and initiate each repository
    ***svn will require a username and password. There are two usernames/passwords stored in
    ***teampass. Multiple user accounts are for different prod servers.
    *** edicdfservice1
    *** edicdfservice2
    >mkdir repositories
    >cd repositories
    >mkdir cdfs
    >mkdir prod
    >cd ./cdfs/
    >svn co http://edi-repo.chq.ei:8391/svnedi/edirepo/EDIGen/prod/cdfs
    >cd ../prod
    >svn co http://edi-repo.chq.ei:8391/svnedi/webmethods-resources/resources/prod
6. initialize the install finisher script:
    >cd /prod/svc/cdfsvc/cdfservice/scripts
    >chmod 755 install_finish.sh
    >./install_finish.sh
    **** at this point the install will run several operations autmatically.
    **** Once finished the app will be up and running and accessible.



***************************************************************************************************
**                                                                                               **
**                                Startup//Check//Stop Webapp                                    **
**                                                                                               **
***************************************************************************************************

During the install process, three scripts are deployed to the service account home directory.
If linux sources the .bashrc file correctly, managinge the operation of the app is simple.
START:
1. Login to the server using the cdfsvc login and password.
2. at the command prompt:
    >start
3. The script checks for both the webapp and svn worker. It will start up either process if needed:
**** below is what you will see if neither process is running:
    cat: /prod/svc/cdfsvc/cdfservice/pid.status: No such file or directory
    STARTING CDF SERVICE WORKERS
    WEBAPP STARTUP COMPLETE
    STARTING SVN UPDATE WORKER
    SVN WORKER STARTUP COMPLETE
    WEBAPP PRIMARY PROCESS ID:
    110986
    WEBAPP LOGS:
    /prod/svc/cdfsvc/cdfservice/logs/worker_logs.log
    SVNWORKER PROCESS ID:
    111003
    SVN WORKER LOGS:
    /prod/svc/cdfsvc/cdfservice/logs/dblog.log
**** below is what you will see if the webapp process is running:
    THE WEBAPP IS ALREADY RUNNING WITH PID  111590
    MOVING ON TO THE SVN WORKER
    STARTING SVN UPDATE WORKER
    SVN WORKER STARTUP COMPLETE
    WEBAPP PRIMARY PROCESS ID:
    111590
    WEBAPP LOGS:
    /prod/svc/cdfsvc/cdfservice/logs/worker_logs.log
    SVNWORKER PROCESS ID:
    111642
    SVN WORKER LOGS:
    /prod/svc/cdfsvc/cdfservice/logs/dblog.log
**** below is what you will see if the svn worker is running:
    cat: /prod/svc/cdfsvc/cdfservice/pid.status: No such file or directory
    STARTING CDF SERVICE WORKERS
    WEBAPP STARTUP COMPLETE
    SVN WORKER IS ALREADY RUNNING WITH PID  111642
    WEBAPP PRIMARY PROCESS ID:
    111688
    WEBAPP LOGS:
    /prod/svc/cdfsvc/cdfservice/logs/worker_logs.log
    SVNWORKER PROCESS ID:
    111642
    SVN WORKER LOGS:
    /prod/svc/cdfsvc/cdfservice/logs/dblog.log

STOP:
1. Login to the server using the cdfsvc login and password.
2. The script will ask two questions.
3. You can stop either the webapp, the svn worker, or both.
2. At the command prompt:
    >stop
    PID is 97606
    Child processes:
    97610
    97611
    97612

    Are you sure you wish to kill the service? (y/n) y
    killing master 97606
    The SVN process is still running.
    97623
    Would you like to stop the SVN UPDATE worker? (y/n) y
    killing SVN Update worker

CHECK:
1. Login to the server using the cdfsvc login and password.
2. The script checks both the webapp and the svn worker.
3. At the command prompt:
    >check
4. Below are possible outputs:
**** If both webapp and svn worker are running:
    cdfsvc is running with the following processes

    cdfsvc   111688      1  0 21:43 pts/0    00:00:00 /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app
    cdfsvc   111692 111688  0 21:43 pts/0    00:00:00  \_ /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app
    cdfsvc   111693 111688  0 21:43 pts/0    00:00:00  \_ /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app
    cdfsvc   111694 111688  0 21:43 pts/0    00:00:00  \_ /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app

    SVN UPDATE WORKER running with the following process
    cdfsvc   111642      1  0 21:41 pts/0    00:00:01 python -m cdfService.svnServices.svnUpdate

**** If only the webapp is running:
    cdfsvc is running with the following processes

    cdfsvc   111688      1  0 21:43 pts/0    00:00:00 /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app
    cdfsvc   111692 111688  0 21:43 pts/0    00:00:00  \_ /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app
    cdfsvc   111693 111688  0 21:43 pts/0    00:00:00  \_ /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app
    cdfsvc   111694 111688  0 21:43 pts/0    00:00:00  \_ /prod/svc/cdfsvc/cdfservice/venv/bin/python3.6 /prod/svc/cdfsvc/cdfservice/venv/bin/gunicorn -c config.py run:app

    SVN UPDATE WORKER running with the following process

**** if only the svn worker is running:
    cdfsvc is running with the following processes

    SVN UPDATE WORKER running with the following process
    cdfsvc   112904      1  4 21:51 pts/0    00:00:00 python -m cdfService.svnServices.svnUpdate

**** If neither process is running:
    cdfsvc is running with the following processes

    SVN UPDATE WORKER running with the following process



***************************************************************************************************
**                                                                                               **
**                                  Endpoint Definitions                                         **
**                                                                                               **
***************************************************************************************************

The Webapp has several enpoints, some of which are accessible only via web browser, such as chrome.
Other endpoints are only accessible via api request calls. Below is a list of all endpoint
definitions. If an endpoint is input but doesn't exist, a user is sent back to the login page.

1.	'/'
    a.	Index page routes to login or about page if already logged in.
2.	'/webapp/about'
    a.	Requires login. Routes to login page if not already logged in.
    b.	Homepage of the user interface.
3.	'/webapp/login'
    a.	Login page for accessing user web interface functions.
    b.	Routes to ‘/about’ if already logged in.
4.	'/webapp/logout'
    a.	Route to initiate a logout of the user from the web interface.
5.	'/webapp/users'
    a.	Requires login. Routes to login page if not already logged in.
    b.	This route contains the user table data.
    c.	Users can be added on this page.
    d.	Future functionality will include deletion.
    e.	Only admins can access this route.
6.	‘/api/user/create’
    a.	Requires token access.
    b.	Only accessed by API call by admin user.
    c.	Used to create new API users.
7.	‘/api/user/update’
    a.	Requires token access.
    b.	Only accessed by API call by admin user.
    c.	Used to update password of API users.
8.	'/webapp/register'
    a.	Routes to login page if not already logged in.
    b.	Original page designed for only adding new users.
    c.	Will most likely be removed in future versions.
9.	'/webapp/account'
    a.	This route is unfinished.
    b.	Future contents will include password change, permissions requests, email change.
10.	'/filter_switch'
    a.	Requires login. Routes to login page if not already logged in.
    b.	Shows currently available filter types.
    c.	Requires user to have permissions.
    d.  Links to /webapp/filter_switch/<RESTRICTION>
11.	'/webapp/filter_switch/<RESTRICTION>'
    a.	Requires login. Routes to login page if not already logged in.
    b.	Access the current filters list based on the chosen RESTRICTION type.
    c.	Filters can be added on this page.
    d.	Requires user to have permissions.
12.	‘/webapp/filter/<RESTRICTION>’
    a.	Requires login. Routes to login page if not already logged in.
    b.	Requires permissions to access filters.
    c.	Linked from the ‘/filter_switch/<RESTRICTION>’ endpoint.
    d.	Contains only the selected filter.
    e.	Used to remove the filter if needed.
13.	‘/webapp/filters/reload’
    a.	Requires login. Routes to login page if not already logged in.
    b.	Linked from ‘/filters’ page.
    c.	Page contains username/password verification to start reload function.
    d.	Function reloads all flags for all .cdf files in database based on filters.
    e.	Should be used after adding/removing multiple filters.
14.	‘/api/token_gen’
    a.	Used by service catalog to generate x-access-token.
    b.	After successful authentication, returns x-access-token for future use.
    c.	Tokens are currently only valid for 30 minutes.
15.	‘/cdf/list’
    a.	Endpoint accessed by service catalog only.
    b.	Requires valid token to access.
    c.	Returns a complete and current list of all cdf’s available.
    d.	List contains names of cdf’s and their id_key.
16.	‘/api/cdf/list/<key>’
    a.	Endpoint accessed by Service catalog only.
    b.	Requires valid token access.
    c.	Uses the provided <key> to return a limited list of results.
    d.	<key> is sent by service catalog based on user input.
    e.	Return list contains cdf names and their id_key.
17.	‘/api/cdf/ID_KEY/<ID_KEY>’
    a.	Endpoint accessed by Service Catalog Only.
    b.	Requires valid token access.
    c.	Uses the provided <ID_KEY> to return all data on a single CDF.
18. '/webapp/services/webcheck'
    a. Webcheck endpoint
    b. Does not require any login information.
    c. Reports back several data elements:
        i. current memory use marked as "Free", Total, and Used memory.
        ii. Currently running webapp processes
        iii. currently running SVN Update process
        iiii. Current version of both Gen and Web repositories.