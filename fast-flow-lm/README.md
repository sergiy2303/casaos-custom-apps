# FastFlowLM — CasaOS App

Run LLMs directly on the AMD Ryzen AI NPU using [FastFlowLM](https://github.com/FastFlowLM/FastFlowLM).
This repository provides a CasaOS-ready Docker Compose setup for one-click deployment.

## Features

- **NPU-accelerated inference** — runs models on the AMD XDNA 2 NPU, not the CPU/GPU
- **OpenAI-compatible API** — drop-in replacement at `http://<host>:8002/v1`
- **CasaOS integration** — import directly as a custom app

## Prerequisites

### Hardware

- AMD Ryzen AI 300/400-series processor (XDNA 2 NPU required)

### Host Setup

1. Install kernel headers and build tools:

```bash
sudo apt update
sudo apt install build-essential dkms linux-headers-$(uname -r)
```

2. Install the NPU driver and XRT user-space libraries:

```bash
sudo add-apt-repository ppa:amd-team/xrt
sudo apt update
sudo apt install libxrt-npu2 amdxdna-dkms
```

3. Grant your user access to the NPU device:

```bash
sudo usermod -aG render $USER
```

4. Set memlock to unlimited in `/etc/security/limits.conf`:

```
*    soft    memlock    unlimited
*    hard    memlock    unlimited
```

5. Reboot and verify the NPU is available:

```bash
sudo reboot
# after reboot:
ls -la /dev/accel/accel0
```

## Install on CasaOS

### 1. Build the Docker image on the host

```bash
git clone https://github.com/sergiy2303/fast-flow-lm-casaos.git
cd fast-flow-lm-casaos
docker build -t fast-flow-lm .
```

### 2. Import into CasaOS

1. Open CasaOS dashboard
2. Go to **Apps → Install a customized app → Import**
3. Paste the contents of `docker-compose.yml`
4. Click **Submit**

The app will appear on your CasaOS dashboard and start automatically.

> **⏳ First run:** On the first start, FastFlowLM will automatically download the **gemma3:4b** model (~3 GB). This may take several minutes depending on your internet connection. The API will not respond until the download and NPU compilation are complete. You can monitor progress with:
> ```bash
> docker logs -f fast-flow-lm
> ```

### 3. Verify

```bash
curl http://localhost:8002/v1/models
```

### 4. Chat

```bash
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gemma3:4b", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## Optional Features

By default, the server runs **gemma3:4b** for chat completions only. You can enable additional capabilities by editing the `command` in `docker-compose.yml`.

### Enable Embeddings

Add `-e 1` to load an embedding model alongside the chat model:

```yaml
command: ["flm", "serve", "gemma3:4b", "--host", "0.0.0.0", "-e", "1"]
```

Then use the embeddings endpoint:

```bash
curl http://localhost:8002/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "snowflake-arctic-embed2:xs", "input": "Hello world"}'
```

### Enable ASR (Speech-to-Text)

Add `-a 1` to load a Whisper model for automatic speech recognition:

```yaml
command: ["flm", "serve", "gemma3:4b", "--host", "0.0.0.0", "-a", "1"]
```

### Enable Both

```yaml
command: ["flm", "serve", "gemma3:4b", "--host", "0.0.0.0", "-a", "1", "-e", "1"]
```

> **Note:** Each additional model uses NPU resources. Enable only what you need.

## Data Persistence

Model weights and compiled artifacts are stored on the host under CasaOS AppData:

| Container Path | Host Path | Purpose |
|---|---|---|
| `/root/.config/flm` | `/DATA/AppData/fast-flow-lm/flm` | Models & NPU-compiled artifacts |

## Components

- **FastFlowLM** (latest) — Runtime optimized for AMD XDNA 2 NPUs (auto-fetched at build time)
- **XRT (libxrt-npu2)** — User-space library for NPU communication

> **Pin a specific version** if needed:
> ```bash
> docker build --build-arg FLM_VERSION=v0.9.36 -t fast-flow-lm .
> ```
