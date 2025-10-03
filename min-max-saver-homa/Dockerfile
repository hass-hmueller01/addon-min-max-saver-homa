# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_ARCH=amd64
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:latest
FROM $BUILD_FROM

RUN echo "alias l='ls --color=auto -alF'" >> /root/.bashrc

# Install dependencies
RUN \
    pip install --no-cache-dir --root-user-action ignore \
        paho-mqtt

# Copy root filesystem
COPY rootfs /

ENTRYPOINT ["/init"]
