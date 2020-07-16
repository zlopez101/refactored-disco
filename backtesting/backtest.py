import backtrader as bt
import matplotlib.pyplot as plt
from btutils import get_data

from strategies import ZachSMA
import argparse


def run(pfast=(5, 20), pslow=(26, 41)):
    results = []
    data = get_data("TSLA")
    btready_data = bt.feeds.PandasData(dataname=data)
    print(len(data))

    for i in range(pfast[0], pfast[1] + 1):
        for j in range(pslow[0], pslow[1] + 1):
            cerebro = bt.Cerebro()
            cerebro.broker.set_cash(100000)
            cerebro.adddata(btready_data)
            cerebro.addstrategy(ZachSMA, pfast=i, pslow=j)
            cerebro.run()
            end = cerebro.broker.getvalue()
            results.append((i, j, end))
    values = [results[-1] for result in results]
    best = results[results.index(max(values))]
    print(
        f"The best combinations of period  for the moving average crossover the ranges ({pslow[0]}, {pslow[1]}) for the slow period and ({pfast[0]}, {pfast[1]}) for the fast period were {best[0]} fast and {best[1]} slow."
    )
    """
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(100000)
    cerebro.adddata(btready_data)
    cerebro.addstrategy(ZachSMA)
    cerebro.run()
    print(cerebro.broker.getvalue())
    """
    # results[end] = {"pslow": j, "pfast": i}
    # print(pfast[0])
    # print(pslow[0])
    # print(results)

    # cerebro.plot()


if __name__ == "__main__":

    # parser = argparse.ArgumentParser("Welcome to the Backtrading Integration.")
    print("running..")
    run()

