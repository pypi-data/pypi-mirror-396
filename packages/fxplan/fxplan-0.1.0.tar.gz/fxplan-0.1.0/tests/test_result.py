import pytest
from decimal import Decimal
from src.fxplan.result import Result
from src.fxplan.calculator import Calculator


def _mock_calculator_state() -> Calculator:
    calc = Calculator()
    calc.set_symbol("EURUSD")
    calc.set_is_long(True)
    calc.set_entry_price(1.1000)
    calc.set_sl_in_pips(50)
    calc.set_tp_in_pips(100)
    calc.set_position_size_in_lots(1.0)
    calc.calculate()
    return calc


class TestGetResult:
    def test_valid(self):
        calc = _mock_calculator_state()
        result = calc.get_result()
        assert result["symbol"] == "EURUSD"
        assert result["target_currency"] == "USD"
        assert result["rrr"] == Decimal("2.00")

    def test_invalid(self):
        calc = Calculator()
        with pytest.raises(AttributeError):
            calc.get_result()


class TestGetResultAsJson:
    def test_valid(self):
        calc = _mock_calculator_state()
        result = calc.get_result_as_json()
        result = calc.get_result_as_json("string")
        result = calc.get_result_as_json("float")

    def test_invalid(self):
        calc = _mock_calculator_state()
        with pytest.raises(ValueError, match="Numbers can be converted to 'string' or 'float' only."):
            calc.get_result_as_json(convert_numbers_to="int")
        with pytest.raises(ValueError, match="Numbers can be converted to 'string' or 'float' only."):
            calc.get_result_as_json(convert_numbers_to="str")
