# nrd

Run `npm run dev` in background for all your Laravel Herd sites.

## Installation

```bash
pip install nrd
```

## Usage

Simply run the nrd command to start all Vite dev servers for your secured Herd sites:

```bash
python -m nrd.nrd
```

## Autostart on System Boot

NRD can be configured to automatically start when your system boots. This ensures your development servers are always running in the background.

### Quick Start

After installing NRD via pip, simply run:

**macOS:**
```bash
nrd-service-install
```

**Linux:**
```bash
sudo nrd-service-install
```

**Windows (Run PowerShell/CMD as Administrator):**
```powershell
nrd-service-install
```

### Uninstall Service

**macOS:**
```bash
nrd-service-uninstall
```

**Linux:**
```bash
sudo nrd-service-uninstall
```

**Windows (Run as Administrator):**
```powershell
nrd-service-uninstall
```

For detailed instructions, troubleshooting, and management commands, see the [Service Installation Guide](service/README.md).

## Features

- Automatically detects all secured Laravel Herd sites
- Runs Vite dev servers in the background
- Cross-platform service support (macOS, Linux, Windows)
- Auto-restart on failure
- Easy installation and management scripts

## Requirements

- Python 3.8 or higher
- Laravel Herd installed and configured
- npm and node.js
- Sites with Vite configured

## How It Works

NRD uses the `herd parked --json` command to discover all your secured Herd sites, then starts `npm run dev` for each site in the background. When configured as a service, it automatically starts on system boot and keeps your dev servers running.
