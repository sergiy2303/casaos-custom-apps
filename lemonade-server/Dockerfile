FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and XRT user-space library for NPU support
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    && add-apt-repository ppa:amd-team/xrt \
    && apt-get update \
    && apt-get install -y libxrt-npu2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Download and install Lemonade Server v10.0.0
RUN wget -q https://github.com/lemonade-sdk/lemonade/releases/download/v10.0.0/lemonade-server_10.0.0_amd64.deb \
    && apt-get update \
    && apt-get install -y ./lemonade-server_10.0.0_amd64.deb \
    && rm -f lemonade-server_10.0.0_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Model cache directory
RUN mkdir -p /root/.cache/lemonade

WORKDIR /app

# Lemonade Server default port
EXPOSE 8080

# Start Lemonade Server
CMD ["lemonade-server", "serve", "--host", "0.0.0.0", "--no-tray"]
