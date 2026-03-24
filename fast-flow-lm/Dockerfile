FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and XRT user-space library
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    && add-apt-repository ppa:amd-team/xrt \
    && apt-get update \
    && apt-get install -y libxrt-npu2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Fetch and install the latest FastFlowLM release (or pin with --build-arg FLM_VERSION=v0.9.36)
ARG FLM_VERSION=""
RUN if [ -z "$FLM_VERSION" ]; then \
      FLM_VERSION=$(curl -sL -o /dev/null -w '%{url_effective}' \
        https://github.com/FastFlowLM/FastFlowLM/releases/latest | grep -oP 'v[\d.]+$'); \
    fi \
    && FLM_VER_NUM=${FLM_VERSION#v} \
    && echo "Installing FastFlowLM ${FLM_VERSION}" \
    && wget -q "https://github.com/FastFlowLM/FastFlowLM/releases/download/${FLM_VERSION}/fastflowlm_${FLM_VER_NUM}_ubuntu24.04_amd64.deb" \
    && apt-get update \
    && apt-get install -y "./fastflowlm_${FLM_VER_NUM}_ubuntu24.04_amd64.deb" \
    && rm -f "fastflowlm_${FLM_VER_NUM}_ubuntu24.04_amd64.deb" \
    && rm -rf /var/lib/apt/lists/*

# Model cache directory
RUN mkdir -p /root/.config/flm

WORKDIR /app

# FastFlowLM API port
EXPOSE 52625

# Run FastFlowLM Server with gemma3:4b
CMD ["flm", "serve", "gemma3:4b", "--host", "0.0.0.0"]
