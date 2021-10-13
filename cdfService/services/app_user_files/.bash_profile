# User specific environment and startup programs

PATH=$PATH:$HOME/bin:/opt/CollabNet_Subversion/bin:$M2_HOME/bin

export PATH
if [ -f ~/.profile ]; then . ~/.profile; fi

# For Maven:
#export MAVEN_OPTS="-Xmx2048m -XX:+UseG1GC -d64"
export M2_HOME="/opt/apache-maven-3.3.9"


# for cdfsvc api
export SECRET_KEY='5791628bb0b13ce0c676fde280ba245'
export SQLALCHEMY_DATABASE_URI='sqlite:////prod/svc/cdfsvc/cdfservice/cdfService/database/CDF_INFO.sqlite'
export SECRET_TOKEN=''
export SEVER_URL='https://elasticdev004.chq.ei:8200'
export SERVER_CERT='/prod/svc/cdfsvc/cdfService/services/ca_certs.pem'
export CA_CERTS='/prod/svc/cdfsvc/cdfService/services/ca_certs/pem'
export MAIL_SERVER='exch-smtp.expeditors.com'
export MAIL_PORT='587'


#alias variables
export app_user=`whoami`
export appdir="/prod/svc/$app_user/cdfservice"
# primary application account home directory
export homedir="/export/home/$app_user"

