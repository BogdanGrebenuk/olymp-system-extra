FROM python:3.7

WORKDIR /olymp-system-extra

COPY . /olymp-system-extra

RUN pip install -r requirements.txt
