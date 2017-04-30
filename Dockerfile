FROM centos:7.2.1511
MAINTAINER Daniel Kristof <kristofdan@yahoo.com>

ARG http_proxy
ARG https_proxy
ARG ftp_proxy

ENV http_proxy "$http_proxy"
ENV https_proxy "$https_proxy"
ENV ftp_proxy "$ftp_proxy"

RUN yum --disableplugin=fastestmirror -y update && yum clean all
RUN yum --disableplugin=fastestmirror -y install gd libxslt libxml2 git wget

RUN mkdir /usr/lbzip2 && cd /usr/lbzip2
RUN wget http://dl.fedoraproject.org/pub/epel/7/x86_64/l/lbzip2-2.5-1.el7.x86_64.rpm
RUN rpm -Uvh lbzip2-2.5-1.el7.x86_64.rpm

RUN mkdir /usr/local/maja && cd /usr/local/maja

ADD maja-1.0.0-rhel.7.2.x86_64-release-gcc.tar /usr/local/maja/
ADD maja-cots-1.0.0-rhel.7.2.x86_64-release-gcc.tar /usr/local/maja/

RUN cd /usr/local/maja/maja-cots-1.0.0-rhel.7.2.x86_64-release-gcc && echo 'Y'|./install.sh
RUN cd /usr/local/maja/maja-1.0.0-rhel.7.2.x86_64-release-gcc && echo 'Y'|./install.sh

RUN cd /opt/maja
RUN git clone https://github.com/olivierhagolle/Start_maja
RUN cd Start_maja && rm folders.txt
ADD folders.txt /opt/maja/Start_maja
