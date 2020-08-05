from MyClass import BackTesterMacd


class Universe:
    def __init__(
        self, versions,
    ):

        self.backtests = []
        for i in versions:
            self.backtests.append(MyClass())

    def __iter__(self):
        return

mmm

