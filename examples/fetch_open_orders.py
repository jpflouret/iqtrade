import iqtrade.api as iq

qt = iq.QuestradeIQ("secrets.json")
accounts = qt.get_accounts()
orders = qt.get_orders(accounts[0], state_filter=iq.OrderStateFilter.All)

print(orders)
