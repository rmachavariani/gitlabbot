ARG APP_IMAGE=python:3.8-slim-buster

FROM $APP_IMAGE AS base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip3 install --prefix /install -r /requirements.txt

FROM base
ENV FLASK_APP app/app.py
WORKDIR /magentologybot
COPY --from=builder /install /usr/local
ADD . /magentologybot

ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]