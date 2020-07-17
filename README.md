# README

# Algorithmic Trading Project

This project is an attempt to automate trading strategies for stock market from end-to-end using Alpaca.

## Things to Work on:

1. Backtesting

    Back testing strategies before shifting them to live paper trading for validation. This approach will significantly speed up parameter choices

    - [ ]  Currently writing implementation for moving average cross overs, stochastic oscillators, and RSI indicators
    - [ ]  
2. Live Trader
    - [x]  Timing for order cancellations
    - [ ]  Logging
    - [ ]  Visualization
3. Testing
    - [ ]  

## Cloning this repository

1. Open anaconda prompt. You can stay in the home directory (no `cd`-ing)
2. `git clone https://github.com/zlopez101/refactored-disco.git`
3. `cd refactored-disco`
4. 

### Updating Changes

1. Open anaconda prompt.
2. `cd refactored-disco`
3. `git pull`

### Running the Live Trader

1. Open anaconda prompt.
2. `cd refactored-disco`
3. `cd MoneyPrinter`
4. Make sure the conda environment is activate → should say `(trader)` at the beginning of line
    - If not active, run `conda activate trader`
5. Run the trader `python stream.py` 
    - Flags for customization `-h` → help for display

### Running the Backtester

Not ready for prime-time yet.