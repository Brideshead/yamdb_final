FROM python:3.7-slim
WORKDIR /app
COPY /api_yamdb/requirements.txt .
run pip install --upgrade pip
RUN pip3 install -r /api_yamdb/requirements.txt --no-cache-dir
COPY /api_yamdb/ .
ENV PYTHONPATH /app/api_yamdb
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
