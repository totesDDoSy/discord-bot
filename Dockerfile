FROM python:3

ADD app /

ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "app/main.py" ]