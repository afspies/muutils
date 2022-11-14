"""for storing/retrieving an item externally in a ZANJ archive"""

import json
import typing
from typing import Literal, NamedTuple, Sequence, IO, Callable, Any, Iterable

import numpy as np
import pandas as pd

from muutils.json_serialize.util import JSONitem 
from muutils.tensor_utils import NDArray

ZANJ_MAIN: str = "__zanj__.json"
ZANJ_META: str = "__zanj_meta__.json"

ExternalItemType = Literal["ndarray", "jsonl"]

ExternalItem = NamedTuple(
	"ExternalItem",
	[
		("item_type", ExternalItemType),
		("data", Any),
		("path", list[str|int]), # object path
	],
)

EXTERNAL_ITEMS_EXTENSIONS: dict[ExternalItemType, str] = {
	"ndarray": "npy",
	"jsonl": "jsonl",
}

EXTERNAL_ITEMS_EXTENSIONS_INV: dict[str, ExternalItemType] = {
	ext: item_type
	for item_type, ext in EXTERNAL_ITEMS_EXTENSIONS.items()
}




