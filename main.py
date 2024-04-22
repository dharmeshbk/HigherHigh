from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution
from collections import deque
from datetime import datetime, timedelta

class TrendBasedOnExtremaAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2021, 7, 13)
        self.SetEndDate(2023, 9, 15)
        self.SetCash(100000)

        self.SetWarmUp(timedelta(weeks=4))

        self.spy = self.AddEquity("SPY", Resolution.Daily)

        self.lookback = 10  # Lookback period for local extrema detection
        self.prices = deque(maxlen=self.lookback)

        self.previousMax = None
        self.previousMin = None
        self.currentTrend = None  # 'up' for uptrend, 'down' for downtrend

        # Schedule the function 30 minutes after market open
        self.Schedule.On(self.DateRules.EveryDay("SPY"), 
                         self.TimeRules.AfterMarketOpen("SPY", 30),
                         self.DetermineTrend)

    def OnData(self, data):
        if not data.ContainsKey("SPY"):
            return

        # Append price to the rolling window for later analysis
        self.prices.append(data["SPY"].Close)

    def DetermineTrend(self):
        if len(self.prices) < self.lookback:
            return

        currentMax = max(self.prices)
        currentMin = min(self.prices)

        # Update previous maxima and minima
        if self.prices[-1] == currentMax:
            self.previousMax = currentMax
        if self.prices[-1] == currentMin:
            self.previousMin = currentMin

        # Determine the trend based on previous extrema
        if self.previousMax and self.prices[-1] > self.previousMax:
            self.currentTrend = 'up'
            self.Debug(f"{self.Time} - Trend Update: New Up Trend. Current close is higher than previous max {self.previousMax}")
        elif self.previousMin and self.prices[-1] < self.previousMin:
            self.currentTrend = 'down'
            self.Debug(f"{self.Time} - Trend Update: New Down Trend. Current close is lower than previous min {self.previousMin}")

