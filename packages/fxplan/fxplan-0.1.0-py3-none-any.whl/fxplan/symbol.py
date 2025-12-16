from decimal import Decimal
from typing import Optional, Union
from .utils import *


class Symbol:
    def __init__(self, symbol: str):
        self._symbol: str = symbol
        self._base_currency: Optional[str] = None
        self._quote_currency: Optional[str] = None
        self._lot_size: Decimal = Decimal("100000")
        self._pip_size: Decimal = Decimal("0.0001")
        self._digits: Decimal = Decimal("5")

        self._set_default_symbol_specification()

    def _set_default_symbol_specification(self) -> None:
        self._base_currency, self._quote_currency = parse_symbol(self._symbol)
        self._set_standard_lot_size()
        self._set_standard_pip_size()
        self._set_standard_digits()

    def _set_standard_lot_size(self) -> None:
        if self._base_currency == "XAU":
            self._lot_size = Decimal("100")

    def _set_standard_pip_size(self) -> None:
        if self._quote_currency == "JPY":
            self._pip_size = Decimal("0.01")
        elif self._base_currency == "XAU":
            self._pip_size = Decimal("0.01")

    def _set_standard_digits(self) -> None:
        if self._quote_currency == "JPY":
            self._digits = Decimal("3")
        elif self._base_currency == "XAU":
            self._digits = Decimal("2")

    def get_symbol(self) -> str:
        return self._symbol

    def get_base_currency(self) -> str:
        return self._base_currency

    def get_quote_currency(self) -> str:
        return self._quote_currency

    def get_lot_size(self) -> Decimal:
        return self._lot_size

    def set_lot_size(self, lot_size: Union[Decimal, int, float, str]) -> None:
        lot_size = to_decimal(lot_size)
        if lot_size <= 0:
            raise ValueError("Lot size must be positive.")
        self._lot_size = lot_size

    def get_pip_size(self) -> Decimal:
        return self._pip_size

    def set_pip_size(self, pip_size: Union[Decimal, int, float, str]) -> None:
        pip_size = to_decimal(pip_size)
        if pip_size <= 0:
            raise ValueError("Pip size must be positive.")
        self._pip_size = pip_size

    def get_digits(self) -> Decimal:
        return self._digits

    def set_digits(self, digits: Union[Decimal, int, float, str]) -> None:
        digits = to_decimal(digits)
        if digits <= 0:
            raise ValueError("Digits must be positive.")
        self._digits = digits

    def get_price_precision(self) -> Decimal:
        return Decimal("1") / (10 ** self._digits)
