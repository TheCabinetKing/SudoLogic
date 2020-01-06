FROM python:3.7.2-slim


#Set up sumosv in /app. Slackcommon will be copied into /app/slackcommon, etc.
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy sumosv files to worker's container
COPY ./config/slack_config.ini /usr/src/app/config/slack_config.ini
COPY ./slackcommon/slackcommon.py /usr/src/app/slackcommon/slackcommon.py
COPY ./sumosv/sumosv.py /usr/src/app/sumosv.py

#CMD ["rq","worker","default", "--url=redis://${REDIS_HOST}:${REDIS_PORT}"] --> does not work
CMD rq worker default --url=redis://${REDIS_HOST}:${REDIS_PORT}


