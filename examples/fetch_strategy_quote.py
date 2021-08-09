import iqtrade.api as iq

qt = iq.QuestradeIQ("secrets.json")

msft = qt.get_tickers("MSFT")
msft_call = qt.get_tickers("MSFT15Oct21C300.00")

variants = [
    iq.StrategyVariantRequest(
        1,
        iq.StrategyType.CoveredCall,
        legs=[
            iq.StrategyLeg(msft[0].symbol_id, iq.OrderAction.Buy, 200),
            iq.StrategyLeg(msft_call[0].symbol_id, iq.OrderAction.Sell, 2),
        ],
    )
]

quotes = qt.get_strategy_quotes(variants)

print(quotes[0])
