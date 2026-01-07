# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_ARCH=amd64
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:latest
FROM $BUILD_FROM

RUN echo "alias l='ls --color=auto -alF'" >> /root/.bashrc

# Install dependencies
RUN apk update && \
    apk add --no-cache git

# Copy root filesystem
COPY rootfs /

# Build the Python virtual environment for the service
RUN \
    cd /etc/services.d/min-max-saver && \
    python3 -m venv .venv --system-site-packages && \
    source .venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Cleanup
RUN apk del git && \
    apk cache clean && \
    rm -rf /var/cache/apk/* /tmp/* /root/.cache/pip

ENTRYPOINT ["/init"]
