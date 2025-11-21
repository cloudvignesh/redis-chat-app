# Use Python37
FROM python:3.8

# Accept build args for proxy configuration
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# Set environment variables for proxy (used by pip and other tools)
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}

# Copy requirements.txt to the docker image and install packages
COPY requirements.txt /
RUN pip install --proxy=${HTTP_PROXY} -r requirements.txt || pip install -r requirements.txt

# Set the WORKDIR to be the folder
COPY . /app
# Expose port 8080
EXPOSE 8080
ENV PORT 8080
WORKDIR /app
# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT --worker-class eventlet -w 1 app:app
