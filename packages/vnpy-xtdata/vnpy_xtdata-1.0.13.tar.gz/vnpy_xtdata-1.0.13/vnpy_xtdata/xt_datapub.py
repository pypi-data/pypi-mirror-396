# @Time    : 2025/4/28 19:13
# @Author  : YQ Tsui
# @File    : xt_datapub.py
# @Purpose :
import os
import time
import json
import numpy as np
from datetime import datetime
from collections.abc import Callable
from loguru import logger
from xtquant import xtdata, xtdatacenter as xtdc
from filelock import FileLock, Timeout

from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    SubscribeRequest,
    ContractData,
    TickData,
    OptionType,
)

from vnpy.trader.constant import Exchange, Product
from vnpy.trader.utility import ZoneInfo, get_file_path, round_to
from vnpy.event import Event

# Configure loguru to write to a file for persistent logs.
# We add the handler only once to avoid duplicate handlers on multiple imports.
try:
    LOG_FILE = get_file_path("xt_datapub.log")
except Exception:
    LOG_FILE = os.path.join(os.getcwd(), "xt_datapub.log")

if not getattr(logger, "_xt_datapub_file_added", False):
    handler_id = logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="14 days",
        encoding="utf-8",
        level="INFO",
        backtrace=True,
        diagnose=False,
        enqueue=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | {message}",
    )
    # mark as added and keep handler id for potential later removal
    logger._xt_datapub_file_added = True
    logger._xt_datapub_file_handler = handler_id


EXCHANGE_VT2XT: dict[Exchange, str] = {
    Exchange.SSE: "SH",
    Exchange.SZSE: "SZ",
    Exchange.BSE: "BJ",
    Exchange.SHFE: "SF",
    Exchange.CFFEX: "IF",
    Exchange.INE: "INE",
    Exchange.DCE: "DF",
    Exchange.CZCE: "ZF",
    Exchange.GFEX: "GF",
}

EXCHANGE_XT2VT: dict[str, Exchange] = {v: k for k, v in EXCHANGE_VT2XT.items()}
EXCHANGE_XT2VT.update(
    {
        "CFFEX": Exchange.CFFEX,
        "SHFE": Exchange.SHFE,
        "CZCE": Exchange.CZCE,
        "DCE": Exchange.DCE,
        "GFEX": Exchange.GFEX,
        "SHO": Exchange.SSE,
        "SZO": Exchange.SZSE,
    }
)

# 其他常量
CHINA_TZ = ZoneInfo("Asia/Shanghai")  # 中国时区


# 全局缓存字典
symbol_contract_map: dict[(str, Exchange), ContractData] = {}  # 合约数据
symbol_limit_map: dict[str, tuple[float, float]] = {}  # 涨跌停价

EVENT_CONTRACT_READY = "xt_contract_ready"  # 合约准备就绪事件


class XtMdApi:
    """行情API"""

    lock_filename = "xt_lock"
    lock_filepath = get_file_path(lock_filename)

    def __init__(self, gateway: BaseGateway) -> None:
        """构造函数"""
        self.gateway: BaseGateway = gateway

        self.inited: bool = False
        self.subscribed: set = set()

        self.ip: str = ""
        self.port: int = 0
        self.token: str = ""
        self.stock_active: bool = False
        self.futures_active: bool = False
        self.option_active: bool = False
        self.fut_option_active: bool = False
        self.contract_queried: bool = False

        self.available_exchange: list[Exchange] = []

        self.xtdc_client = None

        self.accu_volumes: dict[str, int] = {}

        self.on_connected = None

    def onMarketData(self, data: dict) -> None:
        """行情推送回调"""

        def parse_data_dict(xt_symbol, d: dict) -> TickData:
            logger.info(f"Received market data for {xt_symbol}: {d}")
            symbol, xt_exchange = xt_symbol.split(".")
            exchange = EXCHANGE_XT2VT[xt_exchange]

            tick: TickData = TickData(
                symbol=symbol,
                exchange=exchange,
                datetime=generate_datetime(d["time"]),
                volume=d["volume"],
                turnover=d["amount"],
                open_interest=d["openInt"],
                gateway_name=self.gateway.gateway_name,
                localtime=datetime.now(CHINA_TZ),
            )

            contract = symbol_contract_map[(tick.symbol, tick.exchange)]
            tick.name = contract.name

            bp_data: list = d["bidPrice"]
            ap_data: list = d["askPrice"]
            bv_data: list = d["bidVol"]
            av_data: list = d["askVol"]

            tick.bid_price_1 = round_to(bp_data[0], contract.pricetick)
            tick.bid_price_2 = round_to(bp_data[1], contract.pricetick)
            tick.bid_price_3 = round_to(bp_data[2], contract.pricetick)
            tick.bid_price_4 = round_to(bp_data[3], contract.pricetick)
            tick.bid_price_5 = round_to(bp_data[4], contract.pricetick)

            tick.ask_price_1 = round_to(ap_data[0], contract.pricetick)
            tick.ask_price_2 = round_to(ap_data[1], contract.pricetick)
            tick.ask_price_3 = round_to(ap_data[2], contract.pricetick)
            tick.ask_price_4 = round_to(ap_data[3], contract.pricetick)
            tick.ask_price_5 = round_to(ap_data[4], contract.pricetick)

            tick.bid_volume_1 = bv_data[0]
            tick.bid_volume_2 = bv_data[1]
            tick.bid_volume_3 = bv_data[2]
            tick.bid_volume_4 = bv_data[3]
            tick.bid_volume_5 = bv_data[4]

            tick.ask_volume_1 = av_data[0]
            tick.ask_volume_2 = av_data[1]
            tick.ask_volume_3 = av_data[2]
            tick.ask_volume_4 = av_data[3]
            tick.ask_volume_5 = av_data[4]

            tick.last_price = round_to(d["lastPrice"], contract.pricetick)
            tick.open_price = round_to(d["open"], contract.pricetick)
            tick.high_price = round_to(d["high"], contract.pricetick)
            tick.low_price = round_to(d["low"], contract.pricetick)
            tick.pre_close = round_to(d["lastClose"], contract.pricetick)

            if tick.vt_symbol in symbol_limit_map:
                tick.limit_up, tick.limit_down = symbol_limit_map[tick.vt_symbol]

            # 判断收盘状态
            tick.extra = {
                "market_closed": False,
            }

            if contract.product == Product.ETF:
                tick.extra["iopv"] = d.get("pe", np.nan)

            # 非衍生品可以通过openInt字段判断证券状态
            if contract.product not in {Product.FUTURES, Product.OPTION}:
                if "openInt" in d and d["openInt"] in {1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23}:
                    tick.extra["status"] = d["openInt"]
                tick.extra["market_closed"] = d["openInt"] == 15
            # 衍生品该字段为持仓量，需要通过结算价判断
            elif d["settlementPrice"] > 0:
                tick.extra["market_closed"] = True
            return tick

        for xt_symbol, buf in data.items():
            if isinstance(buf, dict):
                tick = parse_data_dict(xt_symbol, buf)
                tick.last_volume = max(0, tick.volume - self.accu_volumes.get(tick.vt_symbol, 0))
                self.gateway.on_tick(tick)
                self.accu_volumes[tick.vt_symbol] = tick.volume
            elif isinstance(buf, list):
                for d in buf:
                    tick = parse_data_dict(xt_symbol, d)
                    tick.last_volume = max(0, tick.volume - self.accu_volumes.get(tick.vt_symbol, 0))
                    self.gateway.on_tick(tick)
                    self.accu_volumes[tick.vt_symbol] = tick.volume

    def connect(
        self,
        ip: str,
        port: int,
        token: str,
        stock_active: bool,
        futures_active: bool,
        option_active: bool,
        fut_option_active: bool,
        server_pool: list[str] = None,
    ) -> None:
        """连接"""
        self.ip = ip
        self.port = port
        self.token = token
        self.stock_active = stock_active
        self.futures_active = futures_active
        self.option_active = option_active
        self.fut_option_active = fut_option_active

        if self.inited:
            self.gateway.write_log("行情接口已经初始化，请勿重复操作")
            return
        self.gateway.write_log("开始启动行情服务，请稍等")

        if not 5000 <= self.port <= 65535:
            self.port = 58609
        xtdata.watch_xtquant_status(self.on_connection_status)
        if not self._connect_to_existing_xtdc(self.ip, self.port):
            if self.ip in {"127.0.0.1", "localhost"}:
                _, self.port = self.init_xtdc(server_pool)
                self.xtdc_client = xtdata.connect(port=self.port)
                if self.xtdc_client.is_connected():
                    self.gateway.write_log("迅投研数据服务初始化成功")
                else:
                    self.gateway.write_log("迅投研数据服务初始化失败，请检查日志")
            else:
                self.gateway.write_log(f"远程迅投研数据服务{self.ip}:{self.port}连接失败")

    def _connect_to_existing_xtdc(self, ip: str, port: int) -> bool:
        """连接到已经存在的行情服务"""
        try:
            self.xtdc_client = xtdata.connect(ip, port)
            if self.xtdc_client.is_connected():
                self.gateway.write_log("连接到已经存在的行情服务")
                self.inited = True
                self.query_contracts()
                return True
            return False
        except Exception:
            self.xtdc_client = None
            return False

    def get_lock(self) -> bool:
        """获取文件锁，确保单例运行"""
        self.lock = FileLock(self.lock_filepath)

        try:
            self.lock.acquire(timeout=1)
            return True
        except Timeout:
            return False

    def init_xtdc(self, server_pool: list[str] = None) -> tuple[str, int]:
        """初始化xtdc服务进程"""
        if not self.get_lock():
            return 0

        # 设置token
        xtdc.set_token(self.token)

        # 设置是否只连接VIP服务器
        if isinstance(server_pool, list) and len(server_pool) > 0:
            xtdc.set_allow_optmize_address(server_pool)

        # 开启使用期货真实夜盘时间
        xtdc.set_future_realtime_mode(True)

        # 执行初始化，但不启动默认58609端口监听
        xtdc.init(False)

        # 设置监听端口58620
        return xtdc.listen(port=(self.port, self.port + 50))

    def on_connection_status(self, info_dict: dict) -> None:
        """连接状态回调"""
        if self.inited:
            if info_dict["status"] != "connected":
                error_info = json.loads(info_dict.get("error", "{}"))
                if bool(error_info):
                    self.gateway.write_log(f"[{error_info['error id']}]{error_info['error']}")
                self.inited = False
                self.gateway.write_log(f"行情服务（{info_dict['address']}）连接断开")
        elif info_dict["status"] == "connected":
            time.sleep(1)
            for _attempt in range(5):
                if self.xtdc_client:
                    if self.xtdc_client.is_connected():
                        self.gateway.write_log(f"行情服务（{info_dict['address']}）连接成功")
                        self.inited = True
                        self.query_contracts()
                        if self.on_connected:
                            self.on_connected()
                        break
                else:
                    self.gateway.write_log(f"等待客户端完全连接：尝试{_attempt + 1}/5")
                    time.sleep(1)
            else:
                self.gateway.write_log(f"行情服务（{info_dict['address']}）连接失败，请检查日志")

    def query_contracts(self) -> None:
        """查询合约信息"""
        if self.contract_queried:
            return
        self.gateway.write_log("开始查询合约")
        self.contract_queried = True
        if self.stock_active:
            self.query_stock_contracts()

        if self.futures_active:
            self.query_future_contracts()

        if self.option_active:
            self.query_option_contracts()

        self.gateway.write_log("合约信息查询成功")

        self.gateway.event_engine.put(Event(EVENT_CONTRACT_READY, data=None))

    def query_stock_contracts(self) -> None:
        """查询股票合约信息"""
        xt_symbols: list[str] = []
        markets: list = ["沪深A股", "沪深转债", "沪深ETF", "沪深指数", "京市A股"]
        new_exchanges = [Exchange.SSE, Exchange.SZSE, Exchange.BSE]
        new_exchanges = [exchange for exchange in new_exchanges if exchange not in self.available_exchange]
        self.available_exchange.extend(new_exchanges)

        for i in markets:
            names: list = xtdata.get_stock_list_in_sector(i)
            xt_symbols.extend(names)

        for xt_symbol in xt_symbols:
            # 筛选需要的合约
            product = None
            symbol, xt_exchange = xt_symbol.split(".")

            if xt_exchange == "SZ":
                if xt_symbol.startswith(("00", "30")):
                    product = Product.EQUITY
                elif xt_symbol.startswith("15"):
                    product = Product.ETF
                else:
                    product = Product.INDEX
            elif xt_exchange == "SH":
                if xt_symbol.startswith(("60", "68")):
                    product = Product.EQUITY
                elif xt_symbol.startswith("51"):
                    product = Product.ETF
                else:
                    product = Product.INDEX
            elif xt_exchange == "BJ":
                product = Product.EQUITY

            if not product:
                continue

            # 生成并推送合约信息
            data: dict = xtdata.get_instrument_detail(xt_symbol)
            pricetick = data["PriceTick"]
            vol_step = 100
            if product == Product.ETF:
                pricetick = 0.001
            if product == Product.INDEX:
                vol_step = 1

            if data is None:
                self.gateway.write_log(f"合约{xt_symbol}信息查询失败")
                continue
            exch = EXCHANGE_XT2VT[xt_exchange]

            if abs(data["PriceTick"] - pricetick) > 1e-5:
                print("symbol:", xt_symbol, "pricetick:", data["PriceTick"], "reset to:", pricetick)

            contract: ContractData = ContractData(
                symbol=symbol,
                exchange=exch,
                name=data["InstrumentName"],
                product=product,
                size=data["VolumeMultiple"],
                pricetick=pricetick,
                min_volume=vol_step,
                volume_step=vol_step,
                history_data=False,
                net_position=True,
                gateway_name=self.gateway.gateway_name,
            )

            symbol_contract_map[(symbol, exch)] = contract
            symbol_limit_map[contract.vt_symbol] = (
                data["UpStopPrice"],
                data["DownStopPrice"],
            )

            self.gateway.on_contract(contract)

    def query_future_contracts(self) -> None:
        """查询期货合约信息"""
        xt_symbols: list[str] = []
        markets: list = [
            "中金所期货",
            "上期所期货",
            "能源中心期货",
            "大商所期货",
            "郑商所期货",
            "广期所期货",
        ]
        new_exchanges = [
            Exchange.SHFE,
            Exchange.CFFEX,
            Exchange.INE,
            Exchange.DCE,
            Exchange.CZCE,
            Exchange.GFEX,
        ]
        new_exchanges = [exchange for exchange in new_exchanges if exchange not in self.available_exchange]
        self.available_exchange.extend(new_exchanges)

        for i in markets:
            names: list = xtdata.get_stock_list_in_sector(i)
            xt_symbols.extend(names)

        for xt_symbol in xt_symbols:
            # 筛选需要的合约
            product = None
            symbol, xt_exchange = xt_symbol.split(".")

            if xt_exchange == "ZF" and len(symbol) > 6 and "&" not in symbol:
                product = Product.OPTION
            elif xt_exchange in ("IF", "GF") and "-" in symbol:
                product = Product.OPTION
            elif xt_exchange in ("DF", "INE", "SF") and ("C" in symbol or "P" in symbol) and "SP" not in symbol:
                product = Product.OPTION
            else:
                product = Product.FUTURES

            # 生成并推送合约信息
            if product == Product.OPTION:
                data: dict = xtdata.get_instrument_detail(xt_symbol, True)
            else:
                data: dict = xtdata.get_instrument_detail(xt_symbol)

            if not data["ExpireDate"]:
                if "00" not in symbol:
                    continue

            exch = EXCHANGE_XT2VT[xt_exchange]
            contract: ContractData = ContractData(
                symbol=symbol,
                exchange=exch,
                name=data["InstrumentName"],
                product=product,
                size=data["VolumeMultiple"],
                pricetick=data["PriceTick"],
                history_data=False,
                gateway_name=self.gateway.gateway_name,
            )

            symbol_contract_map[(symbol, exch)] = contract
            symbol_limit_map[contract.vt_symbol] = (
                data["UpStopPrice"],
                data["DownStopPrice"],
            )

            self.gateway.on_contract(contract)

    def query_option_contracts(self) -> None:
        """查询期权合约信息"""
        xt_symbols: list[str] = []

        markets: list[str] = []
        new_exchanges: list[Exchange] = []
        if self.option_active:
            markets.extend(
                [
                    "上证期权",
                    "深证期权",
                ]
            )
            new_exchanges.extend([Exchange.SSE, Exchange.SZSE])
        if self.fut_option_active:
            markets.extend(
                [
                    "中金所期权",
                    "上期所期权",
                    "能源中心期权",
                    "大商所期权",
                    "郑商所期权",
                    "广期所期权",
                ]
            )
            new_exchanges.extend(
                [
                    Exchange.CFFEX,
                    Exchange.SHFE,
                    Exchange.INE,
                    Exchange.DCE,
                    Exchange.CZCE,
                    Exchange.GFEX,
                ]
            )

        new_exchanges = [exchange for exchange in new_exchanges if exchange not in self.available_exchange]
        self.available_exchange.extend(new_exchanges)

        for i in markets:
            names: list = xtdata.get_stock_list_in_sector(i)
            xt_symbols.extend(names)

        for xt_symbol in xt_symbols:
            """"""
            _, xt_exchange = xt_symbol.split(".")

            if xt_exchange in {"SHO", "SZO"}:
                contract = process_etf_option(xtdata.get_instrument_detail, xt_symbol, self.gateway.gateway_name)
            else:
                contract = process_futures_option(xtdata.get_instrument_detail, xt_symbol, self.gateway.gateway_name)

            if contract:
                # for CZCE options, xt will return two contracts for one option, one with one digit for year, which is the current official contract, and one with two digits for year, which is for long history convience, we just ignore the latter
                if (contract.symbol, contract.exchange) in symbol_contract_map:
                    continue
                symbol_contract_map[(contract.symbol, contract.exchange)] = contract

                self.gateway.on_contract(contract)

    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        if (req.symbol, req.exchange) not in symbol_contract_map:
            return

        xt_exchange: str = EXCHANGE_VT2XT[req.exchange]
        if xt_exchange in {"SH", "SZ"} and len(req.symbol) > 6:
            xt_exchange += "O"

        xt_symbol: str = req.symbol + "." + xt_exchange

        if xt_symbol not in self.subscribed:
            # xtdata.subscribe_quote(stock_code=xt_symbol, period="tick", callback=self.onMarketData)
            xtdata.subscribe_whole_quote([xt_symbol], callback=self.onMarketData)
            self.subscribed.add(xt_symbol)

    def close(self) -> None:
        """关闭"""
        if self.inited:
            xtdata.disconnect()
            self.inited = False

        if hasattr(self, "lock"):
            self.lock.release(force=True)

        if hasattr(self, "lock_filepath"):
            try:
                os.remove(self.lock_filepath)
            except Exception:
                pass


def generate_datetime(timestamp: int, millisecond: bool = True) -> datetime:
    """生成本地时间"""
    if millisecond:
        dt: datetime = datetime.fromtimestamp(timestamp / 1000)
    else:
        dt: datetime = datetime.fromtimestamp(timestamp)
    dt: datetime = dt.replace(tzinfo=CHINA_TZ)
    return dt


def process_etf_option(get_instrument_detail: Callable, xt_symbol: str, gateway_name: str) -> ContractData | None:
    """处理ETF期权"""
    # 拆分XT代码
    symbol, xt_exchange = xt_symbol.split(".")

    # 筛选期权合约合约（ETF期权代码为8位）
    if len(symbol) != 8:
        return None

    # 查询转换数据
    data: dict = get_instrument_detail(xt_symbol, True)

    name: str = data["InstrumentName"]
    if "购" in name:
        option_type = OptionType.CALL
    elif "沽" in name:
        option_type = OptionType.PUT
    else:
        return None

    if "A" in name:
        option_index = str(data["OptExercisePrice"]) + "-A"
    else:
        option_index = str(data["OptExercisePrice"]) + "-M"

    contract: ContractData = ContractData(
        symbol=data["InstrumentID"],
        exchange=EXCHANGE_XT2VT[xt_exchange],
        name=data["InstrumentName"],
        product=Product.OPTION,
        size=data["VolumeMultiple"],
        pricetick=data["PriceTick"],
        min_volume=data["MinLimitOrderVolume"],
        option_strike=data["OptExercisePrice"],
        option_listed=datetime.strptime(data["OpenDate"], "%Y%m%d"),
        expiry=datetime.strptime(data["ExpireDate"], "%Y%m%d"),
        option_portfolio=data["OptUndlCode"] + "_O",
        option_index=option_index,
        option_type=option_type,
        option_underlying=data["OptUndlCode"] + "-" + str(data["ExpireDate"])[:6],
        gateway_name=gateway_name,
    )

    symbol_limit_map[contract.vt_symbol] = (data["UpStopPrice"], data["DownStopPrice"])

    return contract


def process_futures_option(get_instrument_detail: Callable, xt_symbol: str, gateway_name: str) -> ContractData | None:
    """处理期货期权"""
    # 筛选期权合约
    data: dict = get_instrument_detail(xt_symbol, True)

    option_strike: float = data["OptExercisePrice"]
    if not option_strike:
        return None

    # 拆分XT代码
    symbol, xt_exchange = xt_symbol.split(".")

    # 移除产品前缀
    ix = 0
    for ix, w in enumerate(symbol):  # noqa
        if w.isdigit():
            break

    suffix: str = symbol[ix:]

    # 过滤非期权合约
    if "(" in symbol or " " in symbol:
        return None

    # 判断期权类型
    if "C" in suffix:
        option_type = OptionType.CALL
    elif "P" in suffix:
        option_type = OptionType.PUT
    else:
        return None

    # 获取期权标的
    if "-" in symbol:
        option_underlying: str = symbol.split("-")[0]
    else:
        option_underlying: str = data["OptUndlCode"]

    # 转换数据
    contract: ContractData = ContractData(
        symbol=data["InstrumentID"],
        exchange=EXCHANGE_XT2VT[xt_exchange],
        name=data["InstrumentName"],
        product=Product.OPTION,
        size=data["VolumeMultiple"],
        pricetick=data["PriceTick"],
        min_volume=data["MinLimitOrderVolume"],
        option_strike=data["OptExercisePrice"],
        option_listed=datetime.strptime(data["OpenDate"], "%Y%m%d"),
        expiry=datetime.strptime(data["ExpireDate"], "%Y%m%d"),
        option_index=str(data["OptExercisePrice"]),
        option_type=option_type,
        option_underlying=option_underlying,
        gateway_name=gateway_name,
    )

    if contract.exchange == Exchange.CZCE:
        contract.option_portfolio = data["ProductID"][:-1]
    else:
        contract.option_portfolio = data["ProductID"]

    symbol_limit_map[contract.vt_symbol] = (data["UpStopPrice"], data["DownStopPrice"])

    return contract
