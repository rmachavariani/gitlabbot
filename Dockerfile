FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get install -y --no-install-recommends gfortran
RUN pip3 install uwsgi

COPY ./requirements.txt /magentologybot/requirements.txt

RUN pip3 install -r /magentologybot/requirements.txt

COPY . /magentologybot

WORKDIR /magentologybot

CMD ["uwsgi", "--ini","uwsgi.ini"]
