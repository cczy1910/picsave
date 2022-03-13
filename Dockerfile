FROM python:3.9

WORKDIR /server/

ADD . /server/

# opencv
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

RUN pip install -r requirements.txt
