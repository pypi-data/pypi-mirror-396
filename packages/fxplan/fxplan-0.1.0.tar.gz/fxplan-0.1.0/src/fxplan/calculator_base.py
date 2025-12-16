from decimal import Decimal, ROUND_FLOOR
from typing import Optional, Union
from .symbol import Symbol
from .result import Result
from .utils import *


class CalculatorBase:
    def __init__(self):
        self._symbol: Union[Symbol, str, None] = None
        self._target_currency: Optional[str] = "USD"
        self._exchange_rate: Optional[dict] = {"symbol": None, "rate": None}
        self._is_long: Optional[bool] = None
        self._position_size_in_lots: Optional[Decimal] = None
        self._entry_price: Optional[Decimal] = None
        self._sl_price: Optional[Decimal] = None
        self._tp_price: Optional[Decimal] = None
        self._sl_in_pips: Optional[Decimal] = None
        self._tp_in_pips: Optional[Decimal] = None
        self._sl_in_points: Optional[Decimal] = None
        self._tp_in_points: Optional[Decimal] = None
        self._sl_in_money: Optional[Decimal] = None
        self._tp_in_money: Optional[Decimal] = None
        self._commission_per_lot_in_money: Decimal = Decimal(0)
        self._commission_per_lot_in_pips: Decimal = Decimal(0)
        self._commission_in_money: Decimal = Decimal(0)
        self._sl_with_commission_in_money: Optional[Decimal] = None
        self._tp_with_commission_in_money: Optional[Decimal] = None
        self._rrr: Optional[Decimal] = None
        self._rrr_with_commission: Optional[Decimal] = None
        self._result: Result = Result()

    def set_symbol(self, symbol: Union[Symbol, str]):
        if self._symbol is not None:
            raise ValueError("Symbol is already set.")

        if isinstance(symbol, Symbol):
            self._symbol = symbol
        elif isinstance(symbol, str):
            self._symbol = Symbol(symbol)
        else:
            raise TypeError("Symbol must be a string or a Symbol object.")

    def _raise_error_if_symbol_is_not_set(self) -> None:
        if self._symbol is None:
            raise ValueError("Symbol must be set before setting other fields.")

    def set_target_currency(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Target currency must be a string.")

        self._target_currency = parse_currency(value)

    def set_exchange_rate(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError("Exchange rate must be a dictionary.")

        self._exchange_rate = {"symbol": value.get("symbol"), "rate": to_decimal(value.get("rate"))}

    def set_is_long(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Is long must be a boolean.")

        self._is_long = value

    def set_position_size_in_lots(self, value: Union[Decimal, int, float, str]):
        value = to_decimal(value)
        value = value.quantize(Decimal('0.01'), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Position size must be positive.")

        self._position_size_in_lots = value
        self._sl_in_money = None
        self._sl_with_commission_in_money = None

    def set_entry_price(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(self._symbol.get_price_precision(), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Entry price must be positive.")

        self._entry_price = value

    def set_sl_price(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(self._symbol.get_price_precision(), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Stop loss price must be positive.")

        self._sl_price = value
        self._sl_in_pips = None
        self._sl_in_points = None

    def set_tp_price(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(self._symbol.get_price_precision(), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Take profit price must be positive.")

        self._tp_price = value
        self._tp_in_pips = None
        self._tp_in_points = None

    def set_sl_in_pips(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(Decimal("0.1"), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Stop loss in pips must be positive.")

        self._sl_in_pips = value
        self._sl_price = None
        self._sl_in_points = None

    def set_tp_in_pips(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(Decimal("0.1"), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Take profit in pips must be positive.")

        self._tp_in_pips = value
        self._tp_price = None
        self._tp_in_points = None

    def set_sl_in_points(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(Decimal("1"), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Stop loss in points must be positive.")

        self._sl_in_points = value
        self._sl_price = None
        self._sl_in_pips = None

    def set_tp_in_points(self, value: Union[Decimal, int, float, str]):
        self._raise_error_if_symbol_is_not_set()

        value = to_decimal(value)
        value = value.quantize(Decimal("1"), rounding=ROUND_FLOOR)

        if value <= 0:
            raise ValueError("Take profit in points must be positive.")

        self._tp_in_points = value
        self._tp_price = None
        self._tp_in_pips = None

    def set_sl_in_money(self, value: Union[Decimal, int, float, str]):
        value = to_decimal(value)

        if value <= 0:
            raise ValueError("Stop loss in money must be positive.")

        self._sl_in_money = value
        self._position_size_in_lots = None
        self._sl_with_commission_in_money = None

    def set_commission_per_lot_in_money(self, value: Union[Decimal, int, float, str]):
        value = to_decimal(value)

        if value < 0:
            raise ValueError("Commission per lot in money must be non-negative.")

        self._commission_per_lot_in_money = value

    def set_sl_with_commission_in_money(self, value: Union[Decimal, int, float, str]):
        value = to_decimal(value)

        if value < 0:
            raise ValueError("Stop loss with commission in money must be non-negative.")

        self._sl_with_commission_in_money = value
        self._position_size_in_lots = None
        self._sl_in_money = None
