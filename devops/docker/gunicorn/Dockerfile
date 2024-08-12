FROM python:3.10.13-alpine3.18

# ToDo: Re-visit whether secret key etc needed in Gunicorn Dockerfile
#ENV POSTGRES_DB=${POSTGRES_DB_NAME}
#ENV POSTGRES_USER=${POSTGRES_USER}
#ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
#ENV SECRET_KEY=${DJANGO_SECRET_KEY}
#ENV DJANGO_ENVIRONMENT=${DJANGO_ENVIRONMENT_TYPE}

WORKDIR /app

# Need to copy in requirements.txt and entrypoint.sh before they can be run

COPY ./requirements.txt /
COPY devops/docker/gunicorn/entrypoint.sh /

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ENTRYPOINT ["sh", "/entrypoint.sh"]
