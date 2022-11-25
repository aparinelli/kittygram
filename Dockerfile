# Set base image (host OS)
FROM python:3.8-alpine
ENV PYTHONIOENCODING=utf-8

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy dependencies and install them
RUN apk update
RUN apk add musl-dev mariadb-dev gcc
RUN apk add build-base

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all source code
COPY . .

# Specify command to run on container start
CMD ["python", "./app.py"]