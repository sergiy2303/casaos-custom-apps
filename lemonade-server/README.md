# Lemonade Server — CasaOS App

Run local LLMs with [Lemonade Server](https://lemonade-server.ai/) — an OpenAI-compatible API server with Vulkan GPU and CPU inference.

## Features

- **OpenAI-compatible API** — drop-in replacement at `http://<host>:8003/api/v1`
- **Multiple backends** — Vulkan GPU, ROCm, or CPU via llama.cpp
- **Model management** — pull models from the Lemonade registry or bring your own GGUF files
- **ASR support** — speech-to-text via whisper.cpp
- **CasaOS integration** — import directly as a custom app

## Prerequisites

### Hardware

- Any x86_64 system with a Vulkan-capable GPU (recommended) or CPU-only

### Host Setup

1. Install Docker (comes pre-installed with CasaOS)
2. *(Optional)* For Vulkan GPU acceleration, ensure Vulkan drivers are installed on the host

## Install on CasaOS

### 1. Build the Docker image on the host

```bash
git clone https://github.com/sergiy2303/casaos-custom-apps.git
cd casaos-custom-apps/lemonade-server
docker build -t lemonade-server .
```

### 2. Import into CasaOS

1. Open CasaOS dashboard
2. Go to **Apps → Install a customized app → Import**
3. Paste the contents of `docker-compose.yml`
4. Click **Submit**

The app will appear on your CasaOS dashboard and start automatically.

### 3. Pull a model

Once the container is running, pull a model from the Lemonade registry:

```bash
docker exec lemonade-server lemonade-server pull Qwen3-0.6B-GGUF
```

You can also pull custom GGUF models from Hugging Face:

```bash
docker exec lemonade-server lemonade-server pull user.MyModel \
    --checkpoint unsloth/Phi-4-mini-instruct-GGUF:Q4_K_M \
    --recipe llamacpp
```

> **📋 Available models:** Browse the [Lemonade Model Registry](https://lemonade-server.ai/models.html) for a full list of supported models.

### 4. Load and chat

Load a model and start chatting:

```bash
# List available models
curl http://localhost:8003/api/v1/models

# Chat completion
curl http://localhost:8003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen3-0.6B-GGUF", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## Configuration

### Environment Variables

Configure the server by editing the `environment` section in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `LEMONADE_HOST` | Bind address | `0.0.0.0` |
| `LEMONADE_PORT` | Server port | `8003` |
| `LEMONADE_API_KEY` | API key for authentication (recommended for network access) | *(none)* |
| `LEMONADE_LLAMACPP` | llama.cpp backend: `vulkan`, `rocm`, or `cpu` | auto-detect |
| `LEMONADE_CTX_SIZE` | Context window size | model default |
| `LEMONADE_LOG_LEVEL` | Log level | `info` |
| `LEMONADE_MAX_LOADED_MODELS` | Max concurrent models (`-1` = unlimited) | `1` |

### API Key Security

To protect your server when exposed on a network, uncomment and set the `LEMONADE_API_KEY` variable in `docker-compose.yml`:

```yaml
environment:
  - LEMONADE_HOST=0.0.0.0
  - LEMONADE_API_KEY=your-random-secret-key
```

Then include the key as a Bearer token in all requests:

```bash
curl http://localhost:8003/v1/chat/completions \
  -H "Authorization: Bearer your-random-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen3-0.6B-GGUF", "messages": [{"role": "user", "content": "Hello!"}]}'
```

> ⚠️ **Important:** If exposing over the internet, do **not** expose Lemonade Server directly. Set up an HTTPS reverse proxy (e.g. nginx) in front of it — otherwise all traffic is in plaintext.

### Selecting a Backend

Set the llama.cpp backend based on your hardware:

```yaml
environment:
  - LEMONADE_LLAMACPP=vulkan    # Vulkan GPU (default, most compatible)
  # - LEMONADE_LLAMACPP=rocm    # AMD ROCm GPU
  # - LEMONADE_LLAMACPP=cpu     # CPU only
```

## Data Persistence

| Container Path | Host Path | Purpose |
|---|---|---|
| `/root/.cache/lemonade` | `/DATA/AppData/lemonade-server/cache` | Downloaded models & server state |

## CLI Reference

Manage models from the host via `docker exec`:

```bash
# Pull a model
docker exec lemonade-server lemonade-server pull <model-name>

# List installed models
docker exec lemonade-server lemonade-server list

# Delete a model
docker exec lemonade-server lemonade-server delete <model-name>

# Check server status
docker exec lemonade-server lemonade-server status
```

## Links

- [Lemonade Server Documentation](https://lemonade-server.ai/docs/server/lemonade-server-cli/)
- [Model Registry](https://lemonade-server.ai/models.html)
- [GitHub Repository](https://github.com/lemonade-sdk/lemonade)
