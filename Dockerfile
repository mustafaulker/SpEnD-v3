FROM python

COPY . /SpEnD
WORKDIR /SpEnD

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT python run.py
