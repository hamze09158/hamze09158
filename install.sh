#!/bin/bash

# Multi-Chain Wallet Recovery Tool Installation Script
# This script sets up the wallet recovery environment

set -e  # Exit on any error

echo "🔐 Multi-Chain Wallet Recovery Tool Setup"
echo "========================================="

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if Python version is 3.7 or higher
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)'; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.7 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if pip is installed
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi
echo "✅ pip3 is available"

# Create virtual environment (optional but recommended)
echo ""
read -p "Do you want to create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv wallet_recovery_env
    source wallet_recovery_env/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate it later, run: source wallet_recovery_env/bin/activate"
fi

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found. Installing dependencies manually..."
    pip3 install mnemonic==0.20 bip32==3.4 ecdsa==0.18.0 pycryptodome==3.19.0 requests==2.31.0 base58==2.1.1
fi

# Make scripts executable
echo "Setting up executable permissions..."
chmod +x wallet_recovery.py
chmod +x gui_wallet_recovery.py

# Check if config.json exists, if not create a template
if [ ! -f "config.json" ]; then
    echo "Creating default configuration file..."
    cat > config.json << 'EOF'
{
  "api_keys": {
    "ethereum": "YOUR_ETHERSCAN_API_KEY",
    "bsc": "YOUR_BSCSCAN_API_KEY",
    "polygon": "YOUR_POLYGONSCAN_API_KEY",
    "avalanche": "YOUR_SNOWTRACE_API_KEY",
    "fantom": "YOUR_FTMSCAN_API_KEY",
    "arbitrum": "YOUR_ARBISCAN_API_KEY",
    "optimism": "YOUR_OPTIMISM_API_KEY"
  },
  "settings": {
    "max_workers": 4,
    "batch_size": 1000,
    "rate_limit_delay": 0.2,
    "timeout": 10,
    "save_all_attempts": false,
    "min_balance_usd": 0.01
  },
  "supported_chains": [
    "bitcoin",
    "ethereum",
    "bsc",
    "polygon",
    "avalanche",
    "fantom",
    "arbitrum",
    "optimism"
  ],
  "derivation_paths": {
    "bitcoin": "m/44'/0'/0'/0/0",
    "ethereum": "m/44'/60'/0'/0/0",
    "bsc": "m/44'/60'/0'/0/0",
    "polygon": "m/44'/60'/0'/0/0",
    "avalanche": "m/44'/60'/0'/0/0",
    "fantom": "m/44'/60'/0'/0/0",
    "arbitrum": "m/44'/60'/0'/0/0",
    "optimism": "m/44'/60'/0'/0/0"
  }
}
EOF
    echo "✅ Default config.json created"
fi

# Test installation
echo ""
echo "Testing installation..."
if python3 -c "import mnemonic, bip32, ecdsa, requests, base58; print('✅ All modules imported successfully')"; then
    echo "✅ Installation test passed"
else
    echo "❌ Installation test failed"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📖 Usage:"
echo "  GUI Version:     python3 gui_wallet_recovery.py"
echo "  CLI Version:     python3 wallet_recovery.py"
echo ""
echo "⚙️  Configuration:"
echo "  Edit config.json to add your API keys for better performance"
echo ""
echo "📚 Documentation:"
echo "  Read README.md for detailed usage instructions"
echo ""
echo "⚠️  Important:"
echo "  This tool is for recovering YOUR OWN wallets only!"
echo "  Using it for unauthorized access is illegal and unethical."
echo ""

# Check for GUI dependencies
echo "Checking GUI support..."
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✅ GUI support available"
    echo "💡 You can run the GUI version with: python3 gui_wallet_recovery.py"
else
    echo "⚠️  GUI support not available (tkinter not installed)"
    echo "💡 You can still use the CLI version: python3 wallet_recovery.py"
fi

echo ""
echo "Happy wallet recovery! 🔓"