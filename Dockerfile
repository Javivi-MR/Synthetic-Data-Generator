FROM python:3.9

ENV FLASK_APP ./App/main.py
ENV FLASK_RUN_HOST 0.0.0.0

RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "run"]