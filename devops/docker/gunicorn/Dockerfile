# Define a build argument for the Python version
ARG PYTHON_VERSION=3.11.0

# Use the argument in the FROM directive
# Default version (3.11.0) used if ARG isn't supplied during the build
FROM python:${PYTHON_VERSION}

WORKDIR /app

# Need to copy in requirements.txt and entrypoint.sh before they can be run
COPY ./requirements.txt /
COPY devops/docker/gunicorn/entrypoint.sh /

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy application code into image
COPY . .

# Add these debugging commands
RUN echo "Listing contents of /app:" && \
    ls -la /app && \
    echo "Current working directory:" && \
    pwd

ENTRYPOINT ["sh", "/entrypoint.sh"]
