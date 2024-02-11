FROM python:3.10.13-alpine3.18

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

WORKDIR /app

ENTRYPOINT ["sh", "./entrypoint.sh"]
