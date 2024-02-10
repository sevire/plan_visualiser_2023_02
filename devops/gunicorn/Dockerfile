FROM python:3.10.13-alpine3.18

RUN pip install --upgrade pip

COPY ../../requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

COPY ../../entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
