# README

# Algorithmic Trading Project

This project is an attempt to automate trading strategies for stock market from end-to-end using Alpaca.

## Things to Work on:

1. Backtesting

    Back testing strategies before shifting them to live paper trading for validation. This approach will significantly speed up parameter choices

    ### OHLCV data with backtesting timeframes:
    - [x] daily minute data for 1 day 
    - [ ] daily data for 1 year
    

    ### Indicators working Currently implemented:
    - [x]  moving average cross overs
    - [ ]  stochastic oscillators
    - [ ]  RSI
    - 
2. Live Trader
    - [x]  Moving Average Crossover Divergence Indicator
    - [ ]  RSI, SO, SMA etc.
    - [ ]  Timing for order cancellations
        * I defined `cancel_old_orders` in the utils.py file. The idea is to get the current time as defined by 
        * My `cancel_old_orders` function call right now is placed in the `on_minute_bars` asynchronous function. That `on_minute_bars` function is called every minute for every stock we include in the trading universe. So every minute the `cancel_old_orders` function is called for every ticker. If more than 200 stocks are being watched, alpaca flags the account for exceeding 200 requests/min rate and throttles us. Which screws everything up. 
        * you might be wondering....why are we set up this way...shouldn't we just make the function run once per minute, not the # of stocks per minute? Well basically the program runs in a "event loop'. It stays in that loop till the program errors out (which is another issue). You have to define event in that loop before (that's what the `@conn.on()` is). The "easiest" implementation of the loop is follow the alpaca set-up, but it gives you the least flexibility since you can't customize events.
        * basically, this is a much more complicated issue AND it explains why the code that we copied from kept track of the orders and order_history.
        ### We might have to rebuild the whole websocket from scratch
        * This isn't the worst thing in the world, since if we want to use other brokers ideally we would only have implement minor changes to a propietary websocket connection. 
        * Timeline: not sure, hopefully <1 week. Can only test during market hours. Building our own would take...some time. not sure.
    - [ ]  Logging
        * the print statements are really annoying i think and kinda useless since they go by fast, especially when watching 200+ stocks. 
        * Python provides a `logging` module that writes statements to an output log file that we can inspect. 
        * Additionally, we can write another program that ingests this log file for analysis i.e. track orders, understand fill errors, and other debugging.
        * Timeline: <1 week for logging file, <2 weeks for analyzer program.
    - [ ]  Visualization
        * We can stream data collected during our `on_minute_bars` function to a visualization package like `bokeh`. This is a really awesome tool outputs graphs and charts to the browser. 
        * Timeline: 2-3 weeks away
    - [ ] Notifications
        * We can set email notifications really easily and text notifications with slightly more difficulty. Notifications might not be for every trade (since there could be a whole bunch of them), but might occur when events like portfolio values dips below threshold, or above thresholds. 
        * Timeline: 1 month away
3. Testing

    Best coding practices require that we write tests for all of our functions/classes etc to make sure that they behave as expected, especially once the project becomes very large. Normally, I would ignore this extrememly tedious job of writing tests, but since the goal is to put real money on the line, I think it becomes very important to make sure that everything works PERFECTLY. 
    - [ ]  Haven't start this yet, will take a look over the weekend 7/17-7/20.

## Cloning this repository
This step will only need to be done once. Go ahead and erase whatever folder you previously stored th
1. Open anaconda prompt. You can stay in the home directory (no `cd`-ing)
2. `git clone https://github.com/zlopez101/refactored-disco.git`
    * this creates the folder and all all files contained within the github repo.

### Updating Changes

1. Open anaconda prompt.
2. `cd refactored-disco`
3. `git pull`

### Running the Live Trader

1. Open anaconda prompt.
2. `cd refactored-disco/MoneyPrinter`
4. Make sure the conda environment is activate → should say `(trader)` at the beginning of line
    - If not active, run `conda activate trader`
5. Run the trader `python stream.py` 
    - Flags for customization `-h` → help for display

### Running the Backtester
0. You will need to download the backtrader package....
1. Open anaconda prompt.
2. `cd refactored-disco/backtesting`
