@echo off
REM Multi-Chain Wallet Recovery Tool Installation Script for Windows
REM This script sets up the wallet recovery environment on Windows

echo 🔐 Multi-Chain Wallet Recovery Tool Setup
echo =========================================

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.7 or higher.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

REM Check Python version (basic check)
python -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3.7 or higher is required. Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)
echo ✅ Python version is compatible

REM Check if pip is installed
echo Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)
echo ✅ pip is available

REM Create virtual environment (optional but recommended)
echo.
set /p create_venv="Do you want to create a virtual environment? (recommended) [y/N]: "
if /i "%create_venv%"=="y" (
    echo Creating virtual environment...
    python -m venv wallet_recovery_env
    call wallet_recovery_env\Scripts\activate.bat
    echo ✅ Virtual environment created and activated
    echo 💡 To activate it later, run: wallet_recovery_env\Scripts\activate.bat
)

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ requirements.txt not found. Installing dependencies manually...
    pip install mnemonic==0.20 bip32==3.4 ecdsa==0.18.0 pycryptodome==3.19.0 requests==2.31.0 base58==2.1.1
)

REM Check if config.json exists, if not create a template
if not exist config.json (
    echo Creating default configuration file...
    (
        echo {
        echo   "api_keys": {
        echo     "ethereum": "YOUR_ETHERSCAN_API_KEY",
        echo     "bsc": "YOUR_BSCSCAN_API_KEY",
        echo     "polygon": "YOUR_POLYGONSCAN_API_KEY",
        echo     "avalanche": "YOUR_SNOWTRACE_API_KEY",
        echo     "fantom": "YOUR_FTMSCAN_API_KEY",
        echo     "arbitrum": "YOUR_ARBISCAN_API_KEY",
        echo     "optimism": "YOUR_OPTIMISM_API_KEY"
        echo   },
        echo   "settings": {
        echo     "max_workers": 4,
        echo     "batch_size": 1000,
        echo     "rate_limit_delay": 0.2,
        echo     "timeout": 10,
        echo     "save_all_attempts": false,
        echo     "min_balance_usd": 0.01
        echo   },
        echo   "supported_chains": [
        echo     "bitcoin",
        echo     "ethereum",
        echo     "bsc",
        echo     "polygon",
        echo     "avalanche",
        echo     "fantom",
        echo     "arbitrum",
        echo     "optimism"
        echo   ],
        echo   "derivation_paths": {
        echo     "bitcoin": "m/44'/0'/0'/0/0",
        echo     "ethereum": "m/44'/60'/0'/0/0",
        echo     "bsc": "m/44'/60'/0'/0/0",
        echo     "polygon": "m/44'/60'/0'/0/0",
        echo     "avalanche": "m/44'/60'/0'/0/0",
        echo     "fantom": "m/44'/60'/0'/0/0",
        echo     "arbitrum": "m/44'/60'/0'/0/0",
        echo     "optimism": "m/44'/60'/0'/0/0"
        echo   }
        echo }
    ) > config.json
    echo ✅ Default config.json created
)

REM Test installation
echo.
echo Testing installation...
python -c "import mnemonic, bip32, ecdsa, requests, base58; print('✅ All modules imported successfully')" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Installation test passed
) else (
    echo ❌ Installation test failed
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 📖 Usage:
echo   GUI Version:     python gui_wallet_recovery.py
echo   CLI Version:     python wallet_recovery.py
echo.
echo ⚙️  Configuration:
echo   Edit config.json to add your API keys for better performance
echo.
echo 📚 Documentation:
echo   Read README.md for detailed usage instructions
echo.
echo ⚠️  Important:
echo   This tool is for recovering YOUR OWN wallets only!
echo   Using it for unauthorized access is illegal and unethical.
echo.

REM Check for GUI dependencies
echo Checking GUI support...
python -c "import tkinter" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GUI support available
    echo 💡 You can run the GUI version with: python gui_wallet_recovery.py
) else (
    echo ⚠️  GUI support not available ^(tkinter not installed^)
    echo 💡 You can still use the CLI version: python wallet_recovery.py
)

echo.
echo Happy wallet recovery! 🔓
pause