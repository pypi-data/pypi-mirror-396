#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import sys
import os
# 获取当前脚本的绝对路径
current_path = os.path.abspath(__file__)
root_path = os.path.abspath(os.path.join(current_path, "../../../"))
# 将根目录添加到 sys.path
if root_path not in sys.path:
    sys.path.insert(0,root_path)
from peoplequant.trade_mdforopenctp import PeopleQuantApi
import time as tm
from peoplequant import zhuchannel
import asyncio
import traceback
import types
import polars
from datetime import datetime,time,date,timedelta
import copy
from typing import Dict, List, Optional, Tuple, Any

envs = {
    "7x24": {
        "td": "tcp://182.254.243.31:40001",
        "md": "tcp://182.254.243.31:40011",
        "user_id": "",
        "password": "",
        "broker_id": "9999",
        "authcode": "0000000000000000",
        "appid": "simnow_client_test",
        "user_product_info": "",
    },
    "电信1": {
        "td": "tcp://182.254.243.31:30001",
        "md": "tcp://182.254.243.31:30011",
        "user_id": "",
        "password": "",
        "broker_id": "9999",
        "authcode": "0000000000000000",
        "appid": "simnow_client_test",
        "user_product_info": "",
    },
    "电信2": {
        "td": "tcp://182.254.243.31:30002",
        "md": "tcp://182.254.243.31:30012",
        "user_id": "",
        "password": "",
        "broker_id": "9999",
        "authcode": "0000000000000000",
        "appid": "simnow_client_test",
        "user_product_info": "",
    },
    "移动": {
        "td": "tcp://182.254.243.31:30003",
        "md": "tcp://182.254.243.31:30013",
        "user_id": "",
        "password": "",
        "broker_id": "9999",
        "authcode": "0000000000000000",
        "appid": "simnow_client_test",
        "user_product_info": "",
    },
}
TradeFrontAddr="tcp://180.168.146.187:10101"   #交易前置地址
MdFrontAddr="tcp://101.230.209.178:53313"      #行情前置地址
TradeFrontAddr = envs["电信1"]["td"]
MdFrontAddr = envs["电信1"]["md"]
#TradeFrontAddr = envs["7x24"]["td"]
#MdFrontAddr = envs["7x24"]["md"]

#TradeFrontAddr = "tcp://121.37.80.177:20002" #openctp
#MdFrontAddr = "tcp://121.37.80.177:20004" #openctp

BROKERID="9999"   #期货公司ID
USERID=""   #账户
PASSWORD=""   #登录密码
APPID="simnow_client_test"   #客户端ID
AUTHCODE="0000000000000000"  #授权码

#策略函数
def cta_spread(first_symbol, second_symbol,spread_space=30 ):
    '''
    first_symbol 第一腿
    second_symbol 第二腿
    spread_space 价差区间
    '''
    quote_first = pqapi.get_quote(first_symbol)        #获取合约行情
    position_first = pqapi.get_position(first_symbol)   #获取合约持仓
    symbol_info_first = pqapi.get_symbol_info(first_symbol) #合约属性
    quote_second = pqapi.get_quote(second_symbol)        #获取合约行情
    position_second = pqapi.get_position(second_symbol)   #获取合约持仓
    symbol_info_second = pqapi.get_symbol_info(second_symbol) #合约属性
    first_UpdateTime = quote_first.ctp_datetime #行情更新时间
    second_UpdateTime = quote_second.ctp_datetime #行情更新时间
    lot = 1 #下单手数
    while True:
        if first_UpdateTime != quote_first.ctp_datetime or second_UpdateTime != quote_second.ctp_datetime: #新行情推送
            first_UpdateTime = quote_first.ctp_datetime
            second_UpdateTime = quote_second.ctp_datetime
            spread_ask = quote_first.AskPrice1 - quote_second.BidPrice1
            spread_bid = quote_first.BidPrice1 - quote_second.AskPrice1
            spread = spread_space*symbol_info_first.PriceTick #价差区间
            buy_up = spread_ask <= spread #价差底部做多
            sell_down = spread_bid >= spread #价差顶部做空
            if buy_up :
                if not position_first.pos_long + position_second.pos_short : #无多单
                    task1 = zhuchannel.WorkThread(pqapi.open_close,args=(first_symbol,'kaiduo',lot,quote_first.AskPrice1 ),kwargs={})
                    task2 = zhuchannel.WorkThread(pqapi.open_close,args=(second_symbol,'kaikong',lot,quote_second.BidPrice1 ),kwargs={})
                    task1.start()
                    task2.start()
                    task1.join()
                    task2.join()
                    r1 = task1.result
                    r2 = task2.result
                if position_first.pos_short + position_second.pos_long : #空单止盈
                    task1 = zhuchannel.WorkThread(pqapi.open_close,args=(first_symbol,'pingkong',position_first.pos_short,quote_first.AskPrice1 ),kwargs={})
                    task2 = zhuchannel.WorkThread(pqapi.open_close,args=(second_symbol,'pingduo',position_second.pos_long,quote_second.BidPrice1 ),kwargs={})
                    task1.start()
                    task2.start()
                    task1.join()
                    task2.join()
                    r1 = task1.result
                    r2 = task2.result
                
            elif sell_down :
                if not position_first.pos_short + position_second.pos_long : #无空单
                    task1 = zhuchannel.WorkThread(pqapi.open_close,args=(first_symbol,'kaikong',lot,quote_first.AskPrice1 ),kwargs={})
                    task2 = zhuchannel.WorkThread(pqapi.open_close,args=(second_symbol,'kaiduo',lot,quote_second.BidPrice1 ),kwargs={})
                    task1.start()
                    task2.start()
                    task1.join()
                    task2.join()
                    r1 = task1.result
                    r2 = task2.result
                if position_first.pos_long + position_second.pos_short : #多单止盈
                    task1 = zhuchannel.WorkThread(pqapi.open_close,args=(first_symbol,'pingduo',position_first.pos_long,quote_first.AskPrice1 ),kwargs={})
                    task2 = zhuchannel.WorkThread(pqapi.open_close,args=(second_symbol,'pingkong',position_second.pos_short,quote_second.BidPrice1 ),kwargs={})
                    task1.start()
                    task2.start()
                    task1.join()
                    task2.join()
                    r1 = task1.result
                    r2 = task2.result
            #瘸腿平仓
            if (not position_first.pos_long or not position_second.pos_short) and position_first.pos_long + position_second.pos_short: #多头瘸腿
                r1 = pqapi.open_close(first_symbol,"pingduo",position_first.pos_long)
                r2 = pqapi.open_close(first_symbol,"pingkong",position_second.pos_short)
            if (not position_first.pos_short or not position_second.pos_long) and position_first.pos_short + position_second.pos_long: #空头瘸腿
                r1 = pqapi.open_close(first_symbol,"pingkong",position_first.pos_short)
                r2 = pqapi.open_close(first_symbol,"pingduo",position_second.pos_long)

                
  
#创建api实例
pqapi = PeopleQuantApi()
account = pqapi.get_account()            #获取账户资金
#创建策略线程
cta1 = zhuchannel.WorkThread(cta_spread,args=('fu2601','hc2601',30 ),kwargs={})
cta2 = zhuchannel.WorkThread(cta_spread,args=('m2601','y2601',30 ),kwargs={})
cta1.start()
cta2.start()
cta1.join
cta2.join