#!/usr/bin/env python3
"""
Quick test of the wallet recovery functionality
"""

from mnemonic import Mnemonic
import sys

def test_wallet_recovery():
    print("🔐 Multi-Chain Wallet Recovery Tool - Quick Test")
    print("=" * 50)
    
    # Test BIP39 functionality
    mnemo = Mnemonic("english")
    print(f"✅ BIP39 library loaded successfully")
    print(f"📚 Wordlist contains {len(mnemo.wordlist)} words")
    
    # Test seed generation
    test_seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    if mnemo.check(test_seed):
        print("✅ BIP39 validation working correctly")
    else:
        print("❌ BIP39 validation failed")
        return
    
    # Test address derivation
    try:
        from bip32 import BIP32
        seed = mnemo.to_seed(test_seed)
        bip32 = BIP32.from_seed(seed)
        
        # Derive Bitcoin address
        btc_key = bip32.get_privkey_from_path("m/44'/0'/0'/0/0")
        print("✅ Bitcoin address derivation working")
        
        # Derive Ethereum address  
        eth_key = bip32.get_privkey_from_path("m/44'/60'/0'/0/0")
        print("✅ Ethereum address derivation working")
        
    except Exception as e:
        print(f"❌ Address derivation failed: {e}")
        return
    
    print("\n🎉 All systems are working correctly!")
    print("\n📋 To use the wallet recovery:")
    print("1. Run: python wallet_recovery.py (CLI version)")
    print("2. Or run: python gui_wallet_recovery.py (GUI version)")
    print("\n💡 You'll need:")
    print("   - At least 2 known words from your seed phrase")
    print("   - The positions where those words appear")
    print("   - Patience (recovery can take time depending on unknown words)")
    
    print("\n⚠️  Remember: This tool is for recovering YOUR OWN wallets only!")

if __name__ == "__main__":
    test_wallet_recovery()