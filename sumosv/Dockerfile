FROM python:3.7.2-slim

#Set up sumosv in /app. Slackcommon will be copied into /app/slackcommon, etc.
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt
# for some reasons, gunicorn can be executable if it is included in the requirements.txt
# but if is installed separately like below it works ok.
RUN pip install gunicorn

COPY ./slackcommon/slackcommon.py /usr/src/app/slackcommon/slackcommon.py
COPY ./sumosv/sumosv.py /usr/src/app/sumosv.py

EXPOSE ${FLASK_RUN_PORT}

# CMD ["flask","run"]  or CMD ["python","sumosv.py"] for development

# Use Gunicorn for production
CMD gunicorn -b ${FLASK_RUN_HOST}:${FLASK_RUN_PORT} sumosv:app
