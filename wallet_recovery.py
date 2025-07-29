#!/usr/bin/env python3
"""
Multi-Chain Wallet Recovery Tool
Recovers wallet seed phrases with known words and checks balances across multiple chains
"""

import itertools
import hashlib
import hmac
import struct
import requests
import time
import json
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from mnemonic import Mnemonic
from bip32 import BIP32
import ecdsa
from Crypto.Hash import keccak
import base58

class WalletRecovery:
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.bip39_words = self.mnemo.wordlist
        self.found_wallets = []
        self.lock = threading.Lock()
        
        # API endpoints for different chains
        self.api_endpoints = {
            'bitcoin': 'https://blockstream.info/api',
            'ethereum': 'https://api.etherscan.io/api',
            'bsc': 'https://api.bscscan.com/api',
            'polygon': 'https://api.polygonscan.com/api',
            'avalanche': 'https://api.snowtrace.io/api',
            'fantom': 'https://api.ftmscan.com/api',
            'arbitrum': 'https://api.arbiscan.io/api',
            'optimism': 'https://api-optimistic.etherscan.io/api'
        }
        
        # API keys (you'll need to add your own)
        self.api_keys = {
            'ethereum': 'YourEtherscanAPIKey',
            'bsc': 'YourBSCscanAPIKey',
            'polygon': 'YourPolygonscanAPIKey',
            'avalanche': 'YourSnowtraceAPIKey',
            'fantom': 'YourFTMscanAPIKey',
            'arbitrum': 'YourArbiscanAPIKey',
            'optimism': 'YourOptimismAPIKey'
        }

    def generate_seed_combinations(self, known_words: List[str], known_positions: List[int], 
                                 total_words: int = 12) -> List[List[str]]:
        """Generate all possible seed phrase combinations with known words at specific positions"""
        if len(known_words) != len(known_positions):
            raise ValueError("Number of known words must match number of known positions")
        
        unknown_positions = [i for i in range(total_words) if i not in known_positions]
        unknown_word_count = len(unknown_positions)
        
        print(f"Generating combinations for {unknown_word_count} unknown words...")
        print(f"This will generate approximately {len(self.bip39_words) ** unknown_word_count:,} combinations")
        
        # Generate combinations in batches to avoid memory issues
        batch_size = 10000
        combinations = []
        
        for unknown_words in itertools.product(self.bip39_words, repeat=unknown_word_count):
            seed_phrase = [''] * total_words
            
            # Place known words
            for word, pos in zip(known_words, known_positions):
                seed_phrase[pos] = word
            
            # Place unknown words
            for i, word in enumerate(unknown_words):
                seed_phrase[unknown_positions[i]] = word
            
            # Validate the seed phrase
            if self.mnemo.check(' '.join(seed_phrase)):
                combinations.append(seed_phrase)
                
            if len(combinations) >= batch_size:
                yield combinations
                combinations = []
        
        if combinations:
            yield combinations

    def derive_addresses(self, seed_phrase: str) -> Dict[str, str]:
        """Derive addresses for different blockchains from seed phrase"""
        addresses = {}
        
        try:
            # Generate seed from mnemonic
            seed = self.mnemo.to_seed(seed_phrase)
            bip32 = BIP32.from_seed(seed)
            
            # Bitcoin (BIP44: m/44'/0'/0'/0/0)
            btc_key = bip32.get_privkey_from_path("m/44'/0'/0'/0/0")
            btc_pubkey = bip32.get_pubkey_from_path("m/44'/0'/0'/0/0")
            addresses['bitcoin'] = self.pubkey_to_bitcoin_address(btc_pubkey)
            
            # Ethereum and EVM chains (BIP44: m/44'/60'/0'/0/0)
            eth_key = bip32.get_privkey_from_path("m/44'/60'/0'/0/0")
            eth_address = self.privkey_to_ethereum_address(eth_key)
            
            addresses['ethereum'] = eth_address
            addresses['bsc'] = eth_address
            addresses['polygon'] = eth_address
            addresses['avalanche'] = eth_address
            addresses['fantom'] = eth_address
            addresses['arbitrum'] = eth_address
            addresses['optimism'] = eth_address
            
        except Exception as e:
            print(f"Error deriving addresses: {e}")
            
        return addresses

    def pubkey_to_bitcoin_address(self, pubkey: bytes) -> str:
        """Convert public key to Bitcoin address"""
        # SHA256 hash
        sha256_hash = hashlib.sha256(pubkey).digest()
        
        # RIPEMD160 hash
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hashed_pubkey = ripemd160.digest()
        
        # Add version byte (0x00 for mainnet)
        versioned_payload = b'\x00' + hashed_pubkey
        
        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Final address
        address_bytes = versioned_payload + checksum
        return base58.b58encode(address_bytes).decode()

    def privkey_to_ethereum_address(self, privkey: bytes) -> str:
        """Convert private key to Ethereum address"""
        # Get public key from private key
        sk = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        pubkey = vk.to_string()
        
        # Keccak256 hash of public key
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(pubkey)
        address = keccak_hash.digest()[-20:]
        
        return '0x' + address.hex()

    def check_bitcoin_balance(self, address: str) -> Dict:
        """Check Bitcoin balance using Blockstream API"""
        try:
            response = requests.get(f"{self.api_endpoints['bitcoin']}/address/{address}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                balance_satoshi = data.get('chain_stats', {}).get('funded_txo_sum', 0) - \
                                data.get('chain_stats', {}).get('spent_txo_sum', 0)
                balance_btc = balance_satoshi / 100000000
                return {
                    'balance': balance_btc,
                    'balance_usd': balance_btc * self.get_btc_price(),
                    'transactions': data.get('chain_stats', {}).get('tx_count', 0)
                }
        except Exception as e:
            print(f"Error checking Bitcoin balance: {e}")
        return {'balance': 0, 'balance_usd': 0, 'transactions': 0}

    def check_evm_balance(self, address: str, chain: str) -> Dict:
        """Check balance for EVM-compatible chains"""
        try:
            api_key = self.api_keys.get(chain, '')
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest',
                'apikey': api_key
            }
            
            response = requests.get(self.api_endpoints[chain], params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    balance_wei = int(data.get('result', '0'))
                    balance_eth = balance_wei / 10**18
                    
                    # Get token balances
                    token_balances = self.get_token_balances(address, chain)
                    
                    return {
                        'native_balance': balance_eth,
                        'native_balance_usd': balance_eth * self.get_eth_price(),
                        'token_balances': token_balances,
                        'total_usd': balance_eth * self.get_eth_price() + sum(t.get('usd_value', 0) for t in token_balances)
                    }
        except Exception as e:
            print(f"Error checking {chain} balance: {e}")
        return {'native_balance': 0, 'native_balance_usd': 0, 'token_balances': [], 'total_usd': 0}

    def get_token_balances(self, address: str, chain: str) -> List[Dict]:
        """Get token balances for an address"""
        # This is a simplified version - you'd want to implement proper token detection
        # For now, checking common tokens like USDT, USDC, etc.
        token_balances = []
        
        common_tokens = {
            'ethereum': {
                '0xdAC17F958D2ee523a2206206994597C13D831ec7': 'USDT',  # Tether
                '0xA0b86a33E6417d8C8FD9B3e6e9c8E9e8e8e8e8e8': 'USDC'   # USD Coin
            },
            'bsc': {
                '0x55d398326f99059fF775485246999027B3197955': 'USDT',
                '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d': 'USDC'
            }
        }
        
        # Implementation would go here to check token balances
        # This is a placeholder
        return token_balances

    def get_btc_price(self) -> float:
        """Get current BTC price in USD"""
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
            if response.status_code == 200:
                return response.json()['bitcoin']['usd']
        except:
            pass
        return 50000  # Fallback price

    def get_eth_price(self) -> float:
        """Get current ETH price in USD"""
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=5)
            if response.status_code == 200:
                return response.json()['ethereum']['usd']
        except:
            pass
        return 3000  # Fallback price

    def check_all_balances(self, addresses: Dict[str, str]) -> Dict:
        """Check balances across all supported chains"""
        all_balances = {}
        
        # Check Bitcoin
        if 'bitcoin' in addresses:
            print(f"Checking Bitcoin balance for {addresses['bitcoin']}")
            all_balances['bitcoin'] = self.check_bitcoin_balance(addresses['bitcoin'])
        
        # Check EVM chains
        evm_chains = ['ethereum', 'bsc', 'polygon', 'avalanche', 'fantom', 'arbitrum', 'optimism']
        for chain in evm_chains:
            if chain in addresses:
                print(f"Checking {chain} balance for {addresses[chain]}")
                all_balances[chain] = self.check_evm_balance(addresses[chain], chain)
                time.sleep(0.2)  # Rate limiting
        
        return all_balances

    def process_seed_batch(self, seed_batch: List[List[str]]) -> List[Dict]:
        """Process a batch of seed phrases"""
        results = []
        
        for seed_phrase_list in seed_batch:
            seed_phrase = ' '.join(seed_phrase_list)
            
            # Derive addresses
            addresses = self.derive_addresses(seed_phrase)
            
            # Check balances
            balances = self.check_all_balances(addresses)
            
            # Calculate total value
            total_usd = 0
            for chain, balance_data in balances.items():
                if chain == 'bitcoin':
                    total_usd += balance_data.get('balance_usd', 0)
                else:
                    total_usd += balance_data.get('total_usd', 0)
            
            if total_usd > 0:  # Only save wallets with balance
                result = {
                    'seed_phrase': seed_phrase,
                    'addresses': addresses,
                    'balances': balances,
                    'total_usd': total_usd
                }
                results.append(result)
                
                with self.lock:
                    self.found_wallets.append(result)
                    print(f"\n🎉 WALLET FOUND! Total value: ${total_usd:.2f}")
                    print(f"Seed phrase: {seed_phrase}")
                    print(f"Addresses: {json.dumps(addresses, indent=2)}")
        
        return results

    def recover_wallet(self, known_words: List[str], known_positions: List[int], 
                      total_words: int = 12, max_workers: int = 4):
        """Main recovery function"""
        print("🔍 Starting wallet recovery...")
        print(f"Known words: {known_words}")
        print(f"Known positions: {known_positions}")
        print(f"Total words in seed: {total_words}")
        
        total_combinations = len(self.bip39_words) ** (total_words - len(known_words))
        print(f"Total combinations to check: {total_combinations:,}")
        
        processed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for batch in self.generate_seed_combinations(known_words, known_positions, total_words):
                future = executor.submit(self.process_seed_batch, batch)
                futures.append(future)
                
                if len(futures) >= max_workers * 2:  # Limit queue size
                    # Process completed futures
                    for completed_future in as_completed(futures[:max_workers]):
                        results = completed_future.result()
                        processed += len(results)
                        
                        if processed % 1000 == 0:
                            print(f"Processed {processed:,} combinations...")
                    
                    futures = futures[max_workers:]
            
            # Process remaining futures
            for future in as_completed(futures):
                results = future.result()
                processed += len(results)
        
        print(f"\n✅ Recovery complete! Processed {processed:,} combinations")
        print(f"Found {len(self.found_wallets)} wallets with balance")
        
        return self.found_wallets

def main():
    """Main function to run the wallet recovery"""
    recovery = WalletRecovery()
    
    print("🔐 Multi-Chain Wallet Recovery Tool")
    print("=" * 50)
    
    # Get user input
    total_words = int(input("Enter total number of words in seed phrase (12/24): ") or "12")
    
    known_words = []
    known_positions = []
    
    print(f"\nEnter your known words and their positions (1-{total_words}):")
    print("Type 'done' when finished")
    
    while True:
        word = input("Known word: ").strip().lower()
        if word == 'done':
            break
        
        if word not in recovery.bip39_words:
            print(f"⚠️  '{word}' is not a valid BIP39 word. Please try again.")
            continue
        
        position = int(input(f"Position of '{word}' (1-{total_words}): ")) - 1
        
        if position < 0 or position >= total_words:
            print(f"⚠️  Position must be between 1 and {total_words}")
            continue
        
        known_words.append(word)
        known_positions.append(position)
        
        print(f"✅ Added '{word}' at position {position + 1}")
    
    if len(known_words) < 2:
        print("⚠️  You need at least 2 known words for recovery")
        return
    
    # Start recovery
    max_workers = int(input("Number of threads (default 4): ") or "4")
    
    found_wallets = recovery.recover_wallet(known_words, known_positions, total_words, max_workers)
    
    # Save results
    if found_wallets:
        with open('recovered_wallets.json', 'w') as f:
            json.dump(found_wallets, f, indent=2)
        print(f"\n💾 Results saved to 'recovered_wallets.json'")
    else:
        print("\n😔 No wallets with balance found")

if __name__ == "__main__":
    main()