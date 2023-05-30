FROM python:3.7-slim
WORKDIR /app
COPY /api_yamdb/requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt
COPY /api_yamdb/ .
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]

#hello1