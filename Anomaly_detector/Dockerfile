FROM python:3.12

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN . /opt/venv/bin/activate && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/opt/venv/bin/python"]
CMD ["app.py"]