import pytest
from decimal import Decimal
from src.fxplan.calculator_base import CalculatorBase
from src.fxplan.symbol import Symbol


class TestSetSymbol:
    def test_valid(self):
        calc1 = CalculatorBase()
        calc1.set_symbol("EURUSD")
        assert isinstance(calc1._symbol, Symbol)

        calc2 = CalculatorBase()
        symbol = Symbol("GBPJPY")
        calc2.set_symbol(symbol)
        assert calc2._symbol is symbol

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(TypeError, match="Symbol must be a string or a Symbol object."):
            calc.set_symbol(None)
        with pytest.raises(TypeError, match="Symbol must be a string or a Symbol object."):
            calc.set_symbol(123)
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Symbol is already set."):
            calc.set_symbol("GBPUSD")


class TestSetTargetCurrency:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_target_currency("GBP")
        assert calc._target_currency == "GBP"

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(TypeError, match="Target currency must be a string."):
            calc.set_target_currency(None)
        with pytest.raises(TypeError, match="Target currency must be a string."):
            calc.set_target_currency(123)
        with pytest.raises(ValueError, match="Currency must contain only 3 letters."):
            calc.set_target_currency("ABCD")
        with pytest.raises(ValueError, match="Currency must contain only letters."):
            calc.set_target_currency("123")


class TestSetExchangeRate:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("GBPJPY")
        calc.set_exchange_rate({"symbol": "USDJPY", "rate": Decimal("150.000")})
        assert calc._exchange_rate["rate"] == Decimal("150.000")

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(TypeError, match="Exchange rate must be a dictionary."):
            calc.set_exchange_rate(None)
        with pytest.raises(TypeError, match="Exchange rate must be a dictionary."):
            calc.set_exchange_rate("invalid")


class TestSetIsLong:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_is_long(True)
        assert calc._is_long is True

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(TypeError, match="Is long must be a boolean."):
            calc.set_is_long(None)
        with pytest.raises(TypeError, match="Is long must be a boolean."):
            calc.set_is_long("true")


class TestSetPositionSizeInLots:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_position_size_in_lots(1.5)
        assert calc._position_size_in_lots == Decimal("1.50")

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(ValueError, match="Position size must be positive."):
            calc.set_position_size_in_lots(-1)
        with pytest.raises(ValueError, match="Position size must be positive."):
            calc.set_position_size_in_lots(0)


class TestSetEntryPrice:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_entry_price(1.1000)
        assert calc._entry_price == Decimal("1.10000")

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(ValueError, match="Symbol must be set before setting other fields."):
            calc.set_entry_price(1.1000)
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Entry price must be positive."):
            calc.set_entry_price(-1)
        with pytest.raises(ValueError, match="Entry price must be positive."):
            calc.set_entry_price(0)


class TestSetSlPrice:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_sl_price(1.0950)
        assert calc._sl_price == Decimal("1.09500")

    def test_invalid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Stop loss price must be positive."):
            calc.set_sl_price(-1)
        with pytest.raises(ValueError, match="Stop loss price must be positive."):
            calc.set_sl_price(0)


class TestSetTpPrice:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_tp_price(1.1100)
        assert calc._tp_price == Decimal("1.11000")

    def test_invalid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Take profit price must be positive."):
            calc.set_tp_price(-1)
        with pytest.raises(ValueError, match="Take profit price must be positive."):
            calc.set_tp_price(0)


class TestSetSlInPips:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_sl_in_pips(50)
        assert calc._sl_in_pips == Decimal("50.0")

    def test_invalid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Stop loss in pips must be positive."):
            calc.set_sl_in_pips(-1)
        with pytest.raises(ValueError, match="Stop loss in pips must be positive."):
            calc.set_sl_in_pips(0)


class TestSetTpInPips:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_tp_in_pips(100)
        assert calc._tp_in_pips == Decimal("100.0")

    def test_invalid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Take profit in pips must be positive."):
            calc.set_tp_in_pips(-1)
        with pytest.raises(ValueError, match="Take profit in pips must be positive."):
            calc.set_tp_in_pips(0)


class TestSetSlInPoints:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_sl_in_points(500)
        assert calc._sl_in_points == Decimal("500")

    def test_invalid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Stop loss in points must be positive."):
            calc.set_sl_in_points(-1)
        with pytest.raises(ValueError, match="Stop loss in points must be positive."):
            calc.set_sl_in_points(0)


class TestSetTpInPoints:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        calc.set_tp_in_points(1000)
        assert calc._tp_in_points == Decimal("1000")

    def test_invalid(self):
        calc = CalculatorBase()
        calc.set_symbol("EURUSD")
        with pytest.raises(ValueError, match="Take profit in points must be positive."):
            calc.set_tp_in_points(-1)
        with pytest.raises(ValueError, match="Take profit in points must be positive."):
            calc.set_tp_in_points(0)


class TestSetSlInMoney:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_sl_in_money(100)
        assert calc._sl_in_money == Decimal("100")

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(ValueError, match="Stop loss in money must be positive."):
            calc.set_sl_in_money(-1)
        with pytest.raises(ValueError, match="Stop loss in money must be positive."):
            calc.set_sl_in_money(0)


class TestSetCommissionPerLotInMoney:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_commission_per_lot_in_money(5)
        assert calc._commission_per_lot_in_money == Decimal("5")

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(ValueError, match="Commission per lot in money must be non-negative."):
            calc.set_commission_per_lot_in_money(-1)


class TestSetSlWithCommissionInMoney:
    def test_valid(self):
        calc = CalculatorBase()
        calc.set_sl_with_commission_in_money(105)
        assert calc._sl_with_commission_in_money == Decimal("105")

    def test_invalid(self):
        calc = CalculatorBase()
        with pytest.raises(ValueError, match="Stop loss with commission in money must be non-negative."):
            calc.set_sl_with_commission_in_money(-1)
