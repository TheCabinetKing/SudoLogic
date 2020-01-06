FROM python:3.7.2-slim


#Set up sumosv in /app. Slackcommon will be copied into /app/slackcommon, etc.
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

#CMD ["rq","worker","default", "--url=redis://${REDIS_HOST}:${REDIS_PORT}"] --> does not work
CMD rq worker default --url=redis://${REDIS_HOST}:${REDIS_PORT}


