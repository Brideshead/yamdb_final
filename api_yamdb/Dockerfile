FROM python:3.7-slim

WORKDIR /app

COPY . .

RUN pip3 install --upgrade pip
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip3 install -r /api_yamdb/requirements.txt --no-cache-dir

ENV PYTHONPATH "${PYTHONPATH}:."

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:5000" ]