FROM python:3.10.13-alpine3.18

WORKDIR /app

# This is being run from the Github runner (or equivalent) so we don't have access to the project files at this point.
# So need to copy in requirements.txt and entrypoint.sh before they can be run

COPY ../../requirements.txt /
COPY ./devops/gunicorn/entrypoint.sh /

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ENTRYPOINT ["sh", "/entrypoint.sh"]
