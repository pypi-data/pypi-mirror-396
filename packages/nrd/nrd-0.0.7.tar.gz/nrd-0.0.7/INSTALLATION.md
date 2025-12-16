# NRD Installation & Service Setup

## Quick Installation

Install NRD using pip:

```bash
pip install nrd
```

**During installation, you'll be prompted to automatically install NRD as a system service!**

Simply answer 'y' when asked, and the service will be configured automatically.

**Important Notes:**
- **Linux**: Run `sudo pip install nrd` to have permission to install the service
- **Windows**: Run pip in an Administrator PowerShell/CMD window
- **macOS**: Regular installation works, will prompt for password if needed

### What Gets Installed

The package installs:
- `nrd` - Main command to run NRD
- `nrd-service-install` - Command to install as a system service (if you skip the prompt)
- `nrd-service-uninstall` - Command to uninstall the system service

## Basic Usage

Run NRD manually:
```bash
nrd
```

## Service Installation (Autostart on Boot)

### macOS
```bash
nrd-service-install
```

### Linux
```bash
sudo nrd-service-install
```

### Windows
Open PowerShell as Administrator and run:
```powershell
nrd-service-install
```

## Service Uninstallation

### macOS
```bash
nrd-service-uninstall
```

### Linux
```bash
sudo nrd-service-uninstall
```

### Windows
Open PowerShell as Administrator and run:
```powershell
nrd-service-uninstall
```

## What the Service Does

When installed as a service, NRD:
- Automatically starts when your system boots
- Runs all Vite dev servers for your secured Laravel Herd sites
- Restarts automatically if it crashes
- Runs in the background without needing a terminal window

## Package Structure

The package includes three console entry points defined in `pyproject.toml`:

```toml
[project.scripts]
nrd = "nrd.nrd:main"
nrd-service-install = "nrd.service_manager:install"
nrd-service-uninstall = "nrd.service_manager:uninstall"
```

This means after `pip install nrd`, all three commands are available system-wide.

## Development Installation

For development, install in editable mode:

```bash
pip install -e .
```

This allows you to make changes to the code and test them immediately without reinstalling.

## Building the Package

To build a wheel for distribution:

```bash
python -m build --wheel
```

The wheel will be created in the `dist/` directory.

## For More Information

- [Detailed Service Documentation](service/README.md)
- [Main README](README.md)
- [GitHub Repository](https://github.com/blemli/nrd2)
