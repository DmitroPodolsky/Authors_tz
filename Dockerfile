FROM python:3.11.0

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

CMD [ "python", "-m", "src"]
