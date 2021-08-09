from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from unittest import mock

import pytest
import requests_mock
from pytz import timezone
from requests.models import HTTPError

import iqtrade.api as iq

REFRESH_TOKEN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

TEST_MOCK_API_SERVER = "https://api01.iq.questrade.com/"

TEST_REFRESH_TOKEN_VALID = "this_refresh_token_is_valid"
TEST_REFRESH_TOKEN_INVALID = "this_refresh_token_is_NOT_valid"

TEST_VALID_CONFIG = {"iq_refresh_token": TEST_REFRESH_TOKEN_VALID}
TEST_INVALID_CONFIG = {"iq_refresh_token": TEST_REFRESH_TOKEN_INVALID}

ACCESS_TOKEN_RESPONSE = {
    "access_token": "this_access_token_is_valid",
    "refresh_token": "this_is_your_new_refresh_token",
    "token_type": "Bearer",
    "api_server": TEST_MOCK_API_SERVER,
}

TEST_AAPL_SYMBOL = {
    "symbols": [
        {
            "symbol": "AAPL",
            "currency": "USD",
            "symbolId": 8049,
            "prevDayClosePrice": 102.5,
            "highPrice52": 102.9,
            "lowPrice52": 63.89,
            "averageVol3Months": 43769680,
            "averageVol20Days": 12860370,
            "outstandingShares": 5987867000,
            "eps": 6.2,
            "pe": 16.54,
            "dividend": 0.47,
            "yield": 1.84,
            "exDate": "2014-08-07T00:00:00.000000-04:00",
            "marketCap": 613756367500,
            "tradeUnit": 1,
            "optionType": None,
            "optionDurationType": None,
            "optionRoot": "",
            "optionContractDeliverables": {"underlyings": [], "cashInLieu": 0},
            "optionExerciseType": None,
            "listingExchange": "NASDAQ",
            "description": "APPLE INC",
            "securityType": "Stock",
            "optionExpiryDate": None,
            "dividendDate": "2014-08-14T00:00:00.000000-04:00",
            "optionStrikePrice": None,
            "isTradable": True,
            "isQuotable": True,
            "hasOptions": True,
            "minTicks": [{"pivot": 0, "minTick": 0.0001}, {"pivot": 1, "minTick": 0.01}],
            "industrySector": "BasicMaterials",
            "industryGroup": "Steel",
            "industrySubgroup": "Steel",
        },
    ]
}

TEST_AAPL_QUOTE = {
    "quotes": [
        {
            "symbol": "AAPL",
            "symbolId": 8049,
            "tier": " ",
            "bidPrice": 101.4,
            "bidSize": 6500,
            "askPrice": 102.3,
            "askSize": 9100,
            "lastTradePriceTrHrs": 101.9,
            "lastTradePrice": 101.90,
            "lastTradeSize": 3100,
            "lastTradeTick": "Equal",
            "lastTradeTime": "2014-10-24T20:06:40.131000-04:00",
            "volume": 80483500,
            "openPrice": 101.1,
            "highPrice": 102.7,
            "lowPrice": 101.05,
            "delay": 0,
            "isHalted": False,
        },
    ]
}

TEST_ACCOUNTS_RESPONSE = {
    "accounts": [
        {
            "type": "Margin",
            "number": "26598145",
            "status": "Active",
            "isPrimary": True,
            "isBilling": True,
            "clientAccountType": "Individual",
        }
    ]
}

TEST_BALANCES_RESPONSE = {
    "perCurrencyBalances": [
        {
            "currency": "CAD",
            "cash": 243971.7,
            "marketValue": 6017,
            "totalEquity": 249988.7,
            "buyingPower": 496367.2,
            "maintenanceExcess": 248183.6,
            "isRealTime": False,
        },
        {
            "currency": "USD",
            "cash": 198259.05,
            "marketValue": 53745,
            "totalEquity": 252004.05,
            "buyingPower": 461013.3,
            "maintenanceExcess": 230506.65,
            "isRealTime": False,
        },
    ],
    "combinedBalances": [
        {
            "currency": "CAD",
            "cash": 243971.7,
            "marketValue": 6017,
            "totalEquity": 249988.7,
            "buyingPower": 496367.2,
            "maintenanceExcess": 248183.6,
            "isRealTime": False,
        },
        {
            "currency": "USD",
            "cash": 198259.05,
            "marketValue": 53745,
            "totalEquity": 252004.05,
            "buyingPower": 461013.3,
            "maintenanceExcess": 230506.65,
            "isRealTime": False,
        },
    ],
    "sodPerCurrencyBalances": [
        {
            "currency": "CAD",
            "cash": 243971.7,
            "marketValue": 6017,
            "totalEquity": 249988.7,
            "buyingPower": 496367.2,
            "maintenanceExcess": 248183.6,
            "isRealTime": False,
        },
        {
            "currency": "USD",
            "cash": 198259.05,
            "marketValue": 53745,
            "totalEquity": 252004.05,
            "buyingPower": 461013.3,
            "maintenanceExcess": 230506.65,
            "isRealTime": False,
        },
    ],
    "sodCombinedBalances": [
        {
            "currency": "CAD",
            "cash": 243971.7,
            "marketValue": 6017,
            "totalEquity": 249988.7,
            "buyingPower": 496367.2,
            "maintenanceExcess": 248183.6,
            "isRealTime": False,
        },
        {
            "currency": "USD",
            "cash": 198259.05,
            "marketValue": 53745,
            "totalEquity": 252004.05,
            "buyingPower": 461013.3,
            "maintenanceExcess": 230506.65,
            "isRealTime": False,
        },
    ],
}

TEST_ACTIVITIES_RESPONSE = {
    "activities": [
        {
            "tradeDate": "2011-02-16T00:00:00.000000-05:00",
            "transactionDate": "2011-02-16T00:00:00.000000-05:00",
            "settlementDate": "2011-02-16T00:00:00.000000-05:00",
            "action": "",
            "symbol": "",
            "symbolId": 0,
            "description": "INT FR 02/04 THRU02/15@ 4 3/4%BAL 205,006 AVBAL 204,966",
            "currency": "USD",
            "quantity": 0,
            "price": 0,
            "grossAmount": 0,
            "commission": 0,
            "netAmount": -320.08,
            "type": "Interest",
        },
    ]
}

TEST_POSITIONS_RESPONSE = {
    "positions": [
        {
            "symbol": "THI.TO",
            "symbolId": 38738,
            "openQuantity": 100,
            "closedQuantity": 0,
            "currentMarketValue": 6017,
            "currentPrice": 60.17,
            "averageEntryPrice": 60.23,
            "closedPnl": 0,
            "openPnl": -6,
            "dayPnl": 0,
            "totalCost": 6023.00,
            "isRealTime": True,
            "isUnderReorg": False,
        }
    ]
}

TEST_ORDERS_RESPONSE = {
    "orders": [
        {
            "id": 173577870,
            "symbol": "AAPL",
            "symbolId": 8049,
            "totalQuantity": 100,
            "openQuantity": 100,
            "filledQuantity": 0,
            "canceledQuantity": 0,
            "side": "Buy",
            "orderType": "Limit",
            "limitPrice": 500.95,
            "stopPrice": None,
            "isAllOrNone": False,
            "isAnonymous": False,
            "icebergQty": None,
            "minQuantity": None,
            "avgExecPrice": None,
            "lastExecPrice": None,
            "source": "TradingAPI",
            "timeInForce": "Day",
            "gtdDate": None,
            "state": "Canceled",
            "clientReasonStr": "",
            "chainId": 173577870,
            "creationTime": "2014-10-23T20:03:41.636000-04:00",
            "updateTime": "2014-10-23T20:03:42.890000-04:00",
            "notes": "",
            "primaryRoute": "AUTO",
            "secondaryRoute": "",
            "orderRoute": "LAMP",
            "venueHoldingOrder": "",
            "comissionCharged": 0,
            "exchangeOrderId": "XS173577870",
            "isSignificantShareHolder": False,
            "isInsider": False,
            "isLimitOffsetInDollar": False,
            "userId": 3000124,
            "placementCommission": None,
            "legs": [],
            "strategyType": "SingleLeg",
            "triggerStopPrice": None,
            "orderGroupId": 0,
            "orderClass": None,
            "mainChainId": 0,
        },
    ]
}

TEST_EXEUCTIONS_RESPONSE = {
    "executions": [
        {
            "symbol": "AAPL",
            "symbolId": 8049,
            "quantity": 10,
            "side": "Buy",
            "price": 536.87,
            "id": 53817310,
            "orderId": 177106005,
            "orderChainId": 17710600,
            "exchangeExecId": "XS1771060050147",
            "timestamp": "2014-03-31T13:38:29.000000-04:00",
            "notes": "",
            "venue": "LAMP",
            "totalCost": 5368.7,
            "orderPlacementCommission": 0,
            "commission": 4.95,
            "executionFee": 0,
            "secFee": 0,
            "canadianExecutionFee": 0,
            "parentId": 0,
        }
    ]
}

TEST_SEARCH_RESPONSE = {
    "symbols": [
        {
            "symbol": "BMO",
            "symbolId": 9292,
            "description": "BANK OF MONTREAL",
            "securityType": "Stock",
            "listingExchange": "NYSE",
            "isTradable": True,
            "isQuotable": True,
            "currency": "USD",
        },
        {
            "symbol": "BMO.PRJ.TO",
            "symbolId": 9300,
            "description": "BANK OF MONTREAL CL B SR 13",
            "securityType": "Stock",
            "listingExchange": "TSX",
            "isTradable": True,
            "isQuotable": True,
            "currency": "CAD",
        },
    ]
}

TEST_OPTIONS_RESPONSE = {
    "optionChain": [
        {
            "expiryDate": "2015-01-17T00:00:00.000000-05:00",
            "description": "BANK OF MONTREAL",
            "listingExchange": "MX",
            "optionExerciseType": "American",
            "chainPerRoot": [
                {
                    "optionRoot": "BMO",
                    "chainPerStrikePrice": [
                        {"strikePrice": 60, "callSymbolId": 6101993, "putSymbolId": 6102009},
                        {"strikePrice": 62, "callSymbolId": 6101994, "putSymbolId": 6102010},
                        {"strikePrice": 64, "callSymbolId": 6101995, "putSymbolId": 6102011},
                    ],
                    "multiplier": 100,
                }
            ],
        }
    ]
}

TEST_OPTIONS_QUOTE_RESPONSE = {
    "optionQuotes": [
        {
            "underlying": "MSFT",
            "underlyingId": 27426,
            "symbol": "MSFT20Jan17C70.00",
            "symbolId": 7413503,
            "bidPrice": 4.90,
            "bidSize": 0,
            "askPrice": 4.95,
            "askSize": 0,
            "lastTradePriceTrHrs": 4.93,
            "lastTradePrice": 4.93,
            "lastTradeSize": 0,
            "lastTradeTick": "Equal",
            "lastTradeTime": "2015-08-17T00:00:00.000000-04:00",
            "volume": 0,
            "openPrice": 0,
            "highPrice": 4.93,
            "lowPrice": 0,
            "volatility": 52.374257,
            "delta": 0.06985,
            "gamma": 0.01038,
            "theta": -0.001406,
            "vega": 0.074554,
            "rho": 0.04153,
            "openInterest": 2292,
            "delay": 0,
            "isHalted": False,
            "VWAP": 0,
        },
    ]
}

TEST_STRATEGY_QUOTE_RESPONSE = {
    "strategyQuotes": [
        {
            "variantId": 1,
            "bidPrice": 27.2,
            "askPrice": 27.23,
            "underlying": "MSFT",
            "underlyingId": 27426,
            "openPrice": None,
            "volatility": 0,
            "delta": 1,
            "gamma": 0,
            "theta": 0,
            "vega": 0,
            "rho": 0,
            "isRealTime": True,
        },
    ]
}

TEST_CANDLES_RESPONSE = {
    "candles": [
        {
            "start": "2014-01-02T00:00:00.000000-05:00",
            "end": "2014-01-03T00:00:00.000000-05:00",
            "low": 70.3,
            "high": 70.78,
            "open": 70.68,
            "close": 70.73,
            "volume": 983609,
        },
    ]
}


@pytest.fixture()  # type: ignore
def m() -> Any:
    with requests_mock.Mocker() as m:
        yield m


def reset_mock(m: requests_mock.Mocker) -> None:
    m.reset_mock()  # type: ignore


def test_config_file_missing(m: requests_mock.Mocker) -> None:
    with pytest.raises(FileNotFoundError):
        iq.QuestradeIQ("non-existing-file.json")
    assert not m.called


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data=json.dumps(TEST_VALID_CONFIG))
def test_config_file_open(om: mock.MagicMock, m: requests_mock.Mocker) -> None:
    filename = "mysettings.json"
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    iq.QuestradeIQ(filename)
    om.assert_any_call(filename, "r")
    om.assert_called_with(filename, "w")
    assert len(m.request_history) == 1


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data=json.dumps(TEST_VALID_CONFIG))
def test_config_file_open_but_not_saved(om: mock.MagicMock, m: requests_mock.Mocker) -> None:
    filename = "mysettings.json"
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    iq.QuestradeIQ(filename, safe_config=False)
    om.assert_called_once_with(filename, "r")
    assert len(m.request_history) == 1


def test_config_dict_invalid(m: requests_mock.Mocker) -> None:
    with pytest.raises(TypeError):
        iq.QuestradeIQ(False)  # type: ignore
    with pytest.raises(ValueError):
        iq.QuestradeIQ({})
    assert not m.called


def test_config_dict_valid(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    iq.QuestradeIQ(TEST_VALID_CONFIG)
    assert m.call_count == 1


def test_config_dict_invalid_token(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_INVALID, status_code=400, reason="Bad Request")
    with pytest.raises(HTTPError):
        iq.QuestradeIQ(TEST_INVALID_CONFIG)
    assert m.call_count == 1


def test_config_dict_valid_token_inv_response(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json={})
    with pytest.raises(RuntimeError):
        iq.QuestradeIQ(TEST_VALID_CONFIG)
    assert m.call_count == 1


def test_get_time(m: requests_mock.Mocker) -> None:
    tz = timezone("America/New_York")
    now = datetime.now(tz)
    test_response = {"time": now.isoformat()}
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/time", json=test_response)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    now_resp = qt.get_time()
    assert now == now_resp
    assert m.call_count == 2
    history = m.request_history[1]
    assert history.method == "GET"
    assert history.qs == {}
    m.get(TEST_MOCK_API_SERVER + "v1/time", json={})
    with pytest.raises(RuntimeError):
        qt.get_time()


def get_tickers_helper(m: requests_mock.Mocker, result: list[iq.TickerDetails]) -> None:
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], iq.TickerDetails)
    assert result[0].ticker == TEST_AAPL_SYMBOL["symbols"][0]["symbol"]
    assert result[0].symbol_id == TEST_AAPL_SYMBOL["symbols"][0]["symbolId"]
    assert m.call_count == 1
    history = m.request_history[0]
    assert history.method == "GET"
    assert "names" in history.qs or "ids" in history.qs
    assert not ("names" in history.qs and "ids" in history.qs)
    if "names" in history.qs:
        assert isinstance(history.qs["names"], list)
        assert len(history.qs["names"]) == 1
        assert history.qs["names"][0] == str(TEST_AAPL_SYMBOL["symbols"][0]["symbol"]).lower()
    elif "ids" in history.qs:
        assert isinstance(history.qs["ids"], list)
        assert len(history.qs["ids"]) == 1
        assert history.qs["ids"][0] == str(TEST_AAPL_SYMBOL["symbols"][0]["symbolId"])
    assert not (result[0] < result[0])
    result[0].get_display_name()


def test_get_tickers(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/symbols?names=AAPL", json=TEST_AAPL_SYMBOL, complete_qs=True)
    m.get(TEST_MOCK_API_SERVER + "v1/symbols?ids=8049", json=TEST_AAPL_SYMBOL, complete_qs=True)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)

    symbol = "AAPL"
    symbol_id = 8049

    reset_mock(m)
    tickers = qt.get_tickers(symbol)
    get_tickers_helper(m, tickers)

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers([symbol]))

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers({symbol}))

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers(symbol_id))

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers([symbol_id]))

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers({symbol_id}))

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers(tickers[0]))

    reset_mock(m)
    get_tickers_helper(m, qt.get_tickers(tickers))

    m.get(TEST_MOCK_API_SERVER + "v1/symbols?names=AAPL", json={}, complete_qs=True)
    with pytest.raises(RuntimeError):
        qt.get_tickers("AAPL")

    with pytest.raises(TypeError):
        qt.get_tickers(3.14159)  # type: ignore

    with pytest.raises(TypeError):
        qt.get_tickers({3.14159})  # type: ignore

    with pytest.raises(TypeError):
        qt.get_tickers([3.14159])  # type: ignore


def get_quote_helper(m: requests_mock.Mocker, result: list[iq.Level1Quote], expected_count: int) -> None:
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], iq.Level1Quote)
    assert result[0].ticker == TEST_AAPL_SYMBOL["symbols"][0]["symbol"]
    assert result[0].symbol_id == TEST_AAPL_SYMBOL["symbols"][0]["symbolId"]
    assert m.call_count == expected_count
    history = m.request_history[expected_count - 1]
    assert history.method == "GET"
    assert "ids" in history.qs
    assert isinstance(history.qs["ids"], list)
    assert len(history.qs["ids"]) == 1
    assert history.qs["ids"][0] == str(TEST_AAPL_SYMBOL["symbols"][0]["symbolId"])
    result[0].get_display_name()


def test_get_quote(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/symbols?names=AAPL", json=TEST_AAPL_SYMBOL, complete_qs=True)
    m.get(TEST_MOCK_API_SERVER + "v1/markets/quotes?ids=8049", json=TEST_AAPL_QUOTE, complete_qs=True)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)

    symbol = "AAPL"
    symbol_id = 8049

    reset_mock(m)
    get_quote_helper(m, qt.get_quote(symbol_id), 1)

    reset_mock(m)
    get_quote_helper(m, qt.get_quote([symbol_id]), 1)

    reset_mock(m)
    get_quote_helper(m, qt.get_quote({symbol_id}), 1)

    reset_mock(m)
    get_quote_helper(m, qt.get_quote(symbol), 2)

    reset_mock(m)
    get_quote_helper(m, qt.get_quote([symbol]), 2)

    reset_mock(m)
    get_quote_helper(m, qt.get_quote({symbol}), 2)

    tickers = qt.get_tickers(symbol)
    reset_mock(m)
    get_quote_helper(m, qt.get_quote(tickers[0]), 1)

    reset_mock(m)
    get_quote_helper(m, qt.get_quote(tickers), 1)

    m.get(TEST_MOCK_API_SERVER + "v1/markets/quotes?ids=8049", json={}, complete_qs=True)
    with pytest.raises(RuntimeError):
        qt.get_quote(symbol_id)

    with pytest.raises(TypeError):
        qt.get_quote(3.14159)  # type: ignore

    with pytest.raises(TypeError):
        qt.get_quote({3.14159})  # type: ignore

    with pytest.raises(TypeError):
        qt.get_quote([3.14159])  # type: ignore


def test_search_for_symbols(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/symbols/search?prefix=BMO", json=TEST_SEARCH_RESPONSE, complete_qs=True)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.search_for_symbols(prefix="BMO")

    m.get(TEST_MOCK_API_SERVER + "v1/symbols/search?prefix=BMO&offset=1", json=TEST_SEARCH_RESPONSE, complete_qs=True)
    qt.search_for_symbols(prefix="BMO", offset=1)

    m.get(TEST_MOCK_API_SERVER + "v1/symbols/search?prefix=BMO", json={})
    with pytest.raises(RuntimeError):
        qt.search_for_symbols(prefix="BMO")


def test_get_accounts(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/accounts", json=TEST_ACCOUNTS_RESPONSE, complete_qs=True)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    result = qt.get_accounts()
    assert isinstance(result, list)
    assert len(result) == len(TEST_ACCOUNTS_RESPONSE["accounts"])
    assert isinstance(result[0], iq.AccountInfo)
    assert result[0].type == iq.AccountType[str(TEST_ACCOUNTS_RESPONSE["accounts"][0]["type"])]
    assert result[0].number == TEST_ACCOUNTS_RESPONSE["accounts"][0]["number"]
    assert result[0].status == TEST_ACCOUNTS_RESPONSE["accounts"][0]["status"]
    assert not (result[0] < result[0])

    m.get(TEST_MOCK_API_SERVER + "v1/accounts", json={})
    with pytest.raises(RuntimeError):
        qt.get_accounts()


def test_get_balances(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/balances", json=TEST_BALANCES_RESPONSE, complete_qs=True)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.get_balances("12345678")

    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/balances", json={})
    with pytest.raises(RuntimeError):
        qt.get_balances("12345678")


def test_get_activities(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/activities", json=TEST_ACTIVITIES_RESPONSE)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    startTime = datetime.now() - timedelta(days=1)
    endTime = datetime.now()
    result = qt.get_activities("12345678", start_time=startTime, end_time=endTime)
    assert not (result[0] < result[0])

    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/activities", json={})
    with pytest.raises(RuntimeError):
        qt.get_activities("12345678", start_time=startTime, end_time=endTime)


def test_get_positions(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/positions", json=TEST_POSITIONS_RESPONSE)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    result = qt.get_positions("12345678")
    assert not (result[0] < result[0])

    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/positions", json={})
    with pytest.raises(RuntimeError):
        qt.get_positions("12345678")


def test_get_orders_open(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(
        TEST_MOCK_API_SERVER + "v1/accounts/12345678/orders?stateFilter=Open",
        json=TEST_ORDERS_RESPONSE,
        complete_qs=True,
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    result = qt.get_orders("12345678", state_filter=iq.OrderStateFilter.Open)
    assert len(result) == len(TEST_ORDERS_RESPONSE["orders"])
    assert isinstance(result[0], iq.Order)


def test_get_orders_closed(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(
        TEST_MOCK_API_SERVER + "v1/accounts/12345678/orders?stateFilter=Closed", json={"orders": []}, complete_qs=True
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    result = qt.get_orders("12345678", state_filter=iq.OrderStateFilter.Closed)
    assert len(result) == 0

    m.get(
        TEST_MOCK_API_SERVER
        + "v1/accounts/12345678/orders"
        + "?startTime=2021-01-01T00%3A00%3A00&endTime=2021-12-31T00%3A00%3A00&stateFilter=Closed",
        json={"orders": []},
        complete_qs=True,
    )
    qt.get_orders(
        "12345678",
        state_filter=iq.OrderStateFilter.Closed,
        start_time=datetime(2021, 1, 1),
        end_time=datetime(2021, 12, 31),
    )

    with pytest.raises(TypeError):
        qt.get_orders(
            "12345678",
            state_filter=iq.OrderStateFilter.Closed,
            start_time="20210101",  # type: ignore
            end_time=datetime(2021, 12, 31),
        )

    with pytest.raises(TypeError):
        qt.get_orders(
            "12345678",
            state_filter=iq.OrderStateFilter.Closed,
            start_time=datetime(2021, 1, 1),
            end_time="20211231",  # type: ignore
        )

    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/orders?stateFilter=Closed", json={})
    with pytest.raises(RuntimeError):
        qt.get_orders("12345678", state_filter=iq.OrderStateFilter.Closed)


def test_get_orders_all(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(
        TEST_MOCK_API_SERVER + "v1/accounts/12345678/orders?stateFilter=All",
        json=TEST_ORDERS_RESPONSE,
        complete_qs=True,
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.get_orders("12345678", state_filter=iq.OrderStateFilter.All)


def test_get_order(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(
        TEST_MOCK_API_SERVER + "v1/accounts/12345678/orders/54321",
        json=TEST_ORDERS_RESPONSE,
        complete_qs=True,
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.get_order("12345678", "54321")

    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/orders/54321", json={})
    with pytest.raises(RuntimeError):
        qt.get_order("12345678", "54321")


def test_get_executions(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(
        TEST_MOCK_API_SERVER + "v1/accounts/12345678/executions",
        json=TEST_EXEUCTIONS_RESPONSE,
        complete_qs=True,
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.get_executions("12345678")

    m.get(
        TEST_MOCK_API_SERVER
        + "v1/accounts/12345678/executions"
        + "?startTime=2021-01-01T00%3A00%3A00&endTime=2021-12-31T00%3A00%3A00",
        json=TEST_EXEUCTIONS_RESPONSE,
        complete_qs=True,
    )
    qt.get_executions("12345678", start_time=datetime(2021, 1, 1), end_time=datetime(2021, 12, 31))

    with pytest.raises(TypeError):
        qt.get_executions("12345678", start_time="20210101", end_time=datetime(2021, 12, 31))  # type: ignore

    with pytest.raises(TypeError):
        qt.get_executions("12345678", start_time=datetime(2021, 1, 1), end_time="20211231")  # type: ignore

    m.get(TEST_MOCK_API_SERVER + "v1/accounts/12345678/executions", json={})
    with pytest.raises(RuntimeError):
        qt.get_executions("12345678")


def test_get_option_chain(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(
        TEST_MOCK_API_SERVER + "v1/symbols/1234/options",
        json=TEST_OPTIONS_RESPONSE,
        complete_qs=True,
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.get_option_chain(1234)

    m.get(TEST_MOCK_API_SERVER + "v1/symbols?names=AAPL", json=TEST_AAPL_SYMBOL, complete_qs=True)
    m.get(
        TEST_MOCK_API_SERVER + "v1/symbols/8049/options",
        json=TEST_OPTIONS_RESPONSE,
        complete_qs=True,
    )
    qt.get_option_chain("AAPL")
    ticker = qt.get_tickers("AAPL")
    qt.get_option_chain(ticker[0])

    m.get(TEST_MOCK_API_SERVER + "v1/symbols/1234/options", json={})
    with pytest.raises(RuntimeError):
        qt.get_option_chain(1234)  # type: ignore

    with pytest.raises(TypeError):
        qt.get_option_chain(3.14159)  # type: ignore


def test_get_option_quote(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.post(TEST_MOCK_API_SERVER + "v1/markets/quotes/options", json=TEST_OPTIONS_QUOTE_RESPONSE)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)
    qt.get_option_quotes([])
    qt.get_option_quotes(
        1234, filters=[iq.OptionIdFilter(iq.OptionType.Put, 27426, datetime(2021, 8, 20), 250.0, 200.0)]
    )
    qt.get_option_quotes(
        [1234], filters=[iq.OptionIdFilter(iq.OptionType.Put, 27426, datetime(2021, 8, 20), 250.0, 200.0)]
    )

    m.post(TEST_MOCK_API_SERVER + "v1/markets/quotes/options", json={})
    with pytest.raises(RuntimeError):
        qt.get_option_quotes(1234)

    with pytest.raises(TypeError):
        qt.get_option_quotes(3.14159)  # type: ignore

    with pytest.raises(TypeError):
        qt.get_option_quotes([3.14159])  # type: ignore


def test_get_strategy_quotes(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.post(TEST_MOCK_API_SERVER + "v1/markets/quotes/strategies", json=TEST_STRATEGY_QUOTE_RESPONSE)
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)

    variants = [
        iq.StrategyVariantRequest(
            1,
            iq.StrategyType.CoveredCall,
            [
                iq.StrategyLeg(27426, iq.OrderAction.Buy, 1000),
                iq.StrategyLeg(10550014, iq.OrderAction.Sell, 10),
            ],
        )
    ]
    qt.get_strategy_quotes(variants)

    m.post(TEST_MOCK_API_SERVER + "v1/markets/quotes/strategies", json={})
    with pytest.raises(RuntimeError):
        qt.get_strategy_quotes(variants)

    with pytest.raises(TypeError):
        qt.get_strategy_quotes(3.14159)  # type: ignore

    with pytest.raises(TypeError):
        qt.get_strategy_quotes([variants[0], 3.14159])  # type: ignore


def test_get_candles(m: requests_mock.Mocker) -> None:
    m.get(REFRESH_TOKEN_URL + TEST_REFRESH_TOKEN_VALID, json=ACCESS_TOKEN_RESPONSE)
    m.get(TEST_MOCK_API_SERVER + "v1/symbols?names=AAPL", json=TEST_AAPL_SYMBOL, complete_qs=True)
    m.get(
        TEST_MOCK_API_SERVER
        + "v1/markets/candles/8049"
        + "?startTime=2021-01-01T00%3A00%3A00&endTime=2021-12-31T00%3A00%3A00&interval=OneDay",
        json=TEST_CANDLES_RESPONSE,
        complete_qs=True,
    )
    qt = iq.QuestradeIQ(TEST_VALID_CONFIG)

    ticker = qt.get_tickers("AAPL")
    qt.get_candles(8049, iq.Granularity.OneDay, start_time=datetime(2021, 1, 1), end_time=datetime(2021, 12, 31))
    qt.get_candles("AAPL", iq.Granularity.OneDay, start_time=datetime(2021, 1, 1), end_time=datetime(2021, 12, 31))
    qt.get_candles(ticker[0], iq.Granularity.OneDay, start_time=datetime(2021, 1, 1), end_time=datetime(2021, 12, 31))

    with pytest.raises(TypeError):
        qt.get_candles(
            3.14159,  # type: ignore
            iq.Granularity.OneDay,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
        )
