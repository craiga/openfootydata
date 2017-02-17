FROM python
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y wget

ENV DOCKERIZE_VERSION v0.3.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN mkdir /var/openfootydata
WORKDIR /var/openfootydata
ADD requirements.txt /var/openfootydata/
RUN pip install -r requirements.txt
ADD . /var/openfootydata/
