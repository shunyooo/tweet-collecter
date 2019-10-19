FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app

# mysql client
ENV MYSQL_PWD password
RUN echo "mysql-server mysql-server/root_password password $MYSQL_PWD" | debconf-set-selections \
	&& echo "mysql-server mysql-server/root_password_again password $MYSQL_PWD" | debconf-set-selections \
	&& apt-get update && apt-get -y install mysql-server mysql-client tzdata \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install pip setuptools -U && pip install --upgrade pip && pip install -r /tmp/requirements.txt

# timezone 設定
ENV TZ Asia/Tokyo
RUN echo "${TZ}" > /etc/timezone \
   && dpkg-reconfigure -f noninteractive tzdata