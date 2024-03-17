FROM docker.io/python:3.11

ENV \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

ADD requirements.txt /usr/src/

WORKDIR /usr/src

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y binutils libproj-dev gdal-bin postgresql-client libevent-dev curl default-libmysqlclient-dev libsasl2-dev libgdal-dev libspatialindex-dev

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install -r requirements.txt

RUN pip install numpy
RUN pip install gdal==$(gdal-config --version) 

COPY . .

EXPOSE 8000


