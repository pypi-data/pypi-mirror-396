#!/usr/bin/env python3
"""
NRD Service Manager - Install/Uninstall NRD as a system service
Supports macOS (LaunchAgent), Linux (systemd), and Windows (Scheduled Task)
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path


def get_python_path():
    """Get the current Python interpreter path."""
    return sys.executable


def is_admin():
    """Check if running with admin/sudo privileges."""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False


def get_actual_user():
    """Get the actual user (not root/admin)."""
    if platform.system() == 'Windows':
        return os.environ.get('USERNAME')
    else:
        sudo_user = os.environ.get('SUDO_USER')
        if sudo_user:
            return sudo_user
        return os.environ.get('USER')


def install_macos():
    """Install NRD as a macOS LaunchAgent."""
    print("Installing NRD service for macOS...")
    
    user = get_actual_user()
    home = os.path.expanduser('~')
    if is_admin() and os.environ.get('SUDO_USER'):
        # Running under sudo, get the actual user's home
        import pwd
        home = pwd.getpwnam(os.environ['SUDO_USER']).pw_dir
    
    launch_agents_dir = os.path.join(home, 'Library', 'LaunchAgents')
    os.makedirs(launch_agents_dir, exist_ok=True)
    
    python_path = get_python_path()
    plist_file = os.path.join(launch_agents_dir, 'com.problemli.nrd.plist')
    
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.problemli.nrd</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-m</string>
        <string>nrd.nrd</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/tmp/nrd.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/nrd.error.log</string>
    
    <key>WorkingDirectory</key>
    <string>{home}</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:{home}/.local/bin</string>
    </dict>
</dict>
</plist>
'''
    
    with open(plist_file, 'w') as f:
        f.write(plist_content)
    
    print(f"Plist file created at: {plist_file}")
    
    # Unload if already loaded
    subprocess.run(['launchctl', 'unload', plist_file], 
                   stderr=subprocess.DEVNULL, check=False)
    
    # Load the service
    subprocess.run(['launchctl', 'load', plist_file], check=True)
    
    print("✓ NRD service installed and started successfully!")
    print("\nLogs available at:")
    print("  - /tmp/nrd.log")
    print("  - /tmp/nrd.error.log")
    print(f"\nTo uninstall: nrd-service-uninstall")


def install_linux():
    """Install NRD as a Linux systemd service."""
    if not is_admin():
        print("Error: Please run with sudo")
        sys.exit(1)
    
    print("Installing NRD service for Linux...")
    
    actual_user = get_actual_user()
    if not actual_user or actual_user == 'root':
        print("Error: Cannot determine actual user. Please run with sudo as a regular user.")
        sys.exit(1)
    
    print(f"Installing for user: {actual_user}")
    
    python_path = get_python_path()
    service_file = '/etc/systemd/system/nrd@.service'
    
    service_content = f'''[Unit]
Description=NRD - Vite Dev Server Background Service
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory=/home/%i
ExecStart={python_path} -m nrd.nrd
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/%i/.local/bin"

[Install]
WantedBy=multi-user.target
'''
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"Service file created at: {service_file}")
    
    # Reload systemd
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    
    # Enable and start the service
    service_name = f'nrd@{actual_user}.service'
    subprocess.run(['systemctl', 'enable', service_name], check=True)
    subprocess.run(['systemctl', 'start', service_name], check=True)
    
    print("✓ NRD service installed and started successfully!")
    print(f"\nTo check status: sudo systemctl status {service_name}")
    print(f"To view logs: sudo journalctl -u {service_name} -f")
    print(f"To uninstall: sudo nrd-service-uninstall")


def install_windows():
    """Install NRD as a Windows Scheduled Task."""
    if not is_admin():
        print("Error: This script must be run as Administrator")
        print("Right-click PowerShell/CMD and select 'Run as Administrator'")
        sys.exit(1)
    
    print("Installing NRD service for Windows...")
    
    current_user = get_actual_user()
    user_profile = os.environ.get('USERPROFILE')
    python_path = get_python_path()
    
    print(f"Installing for user: {current_user}")
    print(f"Using Python: {python_path}")
    
    task_name = "NRD-Service"
    
    # Use schtasks to create the task
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>NRD - Vite Dev Server Background Service</Description>
    <Author>Problemli GmbH</Author>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{current_user}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>-m nrd.nrd</Arguments>
      <WorkingDirectory>{user_profile}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''
    
    # Write XML to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-16') as f:
        temp_xml = f.name
        f.write(xml_content)
    
    try:
        # Delete existing task if present
        subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'], 
                      stderr=subprocess.DEVNULL, check=False)
        
        # Create the scheduled task
        subprocess.run(['schtasks', '/Create', '/XML', temp_xml, '/TN', task_name], check=True)
        
        # Start the task
        subprocess.run(['schtasks', '/Run', '/TN', task_name], check=True)
        
        print("\n✓ NRD service installed and started successfully!")
        print(f"\nTask Name: {task_name}")
        print(f"To uninstall: nrd-service-uninstall")
    finally:
        os.unlink(temp_xml)


def uninstall_macos():
    """Uninstall NRD LaunchAgent from macOS."""
    print("Uninstalling NRD service for macOS...")
    
    home = os.path.expanduser('~')
    if is_admin() and os.environ.get('SUDO_USER'):
        import pwd
        home = pwd.getpwnam(os.environ['SUDO_USER']).pw_dir
    
    plist_file = os.path.join(home, 'Library', 'LaunchAgents', 'com.problemli.nrd.plist')
    
    if not os.path.exists(plist_file):
        print(f"NRD service is not installed at: {plist_file}")
        sys.exit(1)
    
    # Unload the service
    print("Stopping service...")
    subprocess.run(['launchctl', 'unload', plist_file], 
                   stderr=subprocess.DEVNULL, check=False)
    
    # Remove the plist file
    print("Removing service file...")
    os.remove(plist_file)
    
    print("✓ NRD service uninstalled successfully!")


def uninstall_linux():
    """Uninstall NRD systemd service from Linux."""
    if not is_admin():
        print("Error: Please run with sudo")
        sys.exit(1)
    
    print("Uninstalling NRD service for Linux...")
    
    actual_user = get_actual_user()
    if not actual_user or actual_user == 'root':
        print("Error: Cannot determine actual user.")
        sys.exit(1)
    
    print(f"Uninstalling for user: {actual_user}")
    
    service_name = f'nrd@{actual_user}.service'
    service_file = '/etc/systemd/system/nrd@.service'
    
    if not os.path.exists(service_file):
        print(f"NRD service is not installed at: {service_file}")
        sys.exit(1)
    
    # Stop the service
    print("Stopping service...")
    subprocess.run(['systemctl', 'stop', service_name], 
                   stderr=subprocess.DEVNULL, check=False)
    
    # Disable the service
    print("Disabling service...")
    subprocess.run(['systemctl', 'disable', service_name], 
                   stderr=subprocess.DEVNULL, check=False)
    
    # Remove the service file
    print("Removing service file...")
    os.remove(service_file)
    
    # Reload systemd
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    
    print("✓ NRD service uninstalled successfully!")


def uninstall_windows():
    """Uninstall NRD Scheduled Task from Windows."""
    if not is_admin():
        print("Error: This script must be run as Administrator")
        sys.exit(1)
    
    print("Uninstalling NRD service for Windows...")
    
    task_name = "NRD-Service"
    
    # Check if task exists
    result = subprocess.run(['schtasks', '/Query', '/TN', task_name], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"NRD service is not installed (task '{task_name}' not found)")
        sys.exit(1)
    
    # Stop the task
    print("Stopping task...")
    subprocess.run(['schtasks', '/End', '/TN', task_name], 
                   stderr=subprocess.DEVNULL, check=False)
    
    # Delete the scheduled task
    print("Removing scheduled task...")
    subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'], check=True)
    
    print("✓ NRD service uninstalled successfully!")


def install():
    """Main install function - detects OS and installs appropriate service."""
    system = platform.system()
    
    if system == 'Darwin':
        install_macos()
    elif system == 'Linux':
        install_linux()
    elif system == 'Windows':
        install_windows()
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)


def uninstall():
    """Main uninstall function - detects OS and uninstalls service."""
    system = platform.system()
    
    if system == 'Darwin':
        uninstall_macos()
    elif system == 'Linux':
        uninstall_linux()
    elif system == 'Windows':
        uninstall_windows()
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'uninstall':
        uninstall()
    else:
        install()
