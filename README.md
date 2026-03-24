# CasaOS Custom Apps

A curated collection of third-party applications packaged for [CasaOS](https://casaos.io) that are **not available** in the official CasaOS App Store.

Each subdirectory contains a self-contained app with its own `docker-compose.yml`, `Dockerfile` (when needed), and documentation — ready to import into CasaOS with a single click.

## Available Apps

| App | Description | Status |
|-----|-------------|--------|
| [FastFlowLM](fast-flow-lm/) | NPU-accelerated LLM inference on AMD Ryzen AI processors via [FastFlowLM](https://github.com/FastFlowLM/FastFlowLM) | ✅ Ready |
| [Lemonade Server](lemonade-server/) | Local LLM inference with OpenAI-compatible API via [Lemonade Server](https://lemonade-server.ai/) | ⚠️ Not ready |

## How to Install

1. Pick an app from the table above and open its folder.
2. Follow the app-specific README for any **prerequisites** (drivers, hardware, image builds, etc.).
3. Open your CasaOS dashboard → **Apps → Install a customized app → Import**.
4. Paste the contents of the app's `docker-compose.yml` and click **Submit**.

The app will appear on your CasaOS dashboard and start automatically.

## Repository Structure

```
casaos-custom-apps/
├── README.md                   # ← you are here
└── <app-name>/
    ├── docker-compose.yml      # CasaOS-compatible compose file
    ├── Dockerfile              # (optional) if the app needs a custom image
    ├── icon.png                # App icon shown in CasaOS dashboard
    └── README.md               # App-specific docs & prerequisites
```

## Contributing

Want to add a new app? Create a new directory following the structure above and submit a pull request.

1. Create a folder named after the app (lowercase, hyphens for spaces).
2. Add a `docker-compose.yml` with the [`x-casaos`](https://wiki.casaos.io/en/guides/use-cases/custom-app-panel) metadata block.
3. Include an `icon.png` (256 × 256 px recommended).
4. Write a `README.md` covering prerequisites, installation, and usage.
5. Update the **Available Apps** table in this root README.

## License

Each app may carry its own license from its upstream project. See individual app directories for details.
