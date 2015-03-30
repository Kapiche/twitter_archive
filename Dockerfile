FROM ubuntu:14.10
MAINTAINER Ryan Stuart <ryan@kapiche.com>

# Install packages
RUN \
    apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        python \
        python-dev \
        python-psycopg2 \
        python-setuptools \
        software-properties-common \
        sqlite3 \
        supervisor \
        zlib1g-dev

# Install Nginx
RUN add-apt-repository -y ppa:nginx/stable
RUN \
    apt-get update &&  \
    apt-get install -y ca-certificates nginx && \
    rm -rf /var/lib/apt/lists/*

# Setup the application
RUN easy_install -U pip
RUN pip install uwsgi

# install our code
ADD . /home/docker/code/

# Setup configs
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /home/docker/code/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /home/docker/code/supervisor-app.conf /etc/supervisor/conf.d/

# Install app requirements and setup environment
ENV PYTHONUNBUFFERED=1
RUN pip install -r /home/docker/code/requirements.txt
RUN mkdir /home/docker/csvs
WORKDIR /home/docker/code
VOLUME /var/csvs
RUN python manage.py collectstatic --noinput && \
    chown -R www-data:www-data /home/docker/static
