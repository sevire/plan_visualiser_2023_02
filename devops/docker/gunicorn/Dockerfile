FROM python:3.10.13-alpine3.18

WORKDIR /app

# Need to copy in requirements.txt and entrypoint.sh before they can be run
COPY ./requirements.txt /
COPY devops/docker/gunicorn/entrypoint.sh /

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ENTRYPOINT ["sh", "/entrypoint.sh"]
