import json
from decimal import Decimal
from typing import Dict, Any


class Result:
    def __init__(self) -> None:
        self._result: Dict[str, Any] = {}

    def _set_result(self) -> None:
        self._result = {
            "symbol": self._symbol.get_symbol(),
            "base_currency": self._symbol.get_base_currency(),
            "quote_currency": self._symbol.get_quote_currency(),
            "lot_size": self._symbol.get_lot_size(),
            "pip_size": self._symbol.get_pip_size(),
            "digits": self._symbol.get_digits(),
            "target_currency": self._target_currency,
            "exchange_rate": {
                "symbol": self._exchange_rate["symbol"],
                "rate": self._exchange_rate["rate"],
            },
            "is_long": self._is_long,
            "position_size_in_lots": self._position_size_in_lots,
            "entry_price": self._entry_price,
            "sl_price": self._sl_price,
            "tp_price": self._tp_price,
            "commission_per_lot_in_money": self._commission_per_lot_in_money,
            "commission_per_lot_in_pips": self._commission_per_lot_in_pips,
            "commission_in_money": self._commission_in_money,
            "rr_in_pips": {
                "sl_in_pips": self._sl_in_pips,
                "tp_in_pips": self._tp_in_pips,
            },
            "rr_in_points": {
                "sl_in_points": self._sl_in_points,
                "tp_in_points": self._tp_in_points,
            },
            "rr_in_money": {
                "sl_in_money": self._sl_in_money,
                "tp_in_money": self._tp_in_money,
            },
            "rrr": self._rrr,
            "rr_with_commission_in_money": {
                "sl_with_commission_in_money": self._sl_with_commission_in_money,
                "tp_with_commission_in_money": self._tp_with_commission_in_money,
            },
            "rrr_with_commission": self._rrr_with_commission,
        }

    def get_result(self) -> Dict[str, Any]:
        if not self._result:
            self._set_result()

        return self._result

    def get_result_as_json(self, convert_numbers_to: str = "string") -> str:
        if convert_numbers_to not in ["string", "float"]:
            raise ValueError("Numbers can be converted to 'string' or 'float' only.")

        if not self._result:
            self._set_result()

        if convert_numbers_to == "string":
            return json.dumps(self._result, indent=4, default=lambda x: str(x) if isinstance(x, Decimal) else x)
        elif convert_numbers_to == "float":
            return json.dumps(self._result, indent=4, default=lambda x: float(x) if isinstance(x, Decimal) else x)
