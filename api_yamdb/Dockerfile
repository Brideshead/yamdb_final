FROM python:3.7-slim
WORKDIR /app
COPY /api_yamdb/requirements.txt .
run pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY . .
ENV PYTHONPATH /app/api_yamdb
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
