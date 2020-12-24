FROM python:3.8.6-slim-buster

WORKDIR /backend

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
 && sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
 && apt-get clean

RUN apt-get update \
 && apt-get install -y \
    netcat=1.10-41.1 \
    libpq-dev=11.9-0+deb10u1 \
    unixodbc-dev=2.3.6-0.1 \
    g++=4:8.3.0-1

COPY ./requirements.txt /backend

RUN pip install --upgrade --no-cache-dir pip setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple \
 && pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
