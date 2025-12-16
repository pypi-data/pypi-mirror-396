# FXPLAN

A comprehensive Python library for forex trading calculations, including position sizing, risk/reward analysis, stop loss and take profit calculations, and commission handling.

## Features

- **Position Sizing**: Calculate optimal position size based on risk amount or lot size
- **Stop Loss & Take Profit**: Calculate SL/TP in price, pips, or points with automatic conversions
- **Risk/Reward Ratio**: Calculate RRR with and without commission
- **Multi-Currency Support**: Handle currency conversions with exchange rates
- **Commission Handling**: Account for commission in calculations
- **Symbol Support**: Support for major, minor, JPY pairs, and XAU (Gold)
- **Precise Calculations**: Uses `Decimal` for financial precision
- **Flexible Input**: Accept prices, pips, or points as input
- **JSON Export**: Export calculation results as JSON

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Step 1: Set Required Parameters (Must-Have)](#step-1-set-required-parameters-must-have)
  - [Step 2: Set Optional Parameters](#step-2-set-optional-parameters)
  - [Step 3: Set Stop Loss and Take Profit](#step-3-set-stop-loss-and-take-profit)
  - [Step 4: Set Position Sizing](#step-4-set-position-sizing)
  - [Step 5: Calculate](#step-5-calculate)
  - [Step 6: Get Results](#step-6-get-results)
  - [Complete Example](#complete-example)
- [Symbol](#symbol)
- [License](#license)
- [Contributing](#contributing)

## Installation

```bash
pip install fxplan
```

## Quick Start

```python
from fxplan import Calculator

# Create a calculator instance
calc = Calculator()

# Set trading parameters
calc.set_symbol("EURUSD")
calc.set_is_long(True)
calc.set_entry_price(1.17968)
calc.set_sl_in_pips(50)
calc.set_tp_in_pips(100)
calc.set_position_size_in_lots(1.0)

# Calculate
calc.calculate()

# Get results
result = calc.get_result()
print(result)
```

## Usage

The calculator follows a specific flow to ensure all required parameters are set correctly. Follow these steps in order:

### Step 1: Set Required Parameters (Must-Have)

These three parameters are **required** and must be set first:

1. **Set Symbol** - Set the trading symbol first (must be done before setting entry price, SL, TP, or other parameters)
   ```python
   calc.set_symbol("EURUSD")  # or use Symbol object
   ```

2. **Set Position Direction** - Specify if the position is long or short
   ```python
   calc.set_is_long(True)   # True for long, False for short
   ```

3. **Set Entry Price** - Set the entry price for the trade
   ```python
   calc.set_entry_price(1.17968)
   ```

### Step 2: Set Optional Parameters

**Commission (if applicable)**

If you want to calculate with commission, set the commission per lot:
```python
calc.set_commission_per_lot_in_money(7)  # e.g., $7 per lot
```

**Target Currency (optional, default: USD)**

The target currency determines the currency for money calculations. Default is "USD":
```python
calc.set_target_currency("USD")  # Optional, defaults to "USD"
```

**Exchange Rate (required if quote currency ≠ target currency)**

If the quote currency of your symbol is different from the target currency, you must provide an exchange rate:
```python
# Example: Trading GBPJPY but want results in USD
calc.set_symbol("GBPJPY")
calc.set_target_currency("USD")
calc.set_exchange_rate({"symbol": "USDJPY", "rate": 158.968})
```

### Step 3: Set Stop Loss and Take Profit

For both SL and TP, you can set **only one** of the following options (the calculator will automatically calculate the others):

**Stop Loss Options:**
- `set_sl_price()` - Set stop loss as a price
- `set_sl_in_pips()` - Set stop loss in pips
- `set_sl_in_points()` - Set stop loss in points

**Take Profit Options:**
- `set_tp_price()` - Set take profit as a price
- `set_tp_in_pips()` - Set take profit in pips
- `set_tp_in_points()` - Set take profit in points

**Examples:**
```python
# Entry price
calc.set_entry_price(1.18000)

# Using set_sl_price and set_tp_in_pips
calc.set_sl_price(1.17900)
calc.set_tp_in_pips(30)

# Using set_sl_in_pips and set_tp_in_points
calc.set_sl_in_pips(10)
calc.set_tp_in_points(300)
```

### Step 4: Set Position Sizing

You can set **only one** of the following options:

**Option 1: Set Position Size Directly**
```python
calc.set_position_size_in_lots(1.0)
```

**Option 2: Calculate Position Size from Risk Amount (without commission)**
```python
calc.set_sl_in_money(500)  # Risk $500
```

**Option 3: Calculate Position Size from Risk Amount (with commission)**
```python
calc.set_sl_with_commission_in_money(500)  # Risk $500 including commission
```

### Step 5: Calculate

After setting all parameters, call the `calculate()` method:
```python
calc.calculate()
```

### Step 6: Get Results

Retrieve results in your desired format:

**As Dictionary:**
```python
result = calc.get_result()
print(result['sl_price'])
print(result['rrr'])
```

**As JSON String:**
```python
# With Decimal as strings (default)
json_result = calc.get_result_as_json()
print(json_result)

# Or with Decimal as floats
json_result = calc.get_result_as_json(convert_numbers_to="float")
print(json_result)
```

**Result Dictionary Structure**

```python
{
    "symbol": str,
    "base_currency": str,
    "quote_currency": str,
    "lot_size": Decimal,
    "pip_size": Decimal,
    "digits": Decimal,
    "target_currency": str,
    "exchange_rate": {
        "symbol": str,
        "rate": Decimal
    },
    "is_long": bool,
    "position_size_in_lots": Decimal,
    "entry_price": Decimal,
    "sl_price": Decimal,
    "tp_price": Decimal,
    "commission_per_lot_in_money": Decimal,
    "commission_per_lot_in_pips": Decimal,
    "commission_in_money": Decimal,
    "rr_in_pips": {
        "sl_in_pips": Decimal,
        "tp_in_pips": Decimal
    },
    "rr_in_points": {
        "sl_in_points": Decimal,
        "tp_in_points": Decimal
    },
    "rr_in_money": {
        "sl_in_money": Decimal,
        "tp_in_money": Decimal
    },
    "rrr": Decimal,
    "rr_with_commission_in_money": {
        "sl_with_commission_in_money": Decimal,
        "tp_with_commission_in_money": Decimal
    },
    "rrr_with_commission": Decimal
}
```

### Complete Example

```python
from fxplan import Calculator

calc = Calculator()

# Step 1: Required parameters
calc.set_symbol("GBPJPY")
calc.set_is_long(True)
calc.set_entry_price(186.968)

# Step 2: Optional parameters
calc.set_commission_per_lot_in_money(7)
calc.set_target_currency("USD")  # Optional, defaults to USD
calc.set_exchange_rate({"symbol": "USDJPY", "rate": 158.968})

# Step 3: Set SL/TP (choose one method per)
calc.set_sl_in_pips(50)
calc.set_tp_in_pips(100)

# Step 4: Position sizing (choose one method)
calc.set_sl_with_commission_in_money(100)

# Step 5: Calculate
calc.calculate()

# Step 6: Get results
result = calc.get_result_as_json()
print(result)
```

## Symbol

The `Symbol` class encapsulates currency pair specifications including lot size, pip size, and price digits. It automatically sets defaults based on symbol type:
- **Standard pairs** (EURUSD, GBPUSD): lot_size=100000, pip_size=0.0001, digits=5
- **JPY pairs** (USDJPY, EURJPY): lot_size=100000, pip_size=0.01, digits=3
- **XAU pairs** (XAUUSD): lot_size=100, pip_size=0.01, digits=2

When passing the symbol as `string` to the method `set_symbol()` of the class `Calculator` like below, the symbol's defaults are applied automatically and could not be customized later.
```python
calc = Calculator()
calc.set_symbol("EURUSD")
```

**Why Customize?**

Different brokers may provide different specifications for the same currency pair (e.g., different lot sizes, pip sizes, or price digits). **Always check the default values first and verify them with your broker's specifications before customizing.**

```python
from fxplan import Calculator, Symbol

# Check defaults
symbol = Symbol("EURUSD")
print(symbol.get_lot_size(), symbol.get_pip_size(), symbol.get_digits())

# Customize if broker specifications differ
symbol.set_lot_size(10000)
symbol.set_pip_size(0.001)
symbol.set_digits(4)

# Set symbol as object (not string)
calc = Calculator()
calc.set_symbol(symbol)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
