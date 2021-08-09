import iqtrade.api as iq


def print_accounts_pnl(qt: iq.QuestradeIQ) -> None:
    accounts = qt.get_accounts()
    account_positions = [qt.get_positions(account.number) for account in accounts]
    ticker_set = {position.symbol_id for positions in account_positions for position in positions}
    ticker_map = {symbol.ticker: symbol for symbol in qt.get_tickers(ticker_set)}

    total_pnl = {iq.Currency.CAD: 0.0, iq.Currency.USD: 0.0}
    for account, positions in zip(accounts, account_positions):
        print(account.number, account.type)
        day_pnl = {iq.Currency.CAD: 0.0, iq.Currency.USD: 0.0}
        for position in sorted(positions):
            ticker = ticker_map[position.ticker]
            currency = ticker.currency
            position_day_pnl = position.day_pnl
            day_pnl[currency] += position_day_pnl
            total_pnl[currency] += position_day_pnl
            print(
                "{0:<30}".format(ticker.get_display_name()),
                "",
                "${:11,.2f}".format(position_day_pnl),
                currency.name,
            )
        print(" " * 30, "", "=" * 16)
        for currency in day_pnl:
            print(" " * 30, "", "${0:11,.2f}".format(day_pnl[currency]), currency.name)
        print()

    for currency in total_pnl:
        print("Total".ljust(30), "", "${0:11,.2f}".format(total_pnl[currency]), currency.name)


def main() -> None:
    print_accounts_pnl(iq.QuestradeIQ())


if __name__ == "__main__":
    main()
