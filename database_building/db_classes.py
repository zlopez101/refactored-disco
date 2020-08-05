import requests
from bs4 import BeautifulSoup


class Stock:
    endpoint_1, endpoint_2 = (
        "http://sec.gov/cgi-bin/browse-edgar?CIK=",
        "&Find=Search&owner=exclude&action=getcompany",
    )

    def __init__(self, ticker):  # industry_number, industries):
        self.ticker = ticker
        self._get_industry()

        # self.industry = industry
        # self.industry_sic = industry_sic

    def _get_industry(self):
        r = requests.get(Stock.endpoint_1 + self.ticker + Stock.endpoint_2)
        soup = BeautifulSoup(r.text, features="html.parser")
        text = soup.select("p")[0].get_text().split(" ")
        self.industry_sic = text[1]

        url_1, url_2 = (
            "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=",
            "&owner=include&count=40",
        )

        r = requests.get(url_1 + self.industry_sic + url_2)
        soup = BeautifulSoup(r.text, features="html.parser")
        self.industry = " ".join(soup.select("div span")[0].get_text().split(" ")[6:])

    def __repr__(self):
        return f"{self.ticker} in {self.industry}"

