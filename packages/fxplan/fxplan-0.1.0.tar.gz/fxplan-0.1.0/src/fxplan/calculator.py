from decimal import Decimal, ROUND_FLOOR
from typing import Dict, Any
from .calculator_base import CalculatorBase
from .utils import *


class Calculator(CalculatorBase):
    def __init__(self):
        super().__init__()

    def calculate(self):
        self._validate()
        self._calculate_sl_price_and_in_pips_and_in_points()
        self._calculate_tp_price_and_in_pips_and_in_points()
        self._calculate_commission_per_lot_in_pips()
        self._calculate_position_size()
        self._calculate_sl_in_money()
        self._calculate_tp_in_money()
        self._calculate_sl_and_tp_with_commission_in_money()
        self._calculate_risk_reward_ratio()
        self._set_result()

    def _validate(self):
        self._validate_required_fields()
        self._validate_exchange_rate()
        self._validate_price_relation()

    def _validate_required_fields(self):
        if self._symbol is None:
            raise ValueError("Symbol is required.")

        if self._is_long is None:
            raise ValueError("Is long is required.")

        if self._entry_price is None:
            raise ValueError("Entry price is required.")

    def _validate_exchange_rate(self):
        if self._symbol.get_quote_currency() == self._target_currency:
            return

        exchange_pair = f"{self._symbol.get_quote_currency()}{self._target_currency}"
        reverse_exchange_pair = f"{self._target_currency}{self._symbol.get_quote_currency()}"

        if self._exchange_rate is None or self._exchange_rate["symbol"] is None or self._exchange_rate["rate"] is None:
            raise ValueError(f"Exchange rate of '{exchange_pair}' or '{reverse_exchange_pair}' is required.")

        if self._exchange_rate["rate"] <= 0:
            raise ValueError("Exchange rate rate must be positive.")

        base, quote = parse_symbol(self._exchange_rate["symbol"])

        if self._symbol.get_quote_currency() != base and self._symbol.get_quote_currency() != quote:
            raise ValueError(f"Exchange rate of '{exchange_pair}' or '{reverse_exchange_pair}' is required.")

        if self._target_currency != base and self._target_currency != quote:
            raise ValueError(f"Exchange rate of '{exchange_pair}' or '{reverse_exchange_pair}' is required.")

    def _validate_price_relation(self):
        if self._sl_price is not None:
            if self._is_long and self._sl_price >= self._entry_price:
                raise ValueError("Stop loss price must be lower than entry price in a long position.")
            elif not self._is_long and self._sl_price <= self._entry_price:
                raise ValueError("Stop loss price must be greater than entry price in a short position.")

        if self._tp_price is not None:
            if self._is_long and self._tp_price <= self._entry_price:
                raise ValueError("Take profit price must be greater than entry price in a long position.")
            elif not self._is_long and self._tp_price >= self._entry_price:
                raise ValueError("Take profit price must be lower than entry price in a short position.")

    def _calculate_sl_price_and_in_pips_and_in_points(self):
        if self._sl_price is not None and self._sl_in_pips is None and self._sl_in_points is None:
            self._calculate_sl_in_pips_by_prices()
            self._calculate_sl_in_points_by_pips()
        elif self._sl_in_pips is not None and self._sl_price is None and self._sl_in_points is None:
            self._calculate_sl_price_by_pips()
            self._calculate_sl_in_points_by_pips()
        elif self._sl_in_points is not None and self._sl_price is None and self._sl_in_pips is None:
            self._calculate_sl_in_pips_by_points()
            self._calculate_sl_price_by_pips()
        elif self._sl_price is None and self._sl_in_pips is None and self._sl_in_points is None:
            raise ValueError("One of the stop loss price, stop loss in pips or stop loss in points must be set.")
        else:
            raise ValueError("Only one of the stop loss price, stop loss in pips or stop loss in points is set.")

    def _calculate_tp_price_and_in_pips_and_in_points(self):
        if self._tp_price is not None and self._tp_in_pips is None and self._tp_in_points is None:
            self._calculate_tp_in_pips_by_prices()
            self._calculate_tp_in_points_by_pips()
        elif self._tp_in_pips is not None and self._tp_price is None and self._tp_in_points is None:
            self._calculate_tp_price_by_pips()
            self._calculate_tp_in_points_by_pips()
        elif self._tp_in_points is not None and self._tp_price is None and self._tp_in_pips is None:
            self._calculate_tp_in_pips_by_points()
            self._calculate_tp_price_by_pips()
        elif self._tp_price is None and self._tp_in_pips is None and self._tp_in_points is None:
            raise ValueError("One of the take profit price, take profit in pips or take profit in points must be set.")
        else:
            raise ValueError("Only one of the take profit price, take profit in pips or take profit in points is set.")

    def _calculate_sl_in_pips_by_prices(self):
        self._sl_in_pips = abs(self._entry_price - self._sl_price) / self._symbol.get_pip_size()

    def _calculate_tp_in_pips_by_prices(self):
        self._tp_in_pips = abs(self._tp_price - self._entry_price) / self._symbol.get_pip_size()

    def _calculate_sl_price_by_pips(self):
        if self._is_long:
            self._sl_price = self._entry_price - self._sl_in_pips * self._symbol.get_pip_size()
        else:
            self._sl_price = self._entry_price + self._sl_in_pips * self._symbol.get_pip_size()

    def _calculate_tp_price_by_pips(self):
        if self._is_long:
            self._tp_price = self._entry_price + self._tp_in_pips * self._symbol.get_pip_size()
        else:
            self._tp_price = self._entry_price - self._tp_in_pips * self._symbol.get_pip_size()

    def _calculate_sl_in_points_by_pips(self):
        self._sl_in_points = convert_pips_to_points(self._sl_in_pips)
        self._sl_in_points = self._sl_in_points.quantize(Decimal("1"), rounding=ROUND_FLOOR)

    def _calculate_tp_in_points_by_pips(self):
        self._tp_in_points = convert_pips_to_points(self._tp_in_pips)
        self._tp_in_points = self._tp_in_points.quantize(Decimal("1"), rounding=ROUND_FLOOR)

    def _calculate_sl_in_pips_by_points(self):
        self._sl_in_pips = convert_points_to_pips(self._sl_in_points)
        self._sl_in_pips = self._sl_in_pips.quantize(Decimal("0.1"), rounding=ROUND_FLOOR)

    def _calculate_tp_in_pips_by_points(self):
        self._tp_in_pips = convert_points_to_pips(self._tp_in_points)
        self._tp_in_pips = self._tp_in_pips.quantize(Decimal("0.1"), rounding=ROUND_FLOOR)

    def _calculate_commission_per_lot_in_pips(self):
        if self._commission_per_lot_in_money == 0:
            return

        if self._symbol.get_quote_currency() == self._target_currency:
            commission_per_lot_in_quote = self._commission_per_lot_in_money
        else:
            commission_per_lot_in_quote = self._exchange_currency(self._commission_per_lot_in_money, self._target_currency)

        self._commission_per_lot_in_pips = commission_per_lot_in_quote / self._symbol.get_pip_size() / self._symbol.get_lot_size()

    def _exchange_currency(self, source_amount: Decimal, source_currency: str) -> Decimal:
        exchange_result = exchange_currency_by_rate(
            source_amount=source_amount,
            source_currency=source_currency,
            exchange_symbol=self._exchange_rate["symbol"],
            exchange_rate=self._exchange_rate["rate"],
        )
        return exchange_result[0]

    def _calculate_position_size(self):
        if self._position_size_in_lots is not None and self._sl_in_money is None and self._sl_with_commission_in_money is None:
            return
        elif self._position_size_in_lots is None and self._sl_in_money is not None and self._sl_with_commission_in_money is None:
            self._calculate_position_size_by_sl_in_money()
        elif self._position_size_in_lots is None and self._sl_in_money is None and self._sl_with_commission_in_money is not None:
            self._calculate_position_size_by_sl_with_commission_in_money()
        else:
            raise ValueError("Only one of the position size in lots, stop loss in money or stop loss with commission in money is set.")

    def _calculate_position_size_by_sl_in_money(self):
        if self._symbol.get_quote_currency() == self._target_currency:
            sl_in_quote = self._sl_in_money
        else:
            sl_in_quote = self._exchange_currency(self._sl_in_money, self._target_currency)

        position_size = sl_in_quote / (self._sl_in_pips * self._symbol.get_pip_size() * self._symbol.get_lot_size())
        self._position_size_in_lots = position_size.quantize(Decimal('0.01'), rounding=ROUND_FLOOR)

    def _calculate_position_size_by_sl_with_commission_in_money(self):
        if self._symbol.get_quote_currency() == self._target_currency:
            sl_with_commission_in_quote = self._sl_with_commission_in_money
        else:
            sl_with_commission_in_quote = self._exchange_currency(self._sl_with_commission_in_money, self._target_currency)

        sl_with_commission_in_pips = self._sl_in_pips + self._commission_per_lot_in_pips
        position_size = sl_with_commission_in_quote / (sl_with_commission_in_pips * self._symbol.get_pip_size() * self._symbol.get_lot_size())
        self._position_size_in_lots = position_size.quantize(Decimal('0.01'), rounding=ROUND_FLOOR)

    def _calculate_sl_in_money(self):
        sl_in_quote = abs(self._entry_price - self._sl_price) * self._symbol.get_lot_size() * self._position_size_in_lots

        if self._symbol.get_quote_currency() == self._target_currency:
            self._sl_in_money = sl_in_quote
        else:
            self._sl_in_money = self._exchange_currency(sl_in_quote, self._symbol.get_quote_currency())

        self._sl_in_money = self._sl_in_money.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)

    def _calculate_tp_in_money(self):
        tp_in_quote = abs(self._entry_price - self._tp_price) * self._symbol.get_lot_size() * self._position_size_in_lots

        if self._symbol.get_quote_currency() == self._target_currency:
            self._tp_in_money = tp_in_quote
        else:
            self._tp_in_money = self._exchange_currency(tp_in_quote, self._symbol.get_quote_currency())

        self._tp_in_money = self._tp_in_money.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)

    def _calculate_sl_and_tp_with_commission_in_money(self):
        self._commission_in_money = self._commission_per_lot_in_money * self._position_size_in_lots
        self._sl_with_commission_in_money = self._sl_in_money + self._commission_in_money
        self._tp_with_commission_in_money = self._tp_in_money - self._commission_in_money

    def _calculate_risk_reward_ratio(self):
        self._rrr = self._tp_in_pips / self._sl_in_pips
        self._rrr = self._rrr.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)

        self._rrr_with_commission = self._tp_with_commission_in_money / self._sl_with_commission_in_money
        self._rrr_with_commission = self._rrr_with_commission.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)

    def _set_result(self):
        for k, v in vars(self).items():
            if k.startswith('_') and k != '_result':
                setattr(self._result, k, v)

    def get_result(self) -> Dict[str, Any]:
        return self._result.get_result()

    def get_result_as_json(self, convert_numbers_to: str = "string") -> str:
        return self._result.get_result_as_json(convert_numbers_to)
