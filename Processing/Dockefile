FROM python:3.12

WORKDIR /app

# create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy requirements first for better caching
COPY requirements.txt .

# install dependencies in virtual environment
RUN . /opt/venv/bin/activate && pip install -r requirements.txt

# copy the rest of the application
COPY . .

# use the virtual environment's Python
ENTRYPOINT ["/opt/venv/bin/python"]
CMD ["app.py"]