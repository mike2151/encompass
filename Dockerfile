FROM ubuntu:18.04

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip python-virtualenv

RUN pip3 install --upgrade pip

RUN rm -rf /var/lib/apt/lists/*

# install python libraries

# grab oracle java (auto accept licence)
# RUN add-apt-repository -y ppa:webupd8team/java
# RUN apt-get update
# RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
# RUN apt-get install -y oracle-java8-installer

# Define working directory and install python
COPY docker-python-dep.txt /data/requirements.txt
WORKDIR /data
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

# install pycreate
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

WORKDIR /
RUN git clone https://github.com/Falldog/pyconcrete.git
WORKDIR /pyconcrete
RUN printf "encompassisking786254\nencompassisking786254\n" | python3 setup.py install
WORKDIR /
RUN rm -rf pyconcrete
