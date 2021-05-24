FROM ubuntu:19.10

# Environment
ARG container_code

ARG container_name

ENV container_name $container_name

ARG container_topic

ENV container_topic $container_topic

# Creating Application Source Code Directory
RUN mkdir -p /k8s_python_sample_code/src

# Setting Home Directory for containers
WORKDIR /k8s_python_sample_code/src

RUN apt-get update

RUN apt-get install -y python python-pip imagemagick && \
    apt-get update && \
    pip install --upgrade pip && \
    pip install --upgrade numpy Pillow scipy kafka-python

# Copying src code to Container
COPY . /k8s_python_sample_code/src

# Running Python Application
CMD python container_3.py $container_name $container_topic
