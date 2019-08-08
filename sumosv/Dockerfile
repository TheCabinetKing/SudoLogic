FROM python:3.7.2-slim

#Set up sumosv in /app. Slackcommon will be copied into /app/slackcommon, etc.
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./slackcommon/slackcommon.py /usr/src/app/slackcommon/slackcommon.py
COPY ./sumosv/sumosv.py /usr/src/app/sumosv.py

#Expose port 80 for Sumo access.
EXPOSE 5000
CMD ["flask","run"]