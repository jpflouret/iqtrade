from __future__ import annotations

import json
import re
import urllib.parse
from datetime import datetime as dt
from enum import Enum
from typing import Any, Optional, Union

import requests


class Currency(Enum):
    USD = 0
    CAD = 1


class ListingExchange(Enum):
    TSX = 0
    TSXV = 1
    CNSX = 2
    MX = 3
    NASDAQ = 4
    NYSE = 5
    NYSEAM = 6
    ARCA = 7
    OPRA = 8
    PinkSheets = 9
    OTCBB = 10


class AccountType(Enum):
    Cash = 0
    Margin = 1
    TFSA = 2
    RRSP = 3
    SRRSP = 4
    LRRSP = 5
    LIRA = 6
    LIF = 7
    RIF = 8
    SRIF = 9
    LRIF = 10
    RRIF = 11
    PRIF = 12
    RESP = 13
    FRESP = 14


class ClientAccountType(Enum):
    Individual = 0
    Joint = 1
    InformalTrust = 2
    Corporation = 3
    InvestmentClub = 4
    FormalTrust = 5
    Partnership = 6
    SoleProprietorship = 7
    Family = 8
    JointAndInformalTrust = 9
    Institution = 10

    @staticmethod
    def from_string(account_type: str) -> ClientAccountType:
        account_type = account_type.replace(" ", "").lower()
        if account_type == "individual":
            return ClientAccountType.Individual
        elif account_type == "joint":
            return ClientAccountType.Joint
        elif account_type == "informaltrust":
            return ClientAccountType.InformalTrust
        elif account_type == "corporation":
            return ClientAccountType.Corporation
        elif account_type == "investmentclub":
            return ClientAccountType.InvestmentClub
        elif account_type == "formaltrust":
            return ClientAccountType.FormalTrust
        elif account_type == "partnership":
            return ClientAccountType.Partnership
        elif account_type == "soleproprietorship":
            return ClientAccountType.SoleProprietorship
        elif account_type == "family":
            return ClientAccountType.Family
        elif account_type == "jointandinformaltrust":
            return ClientAccountType.JointAndInformalTrust
        elif account_type == "institution":
            return ClientAccountType.Institution
        else:
            raise ValueError('Unknown account_type "' + account_type + '"')  # pragma: no cover


class TickType(Enum):
    Up = 0
    Down = 1
    Equal = 2


class OptionType(Enum):
    Invalid = 0
    Call = 1
    Put = 2


class OptionDurationType(Enum):
    Invalid = 0
    Weekly = 1
    Monthly = 2
    Quarterly = 3
    LEAP = 4


class OptionExerciseType(Enum):
    Invalid = 0
    American = 1
    European = 2


class SecurityType(Enum):
    Stock = 0
    Option = 1
    Bond = 2
    Right = 3
    Gold = 4
    MutualFund = 5
    Index = 6


class OrderStateFilter(Enum):
    All = 0
    Open = 1
    Closed = 2


class OrderAction(Enum):
    Buy = 0
    Sell = 1


class OrderSide(Enum):
    Buy = 0
    Sell = 1
    Short = 2
    Cov = 3
    BTO = 4
    STC = 5
    STO = 6
    BTC = 7


class OrderType(Enum):
    Market = 0
    Limit = 1
    Stop = 2
    StopLimit = 3
    TrailStopInPercentage = 4
    TrailStopInDollar = 5
    TrailStopLimitInPercentage = 6
    TrailStopLimitInDollar = 7
    LimitOnOpen = 8
    LimitOnClose = 9


class OrderTimeInForce(Enum):
    Day = 0
    GoodTillCanceled = 1
    GoodTillExtendedDay = 2
    GoodTillDate = 3
    ImmediateOrCancel = 4
    FillOrKill = 5


class OrderState(Enum):
    Failed = 0
    Pending = 1
    Accepted = 2
    Rejected = 3
    CancelPending = 4
    Canceled = 5
    PartialCanceled = 6
    Partial = 7
    Executed = 8
    ReplacePending = 9
    Replaced = 10
    Stopped = 11
    Suspended = 12
    Expired = 13
    Queued = 14
    Triggered = 15
    Activated = 16
    PendingRiskReview = 17
    ContingentOrder = 18


class Granularity(Enum):
    OneMinute = 1
    TwoMinutes = 2
    ThreeMinutes = 3
    FourMinutes = 4
    FiveMinutes = 5
    TenMinutes = 6
    FifteenMinutes = 7
    TwentyMinutes = 8
    HalfHour = 9
    OneHour = 10
    TwoHours = 11
    FourHours = 12
    OneDay = 13
    OneWeek = 14
    OneMonth = 15
    OneYear = 16


class OrderClass(Enum):
    Invalid = 0
    Primary = 1
    Limit = 2
    StopLoss = 3


class StrategyType(Enum):
    SingleLeg = 0
    CoveredCall = 1
    MarriedPuts = 2
    VerticalCallSpread = 3
    VerticalPutSpread = 4
    CalendarCallSpread = 5
    CalendarPutSpread = 6
    DiagonalCallSpread = 7
    DiagonalPutSpread = 8
    Collar = 9
    Straddle = 10
    Strangle = 11
    ButterflyCall = 12
    ButterflyPut = 13
    IronButterfly = 14
    CondorCall = 15
    Custom = 16


class SocketMode(Enum):
    RawSocket = 0
    WebSocket = 1


class AccountInfo:
    def __init__(self, iq_data: dict[str, Any]):
        self.number: str = iq_data["number"]
        self.type: AccountType = AccountType[iq_data["type"]]
        self.status: str = iq_data["status"]
        self.is_rimary: bool = iq_data["isPrimary"]
        self.is_billing: bool = iq_data["isBilling"]
        self.client_account_type: ClientAccountType = ClientAccountType.from_string(iq_data["clientAccountType"])

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.number} {self.type.name}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __lt__(self, other: AccountInfo) -> bool:
        return self.number < other.number

    def get_account_number(account_id: Union[str, AccountInfo]) -> str:
        if isinstance(account_id, str):
            return account_id
        elif isinstance(account_id, AccountInfo):
            return account_id.number
        else:
            raise TypeError("Invalid type for 'account_id'")  # pragma: no cover


class AccountActivity:
    def __init__(self, iq_data: dict[str, Any]):
        self.trade_date: dt = dt.fromisoformat(iq_data["tradeDate"])
        self.transaction_date: dt = dt.fromisoformat(iq_data["transactionDate"])
        self.settlement_date: dt = dt.fromisoformat(iq_data["settlementDate"])
        self.action: str = iq_data["action"]
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.description: str = iq_data["description"]
        self.currency: Currency = Currency[iq_data["currency"]]
        self.quantity: float = iq_data["quantity"]
        self.price: float = iq_data["price"]
        self.gross_amount: float = iq_data["grossAmount"]
        self.commission: float = iq_data["commission"]
        self.net_amount: float = iq_data["netAmount"]
        self.activity_type: str = iq_data["type"]

    def __str__(self) -> str:  # pragma: no cover
        return str(
            self.activity_type
            + " "
            + self.action
            + " "
            + f"{self.quantity:.2f}"
            + " "
            + self.ticker
            + " "
            + f"{self.price:.2f}"
            + " "
            + f"{self.net_amount:.2f}"
            + " "
            + self.currency.name
        )

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __lt__(self, other: AccountActivity) -> bool:
        return self.transaction_date < other.transaction_date


class Balance:
    def __init__(self, iq_data: dict[str, Any]):
        self.currency: Currency = Currency[iq_data["currency"]]
        self.cash: float = iq_data["cash"]
        self.market_value: float = iq_data["marketValue"]
        self.total_equity: float = iq_data["totalEquity"]
        self.buying_power: float = iq_data["buyingPower"]
        self.maintenance_excess: float = iq_data["maintenanceExcess"]
        self.is_real_time: bool = iq_data["isRealTime"]

    def __str__(self) -> str:  # pragma: no cover
        return f"${self.total_equity:,.2f} {self.currency.name}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class Balances:
    def __init__(self, iq_data: dict[str, list[dict[str, Any]]]):
        self.combined_balances = [Balance(x) for x in iq_data["combinedBalances"]]
        self.per_currency_balances = [Balance(x) for x in iq_data["perCurrencyBalances"]]
        self.sod_per_currency_balances = [Balance(x) for x in iq_data["sodPerCurrencyBalances"]]
        self.sod_combined_balances = [Balance(x) for x in iq_data["sodCombinedBalances"]]

    def __str__(self) -> str:  # pragma: no cover
        return self.per_currency_balances.__str__()

    def __repr__(self) -> str:  # pragma: no cover
        return self.per_currency_balances.__repr__()


class Position:
    def __init__(self, iq_data: dict[str, Any]):
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.open_quantity: float = iq_data["openQuantity"]
        self.closed_quantity: float = 0
        if "closedQuantity" in iq_data:
            self.closed_quantity = iq_data["closedQuantity"]
        self.current_market_value: float = iq_data["currentMarketValue"]
        self.current_price: float = iq_data["currentPrice"]
        self.average_entry_price: float = iq_data["averageEntryPrice"]
        self.closed_pnl: float = iq_data["closedPnl"]
        self.open_pnl: float = iq_data["openPnl"]
        self.day_pnl: float = 0.0
        if "dayPnl" in iq_data and iq_data["dayPnl"] is not None:
            self.day_pnl = iq_data["dayPnl"]
        self.total_cost: float = iq_data["totalCost"]
        self.is_real_time: bool = iq_data["isRealTime"]
        self.is_under_reorg: bool = iq_data["isUnderReorg"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.ticker} {self.open_quantity}@${self.average_entry_price:.2f}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __lt__(self, other: Position) -> bool:
        return self.ticker < other.ticker


class UnderlyingMultiplierPair:
    def __init__(self, iq_data: dict[str, Any]):
        self.multiplier: int = iq_data["multiplier"]
        self.underlying_symbol: str = iq_data["underlyingSymbol"]
        self.underlying_symbol_id: int = int(iq_data["underlyingSymbolId"])


class OptionContractDeliverables:
    def __init__(self, iq_data: dict[str, Any]):
        self.underlyings: list[UnderlyingMultiplierPair] = [
            UnderlyingMultiplierPair(pair) for pair in iq_data["underlyings"]
        ]
        self.cash_in_lieu: float = iq_data["cashInLieu"]


class MinTickData:
    def __init__(self, iq_data: dict[str, Any]):
        self.pivot: float = iq_data["pivot"]
        self.min_tick: float = iq_data["minTick"]


class TickerDetails:
    def __init__(self, iq_data: dict[str, Any]):
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.prev_day_close_price: float = iq_data["prevDayClosePrice"]
        self.high_price_52: float = iq_data["highPrice52"]
        self.low_price_52: float = iq_data["lowPrice52"]
        self.average_vol_3_months: int = iq_data["averageVol3Months"]
        self.average_vol_20_days: int = iq_data["averageVol20Days"]
        self.outstanding_shares: int = iq_data["outstandingShares"]
        self.eps: float = iq_data["eps"]
        self.pe: float = iq_data["pe"]
        self.dividend: float = iq_data["dividend"]
        self.div_yield: float = iq_data["yield"]
        self.ex_date: Optional[dt] = None
        if not iq_data["exDate"] is None:
            self.ex_date = dt.fromisoformat(iq_data["exDate"])
        self.market_cap: float = iq_data["marketCap"]
        self.option_type: OptionType = OptionType.Invalid
        if iq_data["optionType"] is not None:
            self.option_type = OptionType[iq_data["optionType"]]
        self.option_durationType: OptionDurationType = OptionDurationType.Invalid
        if iq_data["optionDurationType"] is not None:
            self.option_durationType = OptionDurationType[iq_data["optionDurationType"]]
        self.option_root: str = iq_data["optionRoot"]
        self.option_contract_deliverables: OptionContractDeliverables = OptionContractDeliverables(
            iq_data["optionContractDeliverables"]
        )
        self.min_ticks: list[MinTickData] = [MinTickData(x) for x in iq_data["minTicks"]]
        self.option_exercise_type: OptionExerciseType = OptionExerciseType.Invalid
        if iq_data["optionExerciseType"] is not None:
            self.option_exercise_type = OptionExerciseType[iq_data["optionExerciseType"]]
        self.listing_exchange: ListingExchange = ListingExchange[iq_data["listingExchange"]]
        self.description: str = iq_data["description"]
        self.security_type: SecurityType = SecurityType[iq_data["securityType"]]
        self.option_expiry_date: Optional[dt] = None
        if not iq_data["optionExpiryDate"] is None:
            self.option_expiry_date = dt.fromisoformat(iq_data["optionExpiryDate"])
        self.dividend_date: Optional[dt] = None
        if not iq_data["dividendDate"] is None:
            self.dividend_date = dt.fromisoformat(iq_data["dividendDate"])
        self.option_strike_price: float = iq_data["optionStrikePrice"]
        self.is_quotable: bool = iq_data["isQuotable"]
        self.has_options: bool = iq_data["hasOptions"]
        self.currency: Currency = Currency[iq_data["currency"]]
        self.industry_sector: str = iq_data["industrySector"]
        self.industry_group: str = iq_data["industryGroup"]
        self.industry_subgroup: str = iq_data["industrySubgroup"]

    def get_display_name(self) -> str:  # pragma: no cover
        if isinstance(self.option_expiry_date, dt):
            if self.option_root:
                return str(
                    self.option_root
                    + " "
                    + self.option_expiry_date.strftime("%d %b %Y")
                    + " "
                    + f"{self.option_strike_price:.2f}"
                    + " "
                    + self.option_type.name
                )
        return self.ticker

    def __str__(self) -> str:  # pragma: no cover
        return self.get_display_name()

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __lt__(self, other: TickerDetails) -> bool:
        return self.ticker < other.ticker


class OrderLeg:
    def __init__(self, iq_data: dict[str, Any]):
        self.leg_id: int = iq_data["legId"]
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.leg_ratio_quantity: int = iq_data["legRatioQuantity"]
        self.side: OrderSide = OrderSide[iq_data["side"]]
        self.avg_exec_price: float = iq_data["avgExecPrice"]
        self.last_exec_price: float = iq_data["lastExecPrice"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.side.name} {self.leg_ratio_quantity} {self.ticker}@{self.avg_exec_price}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class Order:
    def __init__(self, iq_data: dict[str, Any]):
        self.order_id: int = iq_data["id"]
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.total_quantity: int = iq_data["totalQuantity"]
        self.open_quantity: int = iq_data["openQuantity"]
        self.filled_quantity: int = iq_data["filledQuantity"]
        self.canceled_quantity: int = iq_data["canceledQuantity"]
        self.side: OrderSide = OrderSide[iq_data["side"]]
        self.order_type: OrderType = OrderType[iq_data["orderType"]]
        self.limit_price: float = iq_data["limitPrice"]
        self.stop_price: float = iq_data["stopPrice"]
        self.is_all_or_none: bool = iq_data["isAllOrNone"]
        self.is_anonymous: int = iq_data["isAnonymous"]
        self.iceberg_quantity: int = 0
        if "icebergQuantity" in iq_data and iq_data["icebergQuantity"] is not None:
            self.iceberg_quantity = iq_data["icebergQuantity"]
        self.min_quantity: int = iq_data["minQuantity"]
        self.avg_exec_price: float = iq_data["avgExecPrice"]
        self.last_exec_price: float = iq_data["lastExecPrice"]
        self.source: str = iq_data["source"]
        self.time_in_force: OrderTimeInForce = OrderTimeInForce[iq_data["timeInForce"]]
        self.gtd_date: Optional[dt] = None
        if not iq_data["gtdDate"] is None:
            self.gtd_date = dt.fromisoformat(iq_data["gtdDate"])
        self.order_state: OrderState = OrderState[iq_data["state"]]
        self.client_reason_str: str = ""
        if "clientReasonStr" in iq_data:
            self.client_reason_str = iq_data["clientReasonStr"]
        self.chain_id: int = iq_data["chainId"]
        self.creation_time: dt = dt.fromisoformat(iq_data["creationTime"])
        self.update_time: dt = dt.fromisoformat(iq_data["updateTime"])
        self.notes: str = iq_data["notes"]
        self.primary_route: str = iq_data["primaryRoute"]
        self.secondary_route: str = iq_data["secondaryRoute"]
        self.order_route: str = iq_data["orderRoute"]
        self.venue_holding_order: str = iq_data["venueHoldingOrder"]
        self.commission_charged: float = iq_data["comissionCharged"]  # sic
        self.exchange_order_id: str = iq_data["exchangeOrderId"]
        self.is_limit_offset_in_dollar: bool = iq_data["isLimitOffsetInDollar"]
        self.placement_commission: float = iq_data["placementCommission"]
        self.legs: list[OrderLeg] = [OrderLeg(leg) for leg in iq_data["legs"]]
        self.strategy_type: StrategyType = StrategyType[iq_data["strategyType"]]
        self.trigger_stop_price: float = iq_data["triggerStopPrice"]
        self.order_group_id: int = iq_data["orderGroupId"]
        self.order_class: OrderClass = OrderClass.Invalid
        if iq_data["orderClass"] is not None:
            self.order_class = OrderClass[iq_data["orderClass"]]

    def __str__(self) -> str:  # pragma: no cover
        price = "<unknown>"
        if self.order_type == OrderType.Market:
            price = "Market"
        elif self.order_type == OrderType.Limit:
            price = f"{self.limit_price:,.2f} Limit"
        elif self.order_type == OrderType.Stop:
            price = f"{self.stop_price:,.2f} Stop"
        elif self.order_type == OrderType.StopLimit:
            price = f"{self.limit_price:,.2f} Limit {self.stop_price:,.2f} Stop"
        elif self.order_type == OrderType.TrailStopInPercentage:
            price = f"{self.stop_price:,.2f}% TrlStop"
        elif self.order_type == OrderType.TrailStopInDollar:
            price = f"{self.stop_price:,.2f} TrlStop"
        elif self.order_type == OrderType.TrailStopLimitInPercentage:
            price = f"{self.limit_price:,.2f}% TrlLimit {self.stop_price:,.2f}% TrlStop"
        elif self.order_type == OrderType.TrailStopLimitInDollar:
            price = f"{self.limit_price:,.2f} TrlLimit {self.stop_price:,.2f} TrlStop"
        elif self.order_type == OrderType.LimitOnOpen:
            price = f"{self.limit_price:,.2f} LimitOnOpen"
        elif self.order_type == OrderType.LimitOnClose:
            price = f"{self.limit_price:,.2f} LimitOnClose"
        return str(
            self.side.name
            + " "
            + str(self.total_quantity)
            + " "
            + self.ticker
            + " "
            + self.strategy_type.name
            + " @ "
            + price
            + " "
            + self.time_in_force.name
            + " ("
            + self.order_state.name
            + ")"
        )

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class Execution:
    def __init__(self, iq_data: dict[str, Any]):
        self.execution_id: int = iq_data["id"]
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.quantity: int = iq_data["quantity"]
        self.side: OrderSide = OrderSide[iq_data["side"]]
        self.price: float = iq_data["price"]
        self.order_id: int = iq_data["orderId"]
        self.order_chain_id: int = iq_data["orderChainId"]
        self.exchange_exec_id: str = iq_data["exchangeExecId"]
        self.timestamp: dt = dt.fromisoformat(iq_data["timestamp"])
        self.notes: str = iq_data["notes"]
        self.venue: str = iq_data["venue"]
        self.total_cost: float = iq_data["totalCost"]
        self.order_placement_commission: float = iq_data["orderPlacementCommission"]
        self.commission: float = iq_data["commission"]
        self.execution_fee: float = iq_data["executionFee"]
        self.sec_fee: float = iq_data["secFee"]
        self.canadian_execution_fee: float = iq_data["canadianExecutionFee"]
        self.parent_id: int = iq_data["parentId"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.side.name} {self.quantity} {self.ticker} @ {self.price} ${self.total_cost}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class Ticker:
    def __init__(self, iq_data: dict[str, Any]):
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.description: str = iq_data["description"]
        self.security_type: SecurityType = SecurityType[iq_data["securityType"]]
        self.listing_exchange: ListingExchange = ListingExchange[iq_data["listingExchange"]]
        self.is_quotable: bool = iq_data["isQuotable"]
        self.is_tradable: bool = iq_data["isTradable"]
        self.currency: Currency = Currency[iq_data["currency"]]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.listing_exchange}:{self.ticker} - {self.description}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class Level1Quote:
    def __init__(self, iq_data: dict[str, Any]):
        self.ticker: str = iq_data["symbol"]
        self.symbol_id: int = iq_data["symbolId"]
        self.tier: str = ""
        if "tier" in iq_data:
            self.tier = iq_data["tier"]
        self.bid_price: float = iq_data["bidPrice"]
        self.bid_size: int = iq_data["bidSize"]
        self.ask_price: float = iq_data["askPrice"]
        self.ask_size: int = iq_data["askSize"]
        self.last_trade_tr_hrs: float = iq_data["lastTradePriceTrHrs"]
        self.last_trade_price: float = iq_data["lastTradePrice"]
        self.last_trade_size: int = iq_data["lastTradeSize"]
        self.last_trade_tick: TickType = TickType[iq_data["lastTradeTick"]]
        self.volume: int = iq_data["volume"]
        self.vwap: Optional[int] = None
        if "VWAP" in iq_data:
            self.vwap = int(iq_data["VWAP"])
        self.open_price: float = iq_data["openPrice"]
        self.high_price: float = iq_data["highPrice"]
        self.low_price: float = iq_data["lowPrice"]
        self.is_delayed: bool = iq_data["delay"]
        self.is_halted: str = iq_data["isHalted"]

    def get_display_name(self) -> str:  # pragma: no cover
        return self.ticker

    def __str__(self) -> str:  # pragma: no cover
        return (
            self.get_display_name()
            + " "
            + f"Last: {self.last_trade_price:.2f},{self.last_trade_size};"
            + " "
            + f"Bid: {self.bid_price},{self.bid_size};"
            + " "
            + f"Ask: {self.ask_price},{self.ask_size};"
            + " "
            + f"Volume: {self.volume}"
        )

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class Level1OptionData(Level1Quote):
    def __init__(self, iq_data: dict[str, Any]):
        super().__init__(iq_data)
        self.underlying: str = iq_data["underlying"]
        self.underlying_id: int = iq_data["underlyingId"]
        self.volatility: str = iq_data["volatility"]
        self.delta: str = iq_data["delta"]
        self.gamma: str = iq_data["gamma"]
        self.theta: str = iq_data["theta"]
        self.vega: str = iq_data["vega"]
        self.rho: str = iq_data["rho"]
        self.open_interest: str = iq_data["openInterest"]

    def get_display_name(self) -> str:  # pragma: no cover
        matcher = re.compile(f"{self.underlying}([0-9][0-9])([A-Z][a-z][a-z])([0-9][0-9])(C|P)([0-9]+\\.[0-9][0-9])")
        result = matcher.match(self.ticker)
        if result:
            expiry_date = result.group(1) + " " + result.group(2) + " 20" + result.group(3)
            if result.group(4) == "C":
                option_type = "Call"
            else:
                option_type = "Put"
            return self.underlying + " " + expiry_date + " " + f"{float(result.group(5)):.2f}" + " " + option_type
        return self.ticker


class ChainPerStrikePrice:
    def __init__(self, iq_data: dict[str, Any]):
        self.strike_price: float = iq_data["strikePrice"]
        self.call_symbol_id: int = iq_data["callSymbolId"]
        self.put_symbol_id: int = iq_data["putSymbolId"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.strike_price:.2f}"

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class ChainPerRoot:
    def __init__(self, iq_data: dict[str, Any]):
        self.option_root: str = iq_data["optionRoot"]
        chain_per_strike_price = [ChainPerStrikePrice(x) for x in iq_data["chainPerStrikePrice"]]
        self.chain_per_strike_price: dict[float, ChainPerStrikePrice] = {
            chain.strike_price: chain for chain in chain_per_strike_price
        }
        self.multiplier: float = iq_data["multiplier"]

    def __str__(self) -> str:  # pragma: no cover
        return self.option_root + " " + str(self.chain_per_strike_price)

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class ChainPerExpiryDate:
    def __init__(self, iq_data: dict[str, Any]):
        self.expiry_date: dt = dt.fromisoformat(iq_data["expiryDate"])
        self.description: str = iq_data["description"]
        self.listing_exchange: ListingExchange = ListingExchange[iq_data["listingExchange"]]
        self.option_exercise_type: OptionExerciseType = OptionExerciseType.Invalid
        if iq_data["optionExerciseType"] is not None:
            self.option_exercise_type = OptionExerciseType[iq_data["optionExerciseType"]]
        chain_per_root = [ChainPerRoot(x) for x in iq_data["chainPerRoot"]]
        self.chain_per_root: dict[str, ChainPerRoot] = {chain.option_root: chain for chain in chain_per_root}

    def __str__(self) -> str:  # pragma: no cover
        return self.expiry_date.strftime("%d %b %Y") + " " + str(self.chain_per_root)

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()


class OptionIdFilter:
    def __init__(
        self,
        option_type: OptionType,
        underlying_id: int,
        expiry_date: dt,
        min_strike_price: float,
        max_strike_price: float,
    ):
        self.option_type: OptionType = option_type
        self.underlying_id: int = underlying_id
        self.expiry_date: dt = expiry_date
        self.min_strike_price: float = min_strike_price
        self.max_strike_price: float = max_strike_price

    def to_json(self) -> dict[str, Any]:
        values = {}
        values["optionType"] = self.option_type.name
        values["underlyingId"] = str(self.underlying_id)
        values["expiryDate"] = self.expiry_date.isoformat()
        values["minstrikePrice"] = f"{self.min_strike_price:.2f}"
        values["maxstrikePrice"] = f"{self.max_strike_price:.2f}"
        return values


class StrategyLeg:
    def __init__(self, symbol_id: int, action: OrderAction, ratio: int) -> None:
        self.symbol_id = symbol_id
        self.action = action
        self.ratio = ratio

    def to_json(self) -> dict[str, Any]:
        result = {
            "symbolId": self.symbol_id,
            "action": self.action.name,
            "ratio": self.ratio,
        }
        return result


class StrategyVariantRequest:
    def __init__(self, variant_id: int, strategy: StrategyType, legs: list[StrategyLeg]) -> None:
        self.variant_id = variant_id
        self.strategy = strategy
        self.legs = legs

    def to_json(self) -> dict[str, Any]:
        result = {
            "variantId": self.variant_id,
            "strategy": self.strategy.name,
            "legs": [leg.to_json() for leg in self.legs],
        }
        return result


class StrategyVariantQuote:
    def __init__(self, iq_data: dict[str, Any]):
        self.variant_id: int = iq_data["variantId"]
        self.bid_price: Optional[float] = iq_data["bidPrice"]
        self.ask_price: Optional[float] = iq_data["askPrice"]
        self.underlying: str = iq_data["underlying"]
        self.underlying_id: int = iq_data["underlyingId"]
        self.open_price: Optional[float] = iq_data["openPrice"]
        self.volatility: float = iq_data["volatility"]
        self.delta: float = iq_data["delta"]
        self.gamma: float = iq_data["gamma"]
        self.theta: float = iq_data["theta"]
        self.vega: float = iq_data["vega"]
        self.rho: float = iq_data["rho"]
        self.is_real_time: bool = iq_data["isRealTime"]


class Candle:
    def __init__(self, iq_data: dict[str, Any]):
        self.start: str = iq_data["start"]
        self.end: str = iq_data["end"]
        self.open: float = iq_data["open"]
        self.high: float = iq_data["high"]
        self.low: float = iq_data["low"]
        self.close: float = iq_data["close"]
        self.volume: int = iq_data["volume"]
        self.vwap: Optional[int] = None
        if "VWAP" in iq_data:
            self.vwap = iq_data["VWAP"]


class QuestradeIQ:
    def __init__(self, config: Union[str, dict[str, Any]] = "secrets.json", save_config: bool = True):
        """Constructor

        Parameters
        ----------
        config : Union[str, dict], optional
            Config filename or dictionary.
                If a dict, key/value pairs for configuration, by default "secrets.json"
        """
        self._should_save_config = save_config
        if isinstance(config, str):
            self._config_filename = config
            with open(self._config_filename, "r") as infile:
                self._config = json.load(infile)
        elif isinstance(config, dict):
            self._config_filename = ""
            self._config = config.copy()  # make a copy here to not modify the caller's dict
        else:
            raise TypeError("'config' argument type should be str or dict")

        if "iq_refresh_token" not in self._config:
            raise ValueError("'iq_refresh_token' key not found in config")

        self._api_server = ""
        self._access_token = ""
        self._token_type = ""
        self._api_url: Optional[urllib.parse.ParseResult] = None

        self.session = requests.Session()
        self._get_access_token()

    def get_api_server(self) -> str:
        return self._api_server

    def get_access_token(self) -> str:
        return self._access_token

    def get_access_token_type(self) -> str:
        return self._token_type

    def get_api_url(self) -> urllib.parse.ParseResult:
        if self._api_url is not None:
            return self._api_url
        raise AttributeError("'api_url' is None")  # pragma: no cover

    def _save_config(self) -> None:
        assert "iq_refresh_token" in self._config
        if self._config_filename != "" and self._should_save_config:
            with open(self._config_filename, "w") as outfile:
                json.dump(self._config, outfile, indent=4)

    def _set_config_value(self, key: str, value: Any) -> None:
        self._config[key] = value
        self._save_config()

    def _get_config_value(self, key: str) -> Any:
        return self._config[key]

    def _get_access_token(self) -> None:
        refresh_token_key = "iq_refresh_token"
        refresh_token = self._get_config_value(refresh_token_key)

        access_token_url = (
            f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token}"
        )
        access_token_result = requests.get(access_token_url, timeout=10)
        access_token_result.raise_for_status()

        access_token_data = access_token_result.json()
        if (
            "access_token" not in access_token_data
            or "api_server" not in access_token_data
            or "refresh_token" not in access_token_data
        ):
            raise RuntimeError("Invalid refresh token response: {0}".format(access_token_result.text))

        refresh_token = access_token_data["refresh_token"]
        self._set_config_value(refresh_token_key, refresh_token)

        self._access_token = access_token_data["access_token"]
        self._api_server = access_token_data["api_server"]
        if self._api_server[-1] == "/":
            self._api_server = self._api_server[:-1]

        self._api_url = urllib.parse.urlparse(self._api_server)

        if "token_type" in access_token_data:
            self._token_type = access_token_data["token_type"]
        else:
            self._token_type = "Bearer"  # pragma: no cover

        auth_headers = {"Authorization": self._token_type + " " + self._access_token}
        self.session.headers.update(auth_headers)

    def _make_request(
        self,
        request_path: str,
        *,
        method: str = "GET",
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        request_url = f"{self._api_server}/v1/{request_path}"
        response = self.session.request(method, request_url, params=params, json=json)
        response.raise_for_status()
        json_response = response.json()
        assert isinstance(json_response, dict)
        return json_response

    def get_time(self) -> dt:
        """Retrieves current server time.

        Returns:
            Current server time in ISO format and Eastern time zone.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/time
        """
        response = self._make_request("time")
        if "time" not in response:
            raise RuntimeError("Invalid respose received")
        return dt.fromisoformat(response["time"])

    def get_accounts(self) -> list[AccountInfo]:
        """Retrieves the accounts associated with the user on behalf of which the API client is authorized.

        Returns:
            List of accounts.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts
        """
        response = self._make_request("accounts")
        if "accounts" not in response:
            raise RuntimeError("Invalid respose received")
        return [AccountInfo(account) for account in response["accounts"]]

    def get_activities(
        self, account_id: Union[str, AccountInfo], start_time: dt, end_time: dt
    ) -> list[AccountActivity]:
        """Retrieves executions for a specific account.

        Args:
            account_id: The account number.
            start_time: The start time of the interval to retrieve orders.
            end_time: The end time of the interval to retrieve orders.

        Returns:
            list[AccountActivity]: The list of activities for the specific account.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts-id-activities
        """
        query = {"startTime": start_time.isoformat(), "endTime": end_time.isoformat()}
        response = self._make_request(f"accounts/{AccountInfo.get_account_number(account_id)}/activities", params=query)
        if "activities" not in response:
            raise RuntimeError("Invalid respose received")
        return [AccountActivity(activity) for activity in response["activities"]]

    def get_balances(self, account_id: Union[str, AccountInfo]) -> Balances:
        """Retrieves per-currency and combined balances for a specified account.

        Args:
            account_id: Account number.

        Returns:
            Dictionary of balance types.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts-id-balances
        """
        response = self._make_request(f"accounts/{AccountInfo.get_account_number(account_id)}/balances")
        if (
            "perCurrencyBalances" not in response
            or "combinedBalances" not in response
            or "sodPerCurrencyBalances" not in response
            or "sodCombinedBalances" not in response
        ):
            raise RuntimeError("Invalid respose received")
        return Balances(response)

    def get_positions(self, account_id: Union[str, AccountInfo]) -> list[Position]:
        """Retrieves positions in a specified account.

        Args:
            account_id: Account number.

        Returns:
            List of positions.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts-id-positions
        """
        response = self._make_request(f"accounts/{AccountInfo.get_account_number(account_id)}/positions")
        if "positions" not in response:
            raise RuntimeError("Invalid respose received")
        return [Position(position) for position in response["positions"]]

    def get_orders(
        self,
        account_id: Union[str, AccountInfo],
        *,
        start_time: Optional[dt] = None,
        end_time: Optional[dt] = None,
        state_filter: Optional[OrderStateFilter] = None,
    ) -> list[Order]:
        """Retrieves orders for specified account

        Args:
            account_id: Account number.
            start_time: Start of time range in ISO format. By default – start of today, 12:00am.
            end_time: End of time range in ISO format. By default – end of today, 11:59pm
            state_filter: All, Open, Closed – retrieve all, active or closed orders. Defaults to All.

        Returns:
            List of orders.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts-id-orders
        """
        query = {}
        if start_time is not None:
            if not isinstance(start_time, dt):
                raise TypeError("Type of 'start_time' must be datetime")
            query["startTime"] = start_time.isoformat()
        if end_time is not None:
            if not isinstance(end_time, dt):
                raise TypeError("Type of 'end_time' must be datetime")
            query["endTime"] = end_time.isoformat()
        if state_filter:
            if not isinstance(state_filter, OrderStateFilter):
                raise TypeError("Type of 'state_filter' must be OrderStateFilter")  # pragma: no cover
            query["stateFilter"] = state_filter.name
        response = self._make_request(f"accounts/{AccountInfo.get_account_number(account_id)}/orders", params=query)
        if "orders" not in response:
            raise RuntimeError("Invalid respose received")
        return [Order(order) for order in response["orders"]]

    def get_order(self, account_id: Union[str, AccountInfo], orderId: Union[str, int]) -> list[Order]:
        """Retrieves a specific order for specified account

        Args:
            account_id: Account number.
            orderId: Order number.

        Returns:
            Details for the specified order.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts-id-orders
        """
        response = self._make_request(f"accounts/{AccountInfo.get_account_number(account_id)}/orders/{orderId}")
        if "orders" not in response:
            raise RuntimeError("Invalid respose received")
        return [Order(order) for order in response["orders"]]

    def get_executions(
        self,
        account_id: Union[str, AccountInfo],
        *,
        start_time: Optional[dt] = None,
        end_time: Optional[dt] = None,
    ) -> list[Execution]:
        """Retrieves executions for a specific account.

        Args:
            account_id: Account number.
            start_time: Start of time range in ISO format. By default – start of today, 12:00am.
            end_time: End of time range in ISO format. By default – end of today, 11:59pm

        Returns:
            List of executions.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/account-calls/accounts-id-executions
        """
        query = {}
        if start_time is not None:
            if not isinstance(start_time, dt):
                raise TypeError("Type of 'start_time' must be datetime")
            query["startTime"] = start_time.isoformat()
        if end_time is not None:
            if not isinstance(end_time, dt):
                raise TypeError("Type of 'end_time' must be datetime")
            query["endTime"] = end_time.isoformat()
        response = self._make_request(f"accounts/{AccountInfo.get_account_number(account_id)}/executions", params=query)
        if "executions" not in response:
            raise RuntimeError("Invalid respose received")
        return [Execution(execution) for execution in response["executions"]]

    def get_tickers(
        self,
        tickers: Union[
            list[str], set[str], str, list[Ticker], Ticker, list[TickerDetails], TickerDetails, list[int], set[int], int
        ],
    ) -> list[TickerDetails]:
        """Retrieves detailed information about the given symbols.

        Args:
            tickers: List of, or set, or single ticker name or id.

        Returns:
            List of symbols.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/market-calls/symbols-id
        """
        ids: list[str] = []
        names: list[str] = []
        if isinstance(tickers, int):
            ids.append(str(tickers))
        elif isinstance(tickers, (Ticker, TickerDetails)):
            ids.append(str(tickers.symbol_id))
        elif isinstance(tickers, str):
            names.append(tickers)
        elif isinstance(tickers, set):
            for set_element in tickers:
                if isinstance(set_element, int):
                    ids.append(str(set_element))
                elif isinstance(set_element, str):
                    names.append(set_element)
                else:
                    raise TypeError("Invalid set type for 'tickers'")
        elif isinstance(tickers, list):
            for list_element in tickers:
                if isinstance(list_element, int):
                    ids.append(str(list_element))
                elif isinstance(list_element, (Ticker, TickerDetails)):
                    ids.append(str(list_element.symbol_id))
                elif isinstance(list_element, str):
                    names.append(list_element)
                else:
                    raise TypeError("Invalid list type for 'tickers'")
        else:
            raise TypeError("Invalid type for 'tickers'")
        query: dict[str, str] = {}
        if len(ids):
            query["ids"] = ",".join(ids)
        if len(names):
            query["names"] = ",".join(names)
        response = self._make_request("symbols", params=query)
        if "symbols" not in response:
            raise RuntimeError("Invalid respose received")
        return [TickerDetails(symbol) for symbol in response["symbols"]]

    def search_for_symbols(self, prefix: str, offset: Optional[int] = None) -> list[Ticker]:
        """Retrieves symbol(s) using several search criteria.

        Args:
            prefix: Prefix of a symbol or any word in the description.
            offset: Offset in number of records from the beginning of a result set. Defaults to None.

        Returns:
            List of EquitySymbols found.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/market-calls/symbols-search
        """
        query = {"prefix": prefix}
        if offset is not None:
            query["offset"] = str(offset)
        response = self._make_request("symbols/search", params=query)
        if "symbols" not in response:
            raise RuntimeError("Invalid respose received")
        return [Ticker(symbol) for symbol in response["symbols"]]

    def get_option_chain(self, ticker: Union[str, Ticker, TickerDetails, int]) -> dict[dt, ChainPerExpiryDate]:
        """Retrieves an option chain for a particular underlying symbol.

        Args:
            ticker: String or id of the ticker.

        Returns:
            List of ChainPerExpiryDate for the underlying symbol
        """
        if isinstance(ticker, str):
            symbol_id = self.get_tickers(ticker)[0].symbol_id
        elif isinstance(ticker, (Ticker, TickerDetails)):
            symbol_id = ticker.symbol_id
        elif isinstance(ticker, int):
            symbol_id = ticker
        else:
            raise TypeError("Invalid type for 'ticker'")
        response = self._make_request(f"symbols/{symbol_id}/options")
        if "optionChain" not in response:
            raise RuntimeError("Invalid respose received")
        return {chain.expiry_date: chain for chain in [ChainPerExpiryDate(chain) for chain in response["optionChain"]]}

    def get_quote(
        self,
        tickers: Union[
            list[str], set[str], str, list[Ticker], Ticker, list[TickerDetails], TickerDetails, list[int], set[int], int
        ],
    ) -> list[Level1Quote]:
        """Retrieves a single Level 1 market data quote for one or more symbols.

        Args:
            tickers: List of, or set, or single ticker name or id.

        Returns:
            List of quotes for the given symbols.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-quotes-id
        """
        ids: list[str] = []
        if isinstance(tickers, int):
            ids.append(str(tickers))
        elif isinstance(tickers, (Ticker, TickerDetails)):
            ids.append(str(tickers.symbol_id))
        elif isinstance(tickers, str):
            ids.append(str(self.get_tickers(tickers)[0].symbol_id))
        elif isinstance(tickers, set):
            for element in tickers:
                if isinstance(element, int):
                    ids.append(str(element))
                elif isinstance(element, str):
                    ids.append(str(self.get_tickers(element)[0].symbol_id))
                else:
                    raise TypeError("Invalid set type for 'tickers'")
        elif isinstance(tickers, list):
            for item in tickers:
                if isinstance(item, int):
                    ids.append(str(item))
                elif isinstance(item, (Ticker, TickerDetails)):
                    ids.append(str(item.symbol_id))
                elif isinstance(item, str):
                    ids.append(str(self.get_tickers(item)[0].symbol_id))
                else:
                    raise TypeError("Invalid list type for 'tickers'")
        else:
            raise TypeError("Invalid type for 'tickers'")
        query: dict[str, str] = {}
        if len(ids):
            query["ids"] = ",".join(ids)
        response = self._make_request("markets/quotes", params=query)
        if "quotes" not in response:
            raise RuntimeError("Invalid respose received")
        return [Level1Quote(quote) for quote in response["quotes"]]

    def get_option_quotes(
        self,
        ids: Union[int, list[int]],
        *,
        filters: Optional[list[OptionIdFilter]] = None,
    ) -> list[Level1OptionData]:
        """Retrieves a single Level 1 market data quote and Greek data for one or more option symbols.

        Args:
            ids: Input array of option IDs
            filters: Input array of OptionIdFilters

        Returns:
            List of Level1OptionData quotes.

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-quotes-options
        """
        query: dict[str, Any] = {}
        if isinstance(ids, int):
            query["optionIds"] = [ids]
        elif isinstance(ids, list):
            if len(ids) == 0:
                return []
            elif isinstance(ids[0], int):
                query["optionIds"] = ids
            else:
                raise TypeError("Invalid list type for 'ids'")
        else:
            raise TypeError("Invalid type for 'ids'")
        if isinstance(filters, list):
            query["filters"] = [filter.to_json() for filter in filters]
        response = self._make_request("markets/quotes/options", method="POST", json=query)
        if "optionQuotes" not in response:
            raise RuntimeError("Invalid respose received")
        return [Level1OptionData(quote) for quote in response["optionQuotes"]]

    def get_strategy_quotes(self, variants: list[StrategyVariantRequest]) -> list[StrategyVariantQuote]:
        """Retrieve a calculated L1 market data quote for a single or many multi-leg strategies.

        Args:
            variants: Input array of StrategyVariantsRequests

        Returns:
            List of StrategyVariantQuotes

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-quotes-strategies
        """
        if not isinstance(variants, list):
            raise TypeError("Invalid type for 'variants', expecting list")
        if not all(isinstance(x, StrategyVariantRequest) for x in variants):
            raise TypeError("Invalid element type for 'variants', expecting StrategyVariantRequest")

        query = {"variants": [variant.to_json() for variant in variants]}
        response = self._make_request("markets/quotes/strategies", method="POST", json=query)
        if "strategyQuotes" not in response:
            raise RuntimeError("Invalid respose received")
        return [StrategyVariantQuote(quote) for quote in response["strategyQuotes"]]

    def get_candles(
        self,
        ticker: Union[str, Ticker, TickerDetails, int],
        interval: Granularity,
        start_time: dt,
        end_time: dt,
        raw_data: bool = False,
    ) -> Union[list[Candle], dict[str, Any]]:
        """Retrieves historical market data in the form of OHLC candlesticks for a specified symbol.

            This call is limited to returning 2,000 candlesticks in a single response.

        Args:
            ticker: Symbol identifier.
            interval: Interval of a single candlestick.
            start_time: Beginning of the candlestick range.
            end_time: End of the candlestick range.

        Returns:
            List of Candles

        See Also:
            https://www.questrade.com/api/documentation/rest-operations/market-calls/markets-candles-id
        """
        id: int = 0
        if isinstance(ticker, int):
            id = ticker
        elif isinstance(ticker, (Ticker, TickerDetails)):
            id = ticker.symbol_id
        elif isinstance(ticker, str):
            id = self.get_tickers(ticker)[0].symbol_id
        else:
            raise TypeError("Invalid type for 'ticker'")
        query = {
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
            "interval": interval.name,
        }
        response = self._make_request(f"markets/candles/{id}", params=query)
        if "candles" not in response:
            raise RuntimeError("Invalid respose received")  # pragma: no cover
        return response["candles"] if raw_data else [Candle(candle) for candle in response["candles"]]

    def setup_streaming_notifications(self, socket_mode: SocketMode) -> int:
        """Retrieves the port number used for notification streaming.

        Args:
            socket_mode: Either RawSocket or WebSocket.

        Returns:
            The port number to connect to with ether raw or web sockets as requested.

        See Also:
            https://www.questrade.com/api/documentation/streaming
        """
        query = {"mode": socket_mode.name}
        response = self._make_request("notifications", params=query)
        if "streamPort" not in response:
            raise RuntimeError("Invalid respose received")  # pragma: no cover
        return int(response["streamPort"])

    def setup_streaming_quotes(self, ids: list[int], socket_mode: SocketMode) -> int:
        """Retrieves the port number used for L1 quote streaming.

        Args:
            ids: List of symbol ids to stream.
            socket_mode: Either RawSocket or WebSocket.

        Returns:
            The port number to connect to with ether raw or web sockets as requested.

        See Also:
            https://www.questrade.com/api/documentation/streaming
        """
        query = {"ids": ",".join([str(id) for id in ids]), "stream": "true", "mode": socket_mode.name}
        response = self._make_request("markets/quotes", params=query)
        if "streamPort" not in response:
            raise RuntimeError("Invalid respose received")  # pragma: no cover
        return int(response["streamPort"])
