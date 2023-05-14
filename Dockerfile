FROM python:3.11
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -U pip && pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
