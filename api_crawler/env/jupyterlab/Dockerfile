FROM syunyooo/jupyterlab
MAINTAINER Shunyo Kawamoto

# mysql client
ENV MYSQL_PWD password
RUN echo "mysql-server mysql-server/root_password password $MYSQL_PWD" | debconf-set-selections \
	&& echo "mysql-server mysql-server/root_password_again password $MYSQL_PWD" | debconf-set-selections \
	&& apt-get update && apt-get -y install mysql-server mysql-client libmysqlclient-dev libcurl4-openssl-dev libssl-dev python3.7-dev tzdata \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

# install additional python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install pip setuptools -U && pip install --upgrade pip && pip install -r /tmp/requirements.txt

# timezone settings
ENV TZ Asia/Tokyo
RUN echo "${TZ}" > /etc/timezone \
   && dpkg-reconfigure -f noninteractive tzdata