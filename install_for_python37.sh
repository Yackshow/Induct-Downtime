#!/bin/bash
# Install pip and packages for Python 3.7

echo "Installing pip for Python 3.7..."

# Download the correct pip installer for Python 3.7
curl https://bootstrap.pypa.io/pip/3.7/get-pip.py -o get-pip.py

# Install pip for the current user
python3 get-pip.py --user

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Check if pip is now available
if command -v pip &> /dev/null; then
    echo "✅ pip installed successfully!"
    pip --version
else
    echo "⚠️  pip command not found, trying pip3..."
    if command -v pip3 &> /dev/null; then
        echo "✅ pip3 installed successfully!"
        pip3 --version
        alias pip=pip3
    else
        echo "❌ pip installation may have succeeded but command not in PATH"
        echo "Try: $HOME/.local/bin/pip --version"
    fi
fi

# Install requirements
echo
echo "Installing requirements..."
$HOME/.local/bin/pip install --user -r requirements.txt || pip install --user -r requirements.txt || pip3 install --user -r requirements.txt

echo
echo "Installation complete!"
echo
echo "To make pip permanently available, add this to your ~/.bashrc or ~/.zshrc:"
echo 'export PATH="$HOME/.local/bin:$PATH"'
echo
echo "Then test with:"
echo "  python3 src/auth.py"