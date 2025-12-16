#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import sys
import os
# 获取当前脚本的绝对路径
current_path = os.path.abspath(__file__)
root_path = os.path.abspath(os.path.join(current_path, "../../../"))
# 将根目录添加到 sys.path
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from trade_mdforopenctp import PeopleQuantApi 
import time as tm
import zhuchannel
import os
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
    },
    "电信1": {
        "td": "tcp://182.254.243.31:30001",
        "md": "tcp://182.254.243.31:30011",
    },
    "电信2": {
        "td": "tcp://182.254.243.31:30002",
        "md": "tcp://182.254.243.31:30012",
    },
    "移动": {
        "td": "tcp://182.254.243.31:30003",
        "md": "tcp://182.254.243.31:30013",
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

#创建api实例
pqapi = PeopleQuantApi(BrokerID=BROKERID, UserID=USERID, PassWord=PASSWORD, AppID=APPID, AuthCode=AUTHCODE, TradeFrontAddr=TradeFrontAddr, MdFrontAddr=MdFrontAddr, s=USERID,flowfile="",
                       storage_format="parquet")
account = pqapi.get_account()            #获取账户资金
posions = pqapi.get_position()
symbol = "rb2605"
quote1 = pqapi.get_quote(symbol)        #获取合约行情
symbol_info = pqapi.get_symbol_info(symbol) #获取合约属性
print("合约乘数",symbol_info.VolumeMultiple,"价格最小变动",symbol_info.PriceTick)
position1 = pqapi.get_position(symbol)   #获取合约持仓，建议先取行情后取持仓

local_timestamp = quote1.local_timestamp

kline = pqapi.get_kline(symbol, "10m", 5)   #获取K线
tick = pqapi.get_tick(symbol)                #获取Tick
kline2 = pqapi.get_kline(symbol, "10m", 10)   #获取K线

while True:
    #break
    if local_timestamp != quote1.local_timestamp: #新行情推送
        local_timestamp = quote1.local_timestamp
        print((quote1.ctp_datetime,'合约代码',quote1.InstrumentID,'最新价',quote1.LastPrice,"卖一价",quote1.AskPrice1,"买一价",quote1.BidPrice1,"成交量",quote1.Volume,quote1.ctp_datetime))
        #print(position1)
        #print(quote2["InstrumentID"],quote2["LastPrice"],quote2["UpdateTime"],)
        #print(position2 )
        #print(account)
        #print(quote3)
        #print(margin2)
        #print(kline.data)
        #print(kline.data.select(["InstrumentID", "period_start",   "open", "high","low", "close", "Volume","OpenInterest","period" ]))
        print(tick.data.select(["InstrumentID","TradingDay","LastPrice","BidPrice1","AskPrice1","BidVolume1","AskVolume1","ctp_datetime"]).tail(5))
        #print(kline2.data.select(["InstrumentID", "period_start",   "open", "high","low", "close", "Volume","OpenInterest","period" ]))
        #print(tick2.data.select(["InstrumentID","TradingDay","LastPrice","BidPrice1","AskPrice1","BidVolume1","AskVolume1","ctp_datetime"]).tail(5))
    #tm.sleep(5)