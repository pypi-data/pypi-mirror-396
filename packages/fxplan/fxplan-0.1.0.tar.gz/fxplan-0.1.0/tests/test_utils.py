import pytest
from src.fxplan.utils import *


class TestParseSymbol:
    def test_valid(self):
        assert parse_symbol("EURUSD") == ("EUR", "USD")
        assert parse_symbol("eur/USD") == ("EUR", "USD")
        assert parse_symbol("Eur-uSd") == ("EUR", "USD")

    def test_invalid(self):
        with pytest.raises(ValueError, match="Symbol must contain only 6 letters."):
            parse_symbol("EURUS")
        with pytest.raises(ValueError, match="Symbol must contain only letters."):
            parse_symbol("EUR123")
        with pytest.raises(TypeError, match="Symbol must be a string."):
            parse_symbol(None)
        with pytest.raises(TypeError, match="Symbol must be a string."):
            parse_symbol(123456)


class TestToDecimal:
    def test_valid(self):
        assert to_decimal(Decimal(1.0)) == Decimal(1.0)
        assert to_decimal(1) == Decimal("1")
        assert to_decimal(1.0) == Decimal("1.0")
        assert to_decimal("1.0") == Decimal(1.0)
        assert to_decimal("1") == Decimal(1)

    def test_invalid(self):
        with pytest.raises(TypeError):
            to_decimal(None)
        with pytest.raises(TypeError):
            to_decimal(object())
        with pytest.raises(ValueError):
            to_decimal("12f")
        with pytest.raises(ValueError):
            to_decimal("invalid")


class TestParseCurrency:
    def test_valid(self):
        assert parse_currency("EUR") == "EUR"
        assert parse_currency("eUr") == "EUR"

    def test_invalid(self):
        with pytest.raises(TypeError):
            parse_currency(None)
        with pytest.raises(TypeError):
            parse_currency(object())
        with pytest.raises(ValueError):
            parse_currency("123")
        with pytest.raises(ValueError):
            parse_currency("invalid")


class TestExchangeCurrencyByRate:
    def test_valid(self):
        assert exchange_currency_by_rate(
            source_amount=Decimal("100"),
            source_currency="Eur",
            exchange_symbol="EUR/usd",
            exchange_rate=Decimal("1.21868")
        ) == (Decimal("121.868"), "USD")
        assert exchange_currency_by_rate(
            source_amount=Decimal("20586.8"),
            source_currency="jPy",
            exchange_symbol="gbp-JPY",
            exchange_rate=Decimal("205.868")
        ) == (Decimal("100"), "GBP")

    def test_invalid(self):
        with pytest.raises(TypeError):
            exchange_currency_by_rate(
                source_amount=None,
                source_currency="EUR",
                exchange_symbol="EUR/usd",
                exchange_rate=Decimal("1.21868")
            )
        with pytest.raises(TypeError):
            exchange_currency_by_rate(
                source_amount=Decimal("100"),
                source_currency="EUR",
                exchange_symbol="EUR/usd",
                exchange_rate=None
            )
        with pytest.raises(ValueError):
            exchange_currency_by_rate(
                source_amount=Decimal("100"),
                source_currency="EUR",
                exchange_symbol="EUR/usd",
                exchange_rate=Decimal("-1")
            )
        with pytest.raises(ValueError, match="Exchange symbol must contain different base and quote currencies."):
            exchange_currency_by_rate(
                source_amount=Decimal("100"),
                source_currency="EUR",
                exchange_symbol="usd/usd",
                exchange_rate=Decimal("1.21868")
            )
        with pytest.raises(ValueError, match="Source currency 'GBP' does not match exchange symbol 'EURUSD'."):
            exchange_currency_by_rate(
                source_amount=Decimal("100"),
                source_currency="GBP",
                exchange_symbol="EUR/usd",
                exchange_rate=Decimal("1.21868")
            )
