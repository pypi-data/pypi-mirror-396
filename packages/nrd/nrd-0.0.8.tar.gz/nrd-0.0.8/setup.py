#!/usr/bin/env python3
"""
Custom setup.py to handle post-installation service setup.
This provides an option to automatically install the service after pip install.
"""

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import os


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    
    def run(self):
        install.run(self)
        self._post_install()
    
    def _post_install(self):
        """Ask user if they want to install the service."""
        print("\n" + "="*70)
        print("  NRD Installation Complete!")
        print("="*70)
        print("\nWould you like to install NRD as a system service?")
        print("This will make NRD start automatically when your system boots.\n")
        
        # Check if running in interactive mode
        if not sys.stdin.isatty():
            print("Non-interactive installation detected.")
            print("To install the service, run: nrd-service-install")
            print("="*70 + "\n")
            return
        
        try:
            response = input("Install service now? [y/N]: ").strip().lower()
            
            if response in ['y', 'yes']:
                print("\nInstalling NRD service...")
                
                # Import and run the service installer
                try:
                    from nrd.service_manager import install as install_service
                    install_service()
                except Exception as e:
                    print(f"\n⚠ Service installation failed: {e}")
                    print("\nYou can install it manually later by running:")
                    
                    if sys.platform == 'darwin':
                        print("  nrd-service-install")
                    elif sys.platform.startswith('linux'):
                        print("  sudo nrd-service-install")
                    elif sys.platform == 'win32':
                        print("  nrd-service-install  (in Administrator PowerShell)")
            else:
                print("\nSkipping service installation.")
                print("To install the service later, run:")
                
                if sys.platform == 'darwin':
                    print("  nrd-service-install")
                elif sys.platform.startswith('linux'):
                    print("  sudo nrd-service-install")
                elif sys.platform == 'win32':
                    print("  nrd-service-install  (in Administrator PowerShell)")
        
        except KeyboardInterrupt:
            print("\n\nSkipping service installation.")
        
        print("\n" + "="*70 + "\n")


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    
    def run(self):
        develop.run(self)
        print("\n" + "="*70)
        print("  NRD Development Installation Complete!")
        print("="*70)
        print("\nTo install as a service, run: nrd-service-install")
        print("="*70 + "\n")


if __name__ == '__main__':
    setup(
        cmdclass={
            'install': PostInstallCommand,
            'develop': PostDevelopCommand,
        },
    )
