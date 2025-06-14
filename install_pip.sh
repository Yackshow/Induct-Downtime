#!/bin/bash
# Script to install pip for Python 3

echo "=== Pip Installation Helper ==="
echo

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script needs sudo access to install pip system-wide"
    echo "   Please run: sudo bash install_pip.sh"
    echo
    echo "Alternative options:"
    echo "1. Install pip in user space:"
    echo "   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    echo "   python3 get-pip.py --user"
    echo
    echo "2. Use apt to install pip:"
    echo "   sudo apt update"
    echo "   sudo apt install python3-pip"
    echo
    echo "3. Install Python packages directly via apt:"
    echo "   sudo apt install python3-requests python3-bs4 python3-yaml"
    exit 1
fi

echo "Installing pip via apt..."
apt update
apt install -y python3-pip

if command -v pip3 &> /dev/null; then
    echo "✅ pip3 installed successfully!"
    pip3 --version
else
    echo "❌ pip3 installation failed"
    echo "Trying alternative method..."
    
    # Try to install python3-distutils first (required for pip)
    apt install -y python3-distutils
    
    # Download and install pip
    curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    python3 /tmp/get-pip.py
    
    if command -v pip3 &> /dev/null; then
        echo "✅ pip3 installed via alternative method!"
        pip3 --version
    else
        echo "❌ Could not install pip3"
        echo "Please install Python packages manually via apt:"
        echo "  sudo apt install python3-requests python3-bs4 python3-yaml"
    fi
fi