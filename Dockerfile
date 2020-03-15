FROM ubuntu:18.04

RUN apt-get update -y \
	&& apt-get install -y chromium-chromedriver python3-pip \
	&& mkdir /crayon

WORKDIR /crayon
ADD . .

RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
