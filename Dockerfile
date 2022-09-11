FROM nvidia/cuda:11.7.1-base-ubuntu18.04

RUN apt-get -y update \
    && apt-get install -y software-properties-common \
    && apt-get -y update \
    && add-apt-repository universe \
    && add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get -y update
RUN apt-get -y install python3.8 python3.8-distutils wget
RUN wget https://bootstrap.pypa.io/get-pip.py

RUN ln -s python3.8 /usr/bin/python
RUN python3.8 get-pip.py

COPY requirements.txt .
RUN pip install --upgrade -r requirements.txt