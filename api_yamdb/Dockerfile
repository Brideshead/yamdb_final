FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]
