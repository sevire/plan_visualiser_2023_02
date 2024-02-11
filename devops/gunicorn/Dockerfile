FROM python:3.10.13-alpine3.18

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

ENTRYPOINT ["sh", "./entrypoint.sh"]
