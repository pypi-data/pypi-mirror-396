import re
from decimal import Decimal
from typing import Tuple, Union


def parse_symbol(symbol: str) -> Tuple[str, str]:
    if not isinstance(symbol, str):
        raise TypeError("Symbol must be a string.")

    cleaned = re.sub(r'[-/]', '', symbol.upper().strip())

    if len(cleaned) != 6:
        raise ValueError(f"Symbol must contain only 6 letters.")

    if not cleaned.isalpha():
        raise ValueError(f"Symbol must contain only letters.")

    base = cleaned[:3]
    quote = cleaned[3:]

    return base, quote

def to_decimal(value: Union[Decimal, int, float, str]) -> Decimal:
    if isinstance(value, Decimal):
        return value

    if not isinstance(value, (int, float, str)):
        raise TypeError(f"Value '{value}' is not a valid number in the format of Decimal, int, float or string.")

    try:
        return Decimal(str(value))
    except:
        raise ValueError(f"Cannot convert value '{value}' to Decimal.")

def convert_pips_to_points(pips: Decimal) -> Decimal:
    pips = to_decimal(pips)
    return pips * 10

def convert_points_to_pips(points: Decimal) -> Decimal:
    points = to_decimal(points)
    return points / 10

def parse_currency(currency: str) -> str:
    if not isinstance(currency, str):
        raise TypeError("Currency must be a string.")

    currency = currency.upper().strip()

    if not currency.isalpha():
        raise ValueError("Currency must contain only letters.")

    if len(currency) != 3:
        raise ValueError("Currency must contain only 3 letters.")

    return currency

def exchange_currency_by_rate(**kwargs: dict) -> (Decimal, str):
    source_amount = to_decimal(kwargs.get("source_amount"))
    source_currency = parse_currency(kwargs.get("source_currency"))
    base, quote = parse_symbol(kwargs.get("exchange_symbol"))
    exchange_rate = to_decimal(kwargs.get("exchange_rate"))

    if source_amount is None or source_amount <= 0:
        raise ValueError("Source amount must be positive.")

    if exchange_rate is None or exchange_rate <= 0:
        raise ValueError("Exchange rate must be positive.")

    if base == quote:
        raise ValueError("Exchange symbol must contain different base and quote currencies.")

    if source_currency != base and source_currency != quote:
        raise ValueError(f"Source currency '{source_currency}' does not match exchange symbol '{base}{quote}'.")

    if source_currency == base:
        return (source_amount * exchange_rate, quote)
    else:
        return (source_amount / exchange_rate, base)
