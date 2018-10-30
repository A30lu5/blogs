FROM ubuntu:16.04

RUN sed -i "s/http:\/\/archive.ubuntu.com/http:\/\/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y python-pip  

COPY ./src /home
COPY ./flag /flag
WORKDIR /home

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/requirements.txt

CMD ["python","/home/app.py"]
