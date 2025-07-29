#!/usr/bin/env python3
"""
GUI Multi-Chain Wallet Recovery Tool
User-friendly interface for wallet recovery with real-time progress tracking
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
from wallet_recovery import WalletRecovery

class WalletRecoveryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Chain Wallet Recovery Tool")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize recovery engine
        self.recovery = WalletRecovery()
        self.recovery_thread = None
        self.is_running = False
        
        # Load configuration
        self.load_config()
        
        # Create GUI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.config = json.load(f)
                    # Update recovery instance with API keys
                    self.recovery.api_keys.update(self.config.get('api_keys', {}))
            else:
                self.config = {}
        except Exception as e:
            messagebox.showerror("Config Error", f"Error loading config: {e}")
            self.config = {}
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Recovery tab
        recovery_frame = ttk.Frame(notebook)
        notebook.add(recovery_frame, text="Wallet Recovery")
        self.create_recovery_tab(recovery_frame)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.create_settings_tab(settings_frame)
        
        # Results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        self.create_results_tab(results_frame)
        
    def create_recovery_tab(self, parent):
        """Create the main recovery interface"""
        # Input section
        input_frame = ttk.LabelFrame(parent, text="Seed Phrase Information", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Seed length
        ttk.Label(input_frame, text="Seed phrase length:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.seed_length = ttk.Combobox(input_frame, values=[12, 24], state="readonly", width=10)
        self.seed_length.set(12)
        self.seed_length.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Known words section
        ttk.Label(input_frame, text="Known Words:", font=('TkDefaultFont', 10, 'bold')).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Known words list
        self.known_words_frame = ttk.Frame(input_frame)
        self.known_words_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        self.known_words = []
        self.word_entries = []
        
        # Add word button
        ttk.Button(input_frame, text="Add Known Word", command=self.add_word_entry).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Control section
        control_frame = ttk.LabelFrame(parent, text="Recovery Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Thread count
        ttk.Label(control_frame, text="Number of threads:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.thread_count = tk.StringVar(value="4")
        ttk.Entry(control_frame, textvariable=self.thread_count, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Recovery", command=self.start_recovery)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Recovery", command=self.stop_recovery, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to start recovery")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(pady=5)
        
        # Log output
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def create_settings_tab(self, parent):
        """Create the settings tab"""
        settings_frame = ttk.LabelFrame(parent, text="API Configuration", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # API keys
        self.api_entries = {}
        apis = ['ethereum', 'bsc', 'polygon', 'avalanche', 'fantom', 'arbitrum', 'optimism']
        
        for i, api in enumerate(apis):
            ttk.Label(settings_frame, text=f"{api.title()} API Key:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(settings_frame, width=50, show="*")
            entry.grid(row=i, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
            
            # Load existing key if available
            if api in self.recovery.api_keys:
                entry.insert(0, self.recovery.api_keys[api])
            
            self.api_entries[api] = entry
        
        # Configure column weight
        settings_frame.columnconfigure(1, weight=1)
        
        # Save button
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).grid(row=len(apis), column=0, columnspan=2, pady=10)
        
    def create_results_tab(self, parent):
        """Create the results tab"""
        results_frame = ttk.LabelFrame(parent, text="Recovery Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(results_frame, height=25, width=80)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Results", command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Results", command=self.load_results).pack(side=tk.LEFT, padx=5)
        
    def add_word_entry(self):
        """Add a new known word entry"""
        frame = ttk.Frame(self.known_words_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text="Word:").pack(side=tk.LEFT)
        word_entry = ttk.Entry(frame, width=15)
        word_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame, text="Position:").pack(side=tk.LEFT, padx=(10, 0))
        pos_entry = ttk.Entry(frame, width=5)
        pos_entry.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(frame, text="Remove", command=lambda: self.remove_word_entry(frame))
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.word_entries.append((word_entry, pos_entry, frame))
        
    def remove_word_entry(self, frame):
        """Remove a word entry"""
        for i, (word_entry, pos_entry, entry_frame) in enumerate(self.word_entries):
            if entry_frame == frame:
                frame.destroy()
                del self.word_entries[i]
                break
                
    def get_known_words(self):
        """Get the known words and positions from the GUI"""
        known_words = []
        known_positions = []
        
        for word_entry, pos_entry, _ in self.word_entries:
            word = word_entry.get().strip().lower()
            pos_str = pos_entry.get().strip()
            
            if word and pos_str:
                try:
                    position = int(pos_str) - 1  # Convert to 0-based
                    if word in self.recovery.bip39_words and 0 <= position < int(self.seed_length.get()):
                        known_words.append(word)
                        known_positions.append(position)
                    else:
                        raise ValueError(f"Invalid word '{word}' or position {pos_str}")
                except ValueError as e:
                    messagebox.showerror("Input Error", str(e))
                    return None, None
        
        return known_words, known_positions
        
    def log_message(self, message):
        """Add a message to the log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status):
        """Update the status label"""
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def start_recovery(self):
        """Start the wallet recovery process"""
        if self.is_running:
            return
            
        # Validate inputs
        known_words, known_positions = self.get_known_words()
        if known_words is None:
            return
            
        if len(known_words) < 2:
            messagebox.showerror("Input Error", "You need at least 2 known words for recovery")
            return
            
        try:
            max_workers = int(self.thread_count.get())
            if max_workers < 1 or max_workers > 16:
                raise ValueError("Thread count must be between 1 and 16")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid thread count: {e}")
            return
            
        # Clear previous results
        self.log_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        
        # Update UI state
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        
        # Start recovery in separate thread
        self.recovery_thread = threading.Thread(
            target=self.run_recovery,
            args=(known_words, known_positions, int(self.seed_length.get()), max_workers)
        )
        self.recovery_thread.daemon = True
        self.recovery_thread.start()
        
    def run_recovery(self, known_words, known_positions, total_words, max_workers):
        """Run the recovery process in a separate thread"""
        try:
            self.update_status("Starting recovery...")
            self.log_message("🔍 Starting wallet recovery...")
            self.log_message(f"Known words: {known_words}")
            self.log_message(f"Known positions: {[p+1 for p in known_positions]}")
            self.log_message(f"Total words in seed: {total_words}")
            
            # Override the recovery's print functions to use GUI logging
            original_print = print
            def gui_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                self.root.after(0, self.log_message, message)
            
            # Temporarily replace print
            import builtins
            builtins.print = gui_print
            
            try:
                found_wallets = self.recovery.recover_wallet(known_words, known_positions, total_words, max_workers)
                
                # Display results
                if found_wallets:
                    self.root.after(0, self.display_results, found_wallets)
                else:
                    self.root.after(0, self.log_message, "😔 No wallets with balance found")
                    
            finally:
                # Restore original print
                builtins.print = original_print
                
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Recovery Error", f"An error occurred during recovery: {e}")
        finally:
            self.root.after(0, self.recovery_finished)
            
    def display_results(self, found_wallets):
        """Display the recovery results"""
        self.results_text.delete(1.0, tk.END)
        
        for i, wallet in enumerate(found_wallets, 1):
            self.results_text.insert(tk.END, f"=== WALLET {i} ===\n")
            self.results_text.insert(tk.END, f"Seed Phrase: {wallet['seed_phrase']}\n")
            self.results_text.insert(tk.END, f"Total Value: ${wallet['total_usd']:.2f}\n\n")
            
            self.results_text.insert(tk.END, "Addresses:\n")
            for chain, address in wallet['addresses'].items():
                self.results_text.insert(tk.END, f"  {chain.title()}: {address}\n")
            
            self.results_text.insert(tk.END, "\nBalances:\n")
            for chain, balance_data in wallet['balances'].items():
                if chain == 'bitcoin':
                    balance = balance_data.get('balance', 0)
                    usd_value = balance_data.get('balance_usd', 0)
                    self.results_text.insert(tk.END, f"  {chain.title()}: {balance:.8f} BTC (${usd_value:.2f})\n")
                else:
                    native_balance = balance_data.get('native_balance', 0)
                    total_usd = balance_data.get('total_usd', 0)
                    self.results_text.insert(tk.END, f"  {chain.title()}: {native_balance:.6f} ETH (${total_usd:.2f})\n")
            
            self.results_text.insert(tk.END, "\n" + "="*50 + "\n\n")
        
        # Save results automatically
        try:
            with open('recovered_wallets.json', 'w') as f:
                json.dump(found_wallets, f, indent=2)
            self.log_message("💾 Results saved to 'recovered_wallets.json'")
        except Exception as e:
            self.log_message(f"Error saving results: {e}")
            
    def stop_recovery(self):
        """Stop the recovery process"""
        self.is_running = False
        self.update_status("Stopping recovery...")
        # Note: This is a simple stop - in a production version you'd want more sophisticated cancellation
        
    def recovery_finished(self):
        """Clean up after recovery is finished"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.update_status("Recovery completed")
        
    def save_settings(self):
        """Save API settings to config file"""
        try:
            # Update API keys
            for api, entry in self.api_entries.items():
                key = entry.get().strip()
                if key and key != "YOUR_" + api.upper() + "_API_KEY":
                    self.recovery.api_keys[api] = key
                    
            # Save to config file
            config = self.config.copy()
            config['api_keys'] = self.recovery.api_keys
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error saving settings: {e}")
            
    def clear_results(self):
        """Clear the results display"""
        self.results_text.delete(1.0, tk.END)
        
    def export_results(self):
        """Export results to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Export", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting results: {e}")
                
    def load_results(self):
        """Load results from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    if filename.endswith('.json'):
                        data = json.load(f)
                        self.display_results(data)
                    else:
                        content = f.read()
                        self.results_text.delete(1.0, tk.END)
                        self.results_text.insert(1.0, content)
                        
            except Exception as e:
                messagebox.showerror("Load Error", f"Error loading results: {e}")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = WalletRecoveryGUI(root)
    
    # Add some default known words for testing
    app.add_word_entry()
    app.add_word_entry()
    
    root.mainloop()

if __name__ == "__main__":
    main()