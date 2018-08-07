FROM        ubuntu:18.04
MAINTAINER  Slavik Greshilov slovaricheg@gmail.com

RUN rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get dist-upgrade -y

COPY ./etc /async-aloha/etc
COPY ./server /async-aloha/server
COPY ./temp/dist /async-aloha/frontend/dist
COPY ./temp/pyalohareciever.so /async-aloha/server/pyalohareciever.so

RUN apt-get install -y \
    bash \
    cron \
    libboost-python1.65.1 \
    postgresql-client \
    python3-pip

RUN pip3 install -r /async-aloha/etc/requirements.txt

WORKDIR /async-aloha/server

CMD ["/bin/bash", "/async-aloha/etc/cbin/run.sh"]
