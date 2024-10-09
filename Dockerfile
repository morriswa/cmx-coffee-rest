
#
# AUTHOR: William A. Morris
# CREATION_DATE: 2024-08-28
# PURPOSE:
#   create Docker Container from generated application artifacts
#

# Container will be run on x86-64 Linux Platform
# Pull python 3.12
FROM --platform=x86-64 python:3.12-alpine

# ENV SYS_VAR=default_value

# create and move to directory /app to store artifacts
WORKDIR /app

ENV DJANGO_SETTINGS_MODULE app.prod

# copy into /app folder
COPY src/ ./src/
COPY default.properties .
COPY setup.py .
COPY pyproject.toml .

RUN pip install .

# set entrypoint (command which will run when container is started)
CMD ["gunicorn", "-b", "localhost:8001", "--chdir", "/app", "app.wsgi"]

# expose appropriate API port
EXPOSE 8001
