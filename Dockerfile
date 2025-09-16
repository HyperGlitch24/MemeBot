FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt . 

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . . 

EXPOSE 8501
EXPOSE 8000

CMD ["bash", "startup.sh"]
