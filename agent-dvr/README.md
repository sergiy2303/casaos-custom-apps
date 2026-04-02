# Agent DVR — CasaOS App

[iSpy Agent DVR](https://www.ispyconnect.com) video surveillance platform with AMD GPU
hardware-accelerated encoding/decoding, packaged as a CasaOS custom app.

## Features

- **AMD GPU hardware encoding** — VAAPI-accelerated encode/decode via Mesa drivers
- **Multi-camera support** — IP cameras, ONVIF, RTSP, USB devices
- **AI-powered detection** — built-in motion detection & object recognition
- **WebRTC & TURN** — low-latency live view in the browser
- **CasaOS integration** — import directly as a custom app

## Prerequisites

### Hardware

- AMD GPU or iGPU with VAAPI support (integrated Radeon graphics work fine)

### Host Setup

1. Install Mesa drivers:

```bash
sudo apt update
sudo apt install mesa-va-drivers vainfo
```

2. Verify VAAPI is working:

```bash
vainfo
```

You should see a list of supported profiles (e.g. `VAProfileH264Main`, `VAProfileHEVCMain`).

3. Check that GPU devices are accessible:

```bash
ls -la /dev/dri/renderD128 /dev/dri/card0 /dev/kfd
```

4. Grant your user access to the render and video groups:

```bash
sudo usermod -aG render,video $USER
```

5. Log out and back in (or reboot) for group changes to take effect.

## Install on CasaOS

1. Open CasaOS dashboard
2. Go to **Apps → Install a customized app → Import**
3. Paste the contents of `docker-compose.yml`
4. Click **Submit**

The app will appear on your CasaOS dashboard and start automatically.

> **⏳ First start:** Wait ~30 seconds before opening the WebUI. With many cameras
> configured, startup may take longer.

## First-Run Configuration

### 1. Open the WebUI

Navigate to `http://<your-host-ip>:8090` in your browser.

### 2. Configure Recording Storage

Recordings are stored in the container at `/AgentDVR/Media/WebServerRoot/Media`,
which maps to `/DATA/AppData/agent-dvr/recordings` on the host.

To use a different location (e.g. an external drive or NAS mount), edit the
`docker-compose.yml` volume before importing:

```yaml
- type: bind
  source: /mnt/surveillance/recordings   # ← your custom path
  target: /AgentDVR/Media/WebServerRoot/Media
```

Make sure the directory exists and is writable by UID/GID 1000:

```bash
sudo mkdir -p /mnt/surveillance/recordings
sudo chown 1000:1000 /mnt/surveillance/recordings
```

### 3. Enable Hardware Encoding in Agent DVR

Once the WebUI is running:

1. Go to **Server → Settings → Encoding**
2. Set **Encoder** to `VAAPI` (for AMD GPU)
3. Set **Decoder** to `VAAPI`
4. Save and restart the server when prompted

### 4. Add a Camera

1. Click the **+** button in the WebUI
2. Select **Video Source** → enter your camera's RTSP URL or choose ONVIF discovery
3. Configure motion detection, alerts, and recording schedule as needed

### 5. Verify GPU Acceleration

From the host, check that the GPU is being used:

```bash
# Check for active VAAPI sessions
sudo cat /sys/kernel/debug/dri/0/amdgpu_vcn_dec_usage 2>/dev/null || echo "Check AMD GPU usage via radeontop"

# Or install radeontop for real-time monitoring
sudo apt install radeontop
sudo radeontop
```

You should see VCN (Video Core Next) activity when cameras are streaming.

## Data Persistence

All persistent data is stored under `/DATA/AppData/agent-dvr/` on the host:

| Container Path | Host Path | Purpose |
|---|---|---|
| `/AgentDVR/Media/XML` | `/DATA/AppData/agent-dvr/config` | Configuration files (JSON/XML) |
| `/AgentDVR/Media/WebServerRoot/Media` | `/DATA/AppData/agent-dvr/recordings` | Surveillance recordings |
| `/AgentDVR/Media/Models` | `/DATA/AppData/agent-dvr/models` | AI model files for object detection |
| `/AgentDVR/Commands` | `/DATA/AppData/agent-dvr/commands` | Custom Agent DVR commands |

> **Backups:** To back up your configuration, copy the `config` directory.
> Recordings can be very large — consider pointing that volume to a dedicated drive.

## Ports

| Port | Protocol | Purpose |
|---|---|---|
| 8090 | TCP | WebUI |
| 3478 | UDP | TURN server |
| 50000–50100 | UDP | WebRTC connections |

## Timezone

The default timezone is `Europe/Kyiv`. To change it, edit the `TZ` environment
variable in `docker-compose.yml`:

```yaml
- TZ=America/New_York
```

See the [full list of timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Updating

Pull the latest image and recreate the container:

```bash
docker compose pull agent-dvr
docker compose up -d agent-dvr
docker image prune
```

Your configuration and recordings are preserved in the bind-mounted volumes.

## Troubleshooting

- **WebUI not loading after start** — wait 30 seconds and refresh; Agent DVR takes
  time to initialize, especially with many cameras.
- **No VAAPI profiles in `vainfo`** — install `mesa-va-drivers` and ensure your kernel
  supports your AMD GPU.
- **Permission denied on `/dev/kfd`** — add your user to the `render` group and
  reboot.
- **Recordings not saving** — check that the host directory exists, is writable by
  UID 1000, and has sufficient disk space.
- **Container logs** — check logs with `docker logs -f agent-dvr`.
- **Agent DVR internal logs** — visit `http://<host>:8090/logs.html` in the browser.

## Resources

- [Agent DVR User Guide](https://www.ispyconnect.com/userguide-agent-dvr.aspx)
- [Docker Image GitHub](https://github.com/MekayelAnik/ispyagentdvr-docker)
- [iSpy Community (Reddit)](https://www.reddit.com/r/ispyconnect/)
