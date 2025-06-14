#!/bin/bash
# Setup and test script for Induct Downtime monitoring

echo "=== Induct Downtime Setup and Test ==="
echo

# Check current directory
echo "Current directory: $(pwd)"
echo

# Check for Midway cookie
COOKIE_PATH="$HOME/.midway/cookie"
if [ -f "$COOKIE_PATH" ]; then
    echo "✅ Midway cookie found at: $COOKIE_PATH"
else
    echo "❌ Midway cookie not found at: $COOKIE_PATH"
    echo "   Please run: mwinit -o"
    exit 1
fi

# Check Python
echo
echo "Python version:"
python3 --version

# Check for required packages
echo
echo "Checking for required Python packages..."

python3 -c "import requests" 2>/dev/null && echo "✅ requests available" || echo "❌ requests NOT available"
python3 -c "import bs4" 2>/dev/null && echo "✅ beautifulsoup4 available" || echo "❌ beautifulsoup4 NOT available"
python3 -c "import yaml" 2>/dev/null && echo "✅ PyYAML available" || echo "❌ PyYAML NOT available"
python3 -c "import schedule" 2>/dev/null && echo "✅ schedule available" || echo "❌ schedule NOT available"

# Installation instructions
echo
echo "=== Installation Instructions ==="
echo
echo "Since pip is not available, you have several options:"
echo
echo "Option 1: Install pip first (recommended)"
echo "  sudo apt update"
echo "  sudo apt install python3-pip"
echo "  pip3 install -r requirements.txt"
echo
echo "Option 2: Install packages via apt"
echo "  sudo apt update"
echo "  sudo apt install python3-requests python3-bs4 python3-yaml"
echo "  # Note: python3-schedule might not be available via apt"
echo
echo "Option 3: Use the install_pip.sh script"
echo "  sudo bash install_pip.sh"
echo
echo "Option 4: Install pip in user space (no sudo needed)"
echo "  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
echo "  python3 get-pip.py --user"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "  pip install --user -r requirements.txt"
echo
echo "After installing packages, test with:"
echo "  python3 src/auth.py"
echo "  python3 debug_mercury.py"