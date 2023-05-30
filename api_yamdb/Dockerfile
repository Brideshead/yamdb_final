FROM python:3.7-slim

WORKDIR /app

COPY /api_yamdb/requirements.txt .

RUN pip3 install --upgrade pip
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip3 install -r requirements.txt 

ENV PYTHONPATH "${PYTHONPATH}:."

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:5000" ]

#hello