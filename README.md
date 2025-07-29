# Multi-Chain Wallet Recovery Tool

A powerful Python application designed to recover cryptocurrency wallets when you have partial seed phrase information. This tool supports multiple blockchain networks and can check balances across various chains simultaneously.

## ⚠️ Important Legal Notice

**This tool is intended ONLY for recovering your own wallets.** Using this software to attempt to access wallets that do not belong to you is illegal and unethical. The developers of this tool are not responsible for any misuse.

## 🌟 Features

- **Multi-Chain Support**: Bitcoin, Ethereum, BSC, Polygon, Avalanche, Fantom, Arbitrum, Optimism
- **Partial Seed Recovery**: Recover wallets with just 2+ known words from your seed phrase
- **Real-time Balance Checking**: Automatically checks balances across all supported chains
- **Multi-threaded Processing**: Fast parallel processing for efficient recovery
- **User-Friendly GUI**: Easy-to-use graphical interface
- **Command Line Interface**: Advanced users can use the CLI version
- **No Rate Limits**: Configurable to work without API rate limitations
- **Secure**: All processing happens locally on your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection for blockchain API calls

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd wallet-recovery-tool
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API keys (optional but recommended):**
   - Edit `config.json` and add your API keys for better rate limits
   - You can get free API keys from:
     - [Etherscan](https://etherscan.io/apis) (Ethereum)
     - [BSCScan](https://bscscan.com/apis) (BSC)
     - [PolygonScan](https://polygonscan.com/apis) (Polygon)
     - [SnowTrace](https://snowtrace.io/apis) (Avalanche)
     - [FTMScan](https://ftmscan.com/apis) (Fantom)
     - [Arbiscan](https://arbiscan.io/apis) (Arbitrum)
     - [Optimism Etherscan](https://optimistic.etherscan.io/apis) (Optimism)

### Usage

#### GUI Version (Recommended)
```bash
python gui_wallet_recovery.py
```

#### Command Line Version
```bash
python wallet_recovery.py
```

## 📖 How It Works

### Seed Phrase Recovery Process

1. **Input Known Words**: Enter the words you remember from your seed phrase along with their positions
2. **Generate Combinations**: The tool generates all possible combinations using the BIP39 wordlist
3. **Validate Seeds**: Each combination is validated using BIP39 checksum
4. **Derive Addresses**: Valid seeds are used to derive addresses for all supported chains
5. **Check Balances**: Each address is checked for balances across multiple blockchains
6. **Report Results**: Wallets with non-zero balances are reported and saved

### Supported Derivation Paths

- **Bitcoin**: `m/44'/0'/0'/0/0` (BIP44)
- **Ethereum & EVM Chains**: `m/44'/60'/0'/0/0` (BIP44)

### Blockchain Networks Supported

| Network | Native Token | Explorer API |
|---------|-------------|--------------|
| Bitcoin | BTC | Blockstream |
| Ethereum | ETH | Etherscan |
| BSC | BNB | BSCScan |
| Polygon | MATIC | PolygonScan |
| Avalanche | AVAX | SnowTrace |
| Fantom | FTM | FTMScan |
| Arbitrum | ETH | Arbiscan |
| Optimism | ETH | Optimism Etherscan |

## 🖥️ GUI Features

### Main Tabs

1. **Wallet Recovery**
   - Input seed phrase length (12 or 24 words)
   - Add known words and their positions
   - Configure thread count for parallel processing
   - Real-time progress tracking
   - Live log output

2. **Settings**
   - Configure API keys for different blockchain explorers
   - Save settings for future use

3. **Results**
   - View detailed recovery results
   - Export results to file
   - Load previous results

### Example Usage

If you remember that your 12-word seed phrase contained:
- "abandon" at position 1
- "ability" at position 5

The tool will:
1. Generate ~1.6 billion combinations (2048^10)
2. Validate each combination using BIP39 checksum
3. For valid seeds, derive addresses for all supported chains
4. Check balances for each address
5. Report any wallets with funds

## ⚙️ Configuration

### config.json Structure

```json
{
  "api_keys": {
    "ethereum": "YOUR_ETHERSCAN_API_KEY",
    "bsc": "YOUR_BSCSCAN_API_KEY",
    // ... other API keys
  },
  "settings": {
    "max_workers": 4,
    "batch_size": 1000,
    "rate_limit_delay": 0.2,
    "timeout": 10,
    "save_all_attempts": false,
    "min_balance_usd": 0.01
  }
}
```

### Performance Tuning

- **max_workers**: Number of parallel threads (default: 4)
- **batch_size**: Number of seeds to process in each batch
- **rate_limit_delay**: Delay between API calls to avoid rate limiting
- **timeout**: API request timeout in seconds

## 🔒 Security Considerations

- **Local Processing**: All seed generation and validation happens locally
- **No Data Transmission**: Seed phrases are never transmitted over the internet
- **API Calls**: Only addresses (not private keys) are used for balance checking
- **Memory Management**: Sensitive data is cleared from memory when possible

## 📊 Performance

### Expected Processing Times

With 2 known words in a 12-word seed:
- **Combinations to check**: ~4.2 billion
- **Processing rate**: ~1,000-10,000 seeds/second (depending on hardware)
- **Estimated time**: Several hours to days

### Optimization Tips

1. **Use more known words**: Each additional known word reduces combinations exponentially
2. **Increase thread count**: More threads = faster processing (up to CPU limit)
3. **Use API keys**: Avoid rate limiting for faster balance checking
4. **Filter by minimum balance**: Skip wallets with dust amounts

## 🛠️ Technical Details

### Dependencies

- **mnemonic**: BIP39 seed phrase generation and validation
- **bip32**: HD wallet key derivation
- **ecdsa**: Elliptic curve cryptography
- **pycryptodome**: Cryptographic functions
- **requests**: HTTP API calls
- **base58**: Bitcoin address encoding

### Algorithm Complexity

For an n-word seed with k known words:
- **Time Complexity**: O(2048^(n-k))
- **Space Complexity**: O(1) - streaming generation

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid BIP39 word"**
   - Ensure words are from the official BIP39 wordlist
   - Check for typos or similar-looking words

2. **"No wallets found"**
   - Verify the known words and positions are correct
   - Try with different position combinations
   - Check if the wallet might use a different derivation path

3. **API Rate Limiting**
   - Add API keys to `config.json`
   - Increase `rate_limit_delay` in settings

4. **Out of Memory**
   - Reduce `batch_size` in configuration
   - Close other applications to free memory

### Performance Issues

- **Slow processing**: Increase thread count or use faster hardware
- **High CPU usage**: Reduce thread count
- **Network timeouts**: Increase timeout value or check internet connection

## 📄 File Outputs

- **recovered_wallets.json**: Detailed results of found wallets
- **recovery_log.txt**: Processing log (if enabled)
- **config.json**: User configuration and API keys

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Legal Disclaimer

This software is provided "as is" without warranty of any kind. The developers are not responsible for:
- Lost funds due to incorrect usage
- Legal consequences of misuse
- Recovery failures or false positives
- Any damages resulting from the use of this software

**Use at your own risk and only on wallets you own.**

## 🆘 Support

If you need help:

1. Check the troubleshooting section above
2. Review the configuration options
3. Open an issue on GitHub with detailed information about your problem

---

**Remember**: This tool is for recovering YOUR OWN wallets only. Never attempt to access wallets that don't belong to you.
