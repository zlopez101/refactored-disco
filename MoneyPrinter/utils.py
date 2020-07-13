import os


def credentialing(paper=True):
    if paper:
        url = "https://paper-api.alpaca.markets"
        key = os.environ.get("ALPACA_API_KEY")
        secret = os.environ.get("ALPACA_API_SECRET")
    else:
        url = "https://api.alpaca.markets"
        key = os.environ.get("rALPACA_API_KEY")
        secret = os.environ.get("rALPACA_API_SECRET")
    return url, key, secret
