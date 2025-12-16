import pytest
from decimal import Decimal
from src.fxplan.symbol import Symbol


class TestConstructor:
    def test_valid(self):
        symbol1 = Symbol("Eur/Usd")
        assert symbol1.get_base_currency() == "EUR"
        assert symbol1.get_quote_currency() == "USD"
        assert symbol1.get_lot_size() == Decimal("100000")
        assert symbol1.get_pip_size() == Decimal("0.0001")
        assert symbol1.get_digits() == Decimal("5")
        assert symbol1.get_price_precision() == Decimal("0.00001")

        symbol2 = Symbol("usd-jpy")
        assert symbol2.get_base_currency() == "USD"
        assert symbol2.get_quote_currency() == "JPY"
        assert symbol2.get_lot_size() == Decimal("100000")
        assert symbol2.get_pip_size() == Decimal("0.01")
        assert symbol2.get_digits() == Decimal("3")
        assert symbol2.get_price_precision() == Decimal("0.001")

        symbol3 = Symbol("XAUUSD")
        assert symbol3.get_base_currency() == "XAU"
        assert symbol3.get_quote_currency() == "USD"
        assert symbol3.get_lot_size() == Decimal("100")
        assert symbol3.get_pip_size() == Decimal("0.01")
        assert symbol3.get_digits() == Decimal("2")
        assert symbol3.get_price_precision() == Decimal("0.01")

    def test_invalid(self):
        with pytest.raises(ValueError, match="Symbol must contain only 6 letters."):
            Symbol("EURUS")
        with pytest.raises(ValueError, match="Symbol must contain only letters."):
            Symbol("EUR123")


class TestSetLotSize:
    def test_valid(self):
        symbol = Symbol("EURUSD")
        symbol.set_lot_size(Decimal("1000"))
        assert symbol.get_lot_size() == Decimal("1000")
        symbol.set_lot_size(1000)
        assert symbol.get_lot_size() == Decimal("1000")
        symbol.set_lot_size("1000")
        assert symbol.get_lot_size() == Decimal("1000")

    def test_invalid(self):
        symbol = Symbol("EURUSD")
        with pytest.raises(ValueError, match="Lot size must be positive."):
            symbol.set_lot_size(-1)
        with pytest.raises(ValueError, match="Lot size must be positive."):
            symbol.set_lot_size(0)
        with pytest.raises(TypeError):
            symbol.set_lot_size(None)
        with pytest.raises(ValueError):
            symbol.set_lot_size("xxx")
        with pytest.raises(ValueError):
            symbol.set_lot_size("")


class TestSetPipSize:
    def test_valid(self):
        symbol = Symbol("EURUSD")
        symbol.set_pip_size(Decimal("0.01"))
        assert symbol.get_pip_size() == Decimal("0.01")
        symbol.set_pip_size(0.01)
        assert symbol.get_pip_size() == Decimal("0.01")
        symbol.set_pip_size("0.01")
        assert symbol.get_pip_size() == Decimal("0.01")

    def test_invalid(self):
        symbol = Symbol("EURUSD")
        with pytest.raises(ValueError, match="Pip size must be positive."):
            symbol.set_pip_size(-1)
        with pytest.raises(ValueError, match="Pip size must be positive."):
            symbol.set_pip_size(0)
        with pytest.raises(TypeError):
            symbol.set_pip_size(None)
        with pytest.raises(ValueError):
            symbol.set_pip_size("xxx")
        with pytest.raises(ValueError):
            symbol.set_pip_size("")


class TestSetDigits:
    def test_valid(self):
        symbol = Symbol("EURUSD")
        symbol.set_digits(4)
        assert symbol.get_digits() == Decimal("4")
        assert symbol.get_price_precision() == Decimal("0.0001")
        symbol.set_digits("2")
        assert symbol.get_digits() == Decimal("2")
        assert symbol.get_price_precision() == Decimal("0.01")

    def test_invalid(self):
        symbol = Symbol("EURUSD")
        with pytest.raises(ValueError, match="Digits must be positive."):
            symbol.set_digits(-1)
        with pytest.raises(ValueError, match="Digits must be positive."):
            symbol.set_digits(0)
        with pytest.raises(TypeError):
            symbol.set_digits(None)
        with pytest.raises(ValueError):
            symbol.set_digits("xxx")
        with pytest.raises(ValueError):
            symbol.set_digits("")
