FROM python:3.9

RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 50505

WORKDIR /App

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:50505", "app:app"]