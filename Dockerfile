FROM python:3

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY *.py /opt/

ENTRYPOINT /opt/memberList.py