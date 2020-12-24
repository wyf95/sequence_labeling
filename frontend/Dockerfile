FROM node:14.15-alpine

WORKDIR /frontend

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
 && apk add --update --no-cache\
  bash git openssh-client python3 make g++