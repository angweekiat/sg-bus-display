FROM python:3.10.12-slim

WORKDIR /opt/
COPY ./requirements.txt ./
RUN pip3 install -r ./requirements.txt
COPY ./index.html ./server.py ./

CMD ["python3", "./server.py"]