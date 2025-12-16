

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List
import os
import numpy as np
import io
import itertools
from itertools import permutations
from Bio import Entrez # type: ignore
from Bio import SeqIO # type: ignore
import random

BASE_ALPHABET = ['A', 'C', 'T', 'G']
# Generates all 24 permutations of [0, 1, 2, 3]
ALL_PERMUTATIONS = [list(p) for p in permutations([0, 1, 2, 3])] 

def convert_sequence_by_permutation(sequence: str, perm_number: int) -> list:
    """
    Converts an ACTG sequence to digits (0,1,2,3) using the specified permutation.
    This is a helper function for the main convert_genome_sequence.
    """
    # Ensure perm_number is 1-indexed (1 to 24)
    if not 1 <= perm_number <= len(ALL_PERMUTATIONS):
        raise ValueError("Permutation index must be between 1 and 24.")

    chosen_perm = ALL_PERMUTATIONS[perm_number - 1]

    conversion_map = {
        BASE_ALPHABET[i]: chosen_perm[i] for i in range(4)
    }

    converted_sequence = []
    for char in sequence:
        upper_char = char.upper()
        if upper_char in conversion_map:
            converted_sequence.append(conversion_map[upper_char])

    return converted_sequence
    
def convert_file_to_sequence(file_path: str, base: int) -> list:
    
    print(f"\n--- Running File-Based Irrational Conversion for Base {base} ---")
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found at path: {file_path}")
        return []

    try:
        with open(file_path, 'r') as f:
            raw_content = f.read()

        cleaned_digits = ''
        for char in raw_content:
            if char.isdigit():
                cleaned_digits += char
            else:
                # Skip the decimal point
                pass
            
        if not cleaned_digits:
            print("ERROR: File contains no usable digits.")
            return []

        converted_sequence = []
        for digit_char in cleaned_digits:
            digit_val = int(digit_char)
            converted_sequence.append(digit_val % base)
            
        print(f"Successfully read and converted {len(converted_sequence)} digits.")
        return converted_sequence

    except Exception as e:
        print(f"FATAL ERROR during file processing: {e}")
        return []
def convert_genome_sequence(base: int) -> list:
    """
    Prompts user for required NCBI access credentials, fetches the sequence,
    and converts it to a base 4 digit array using a user-selected permutation.
    Args:base (int): The base of the THART Automata. Must be 4.
    Returns:A list of base 4 integers for THART analysis.
    """
    if base != 4:
        print("ERROR: Genomic analysis requires Base 4.")
        return []
    
    print("\n--- NCBI Genomic Sequence Access ---")
    
    # 1.User Creds and API ID
    
    # Set Entrez Email 
    user_email = input("Enter your email address for NCBI Entrez access: ").strip()
    Entrez.email = user_email
    
    # Optional API Key \
    api_key = input("Enter your optional NCBI API key (Press Enter to skip): ").strip()
    if api_key:
        Entrez.api_key = api_key
    
    sequence_id = input("Enter the NCBI Accession ID (e.g., U00096.3): ").strip()
    
    while True:
        perm_choice_input = input("Enter the Permutation Index (1 to 24): ").strip()
        try:
            perm_choice = int(perm_choice_input)
            if 1 <= perm_choice <= 24:
                break
            else:
                print("Invalid input. Please enter a number between 1 and 24.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

   
    
    print("\n--- Starting Sequence Fetch ---")
    
    try:
        # 2. Fetch and Convert Sequence
        print(f"1. Fetching FASTA sequence for ID: {sequence_id}...")
        handle = Entrez.efetch(db="nucleotide", id=sequence_id, rettype="fasta", retmode="text")
        fasta_data = handle.read()
        handle.close()
        
        # 2b. Parse the sequence
        seq_record = SeqIO.read(io.StringIO(fasta_data), "fasta")
        sequence_string = str(seq_record.seq).strip()
        
        print(f"  -> Success. Sequence length: {len(sequence_string)} bases.")
        
        # 2c. Convert the sequence (DEFINES converted_array)
        converted_array = convert_sequence_by_permutation(sequence_string, perm_choice)
        
        perm_map = ALL_PERMUTATIONS[perm_choice - 1]
        print(f"2. Converted to {len(converted_array)} digits.")
        print(f"  -> Permutation Map: A={perm_map[0]}, C={perm_map[1]}, T={perm_map[2]}, G={perm_map[3]}")
        return converted_array

    except Exception as e:
        # Handle exceptions (e.g., wrong ID, invalid API key, network error)
        print(f"\nFATAL ERROR during Fetch/Conversion: {e}")
        return []


# --- 1. CORE LOGIC FUNCTION (REUSABLE FOR ANY OHLC DATA) ---
""" 
# --- Example Usage ---

# Use the wrapper function to fetch and sequence a stock (e.g., Tesla)
ticker_symbol = "TSLA"
stock_sequence = fetch_and_sequence_ticker(ticker_symbol, period="1y", interval="1d")

print(f"Sequence generated for Ticker: {ticker_symbol}")
if stock_sequence:
    print(f"Total number of candles processed: {len(stock_sequence)}")
    print(f"First 15 numeric states: {stock_sequence[:251]}")
else:
    print("Sequence generation failed.")
"""

def ohlc_to_sequence(df: pd.DataFrame) -> List[int]:
    """
    Converts a DataFrame of OHLC data into the 0-15 numeric sequence 
    based on relative body size (quartiles) and wick size (local medians).
    
    Args:
        df: A pandas DataFrame containing 'Open', 'High', 'Low', 'Close' columns.

    Returns:
        list[int]: A list of integers (0-15) representing the candle sequence.
    """
    
    # Use a copy to avoid SettingWithCopyWarning if the input DF is a slice
    df = df.copy() 

    # 2. Extract specific lengths
    df['body_height'] = (df['Close'] - df['Open']).abs()
    df['upper_wick'] = df['High'] - np.maximum(df['Open'], df['Close'])
    df['lower_wick'] = np.minimum(df['Open'], df['Close']) - df['Low']

    # 3. Assign Height Group (A, B, C, D) using Quartiles
    df['group'] = pd.qcut(df['body_height'], 4, labels=['A', 'B', 'C', 'D'], duplicates='drop')

    # 4. Process Wick Numbers per group logic
    def calculate_wick_number(group_df):
        med_upper = group_df['upper_wick'].median()
        med_lower = group_df['lower_wick'].median()
        
        # Calculate bits: 1 if wick is larger than its group's median
        lower_bit = (group_df['lower_wick'] > med_lower).astype(int) # MSB
        upper_bit = (group_df['upper_wick'] > med_upper).astype(int) # LSB
        
        # Wick Number: (Lower Bit * 2) + (Upper Bit * 1) -> 0, 1, 2, or 3
        group_df['wick_num'] = (lower_bit * 2) + upper_bit
        return group_df

    # Apply the logic group by group (using observed=False to suppress FutureWarning)
    df = df.groupby('group', observed=False, group_keys=False).apply(calculate_wick_number)

    # 5. Final Numeric Encoding (0-15 Mapping)
    # A=0, B=4, C=8, D=12
    group_map = {'A': 0, 'B': 4, 'C': 8, 'D': 12}
    
    # Map group to base value and explicitly convert to int for addition (Fixes TypeError)
    df['group_value'] = df['group'].map(group_map).astype(int) 
    
    # Final state = Group Base Value + Wick Number
    df['numeric_state'] = df['group_value'] + df['wick_num']
    
    # Return the sequence in chronological order
    return df['numeric_state'].astype(int).tolist()


# --- 2. DATA FETCHING WRAPPER FUNCTION (STOCK-SPECIFIC) ---

def fetch_and_sequence_ticker(ticker: str, period: str = "1y", interval: str = "1d") -> List[int]:
    """
    Fetches OHLC data for a stock ticker from Yahoo Finance and converts 
    it to the 0-15 numeric sequence using the core logic function.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        period (str): Data period (e.g., '6mo', '1y').
        interval (str): Data interval (e.g., '1d', '1wk').
        
    Returns:
        list[int]: The final numeric sequence, or an empty list if data 
                   fetching fails or is incomplete.
    """
    
    # 1. Fetch historical data
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    
    if df.empty:
        print(f"Warning: No data found for ticker '{ticker}'.")
        return []

    required_cols = ['Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_cols):
        print("Error: Fetched data is missing required OHLC columns.")
        return []
        
    # 2. Call the reusable core logic function
    sequence = ohlc_to_sequence(df)
    
    return sequence

