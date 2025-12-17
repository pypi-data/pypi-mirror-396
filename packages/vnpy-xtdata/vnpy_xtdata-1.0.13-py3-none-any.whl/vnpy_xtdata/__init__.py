# @Time    : 2025/4/28 19:24
# @Author  : YQ Tsui
# @File    : __init__.py
# @Purpose :
import importlib_metadata
from .xt_datapub import XtMdApi, generate_datetime, symbol_contract_map, EVENT_CONTRACT_READY
from .xt_datafeed import XtDatafeed as Datafeed


try:
    __version__ = importlib_metadata.version("vnpy_xt")
except importlib_metadata.PackageNotFoundError:
    __version__ = "dev"


__all__ = [
    "XtMdApi",
    "Datafeed",
    "generate_datetime",
    "symbol_contract_map",
    "__version__",
    "EVENT_CONTRACT_READY",
]
