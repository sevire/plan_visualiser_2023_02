FROM python:3.10.13-alpine3.18

ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV SECRET_KEY='c*48+8)np*$4ohvxr38x=)(w4vw3!shqm*+m+%v$uzn!q@wk%+'
ENV DEBUG=False
ENV DJANGO_ENVIRONMENT=production

WORKDIR /app

# Need to copy in requirements.txt and entrypoint.sh before they can be run

COPY ./requirements.txt /
COPY devops/docker/gunicorn/entrypoint.sh /

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ENTRYPOINT ["sh", "/entrypoint.sh"]
