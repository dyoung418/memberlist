FROM python:3

RUN useradd -m dev

COPY requirements.txt /tmp/
RUN pip install requests
RUN pip install -r /tmp/requirements.txt

COPY *.py /opt/

ENTRYPOINT /opt/memberList.py