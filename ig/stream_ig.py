#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
IG Markets Stream API sample with Python
2015 FemtoTrader
"""

import time
import sys
import traceback
import logging

from trading_ig import (IGService, IGStreamService)
from trading_ig.lightstreamer import Subscription
import settings


# A simple function acting as a Subscription listener
def on_prices_update(item_update):
    # print("price: %s " % item_update)
    print("{stock_name:<19}: Time {UPDATE_TIME:<8} - "
          "Bid {BID:>5} - Ask {OFFER:>5}".format(stock_name=item_update["name"], **item_update["values"]))

def on_account_update(balance_update):
    print("balance: %s " % balance_update)

def main():
    logging.basicConfig(level=logging.INFO)

    ig_service = IGService(
        username=settings.username,
        password=settings.password,
        api_key=settings.api_key,
        acc_type=settings.acc_type
    )

    ig_service.create_session()
    print(ig_service.search_markets("BHP"))
    ig_stream_service = IGStreamService(ig_service)
    ig_session = ig_stream_service.create_session()
    # Ensure settingsured account is selected
    accounts = ig_session[u'accounts']
    print(accounts)
    accountId = accounts[0]['accountId']
    ig_stream_service.connect(accountId)

    # Making a new Subscription in MERGE mode
    subscription_prices = Subscription(
        mode="MERGE",
        items=['L1:CS.D.GBPUSD.CFD.IP', 'L1:CS.D.USDJPY.CFD.IP'],
        fields=["UPDATE_TIME", "BID", "OFFER", "CHANGE", "MARKET_STATE"],
        )
        #adapter="QUOTE_ADAPTER")


    # Adding the "on_price_update" function to Subscription
    subscription_prices.addlistener(on_prices_update)

    # Registering the Subscription
    sub_key_prices = ig_stream_service.ls_client.subscribe(subscription_prices)


    # Making an other Subscription in MERGE mode
    subscription_account = Subscription(
        mode="MERGE",
        items='ACCOUNT:'+accountId,
        fields=["AVAILABLE_CASH"],
        )
    #    #adapter="QUOTE_ADAPTER")

    # Adding the "on_balance_update" function to Subscription
    subscription_account.addlistener(on_account_update)

    # Registering the Subscription
    sub_key_account = ig_stream_service.ls_client.subscribe(subscription_account)

    input("{0:-^80}\n".format("HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM \
    LIGHTSTREAMER"))

    # Disconnecting
    ig_stream_service.disconnect()

if __name__ == '__main__':
    main()
