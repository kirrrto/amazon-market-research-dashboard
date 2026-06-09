import pandas as pd
import pytest

from src.finance import (
    ProfitAssumptions,
    add_profit_estimates,
    estimate_profit,
)


def standard_assumptions() -> ProfitAssumptions:
    return ProfitAssumptions(
        product_cost=30,
        shipping_cost=10,
        platform_fee_rate=0.15,
        advertising_cost_rate=0.10,
        return_rate=0.05,
    )


def test_estimate_profit_calculates_expected_values():
    result = estimate_profit(
        price=100,
        monthly_sales=10,
        assumptions=standard_assumptions(),
    )

    assert result.gross_profit_per_unit == 60.0
    assert result.net_profit_per_unit == 30.0
    assert result.net_margin == 0.30
    assert result.break_even_price == 57.14
    assert result.estimated_monthly_net_profit == 300.0


def test_add_profit_estimates_adds_financial_columns():
    data = pd.DataFrame(
        [{"price": 100, "monthly_sales": 10, "asin": "A1"}]
    )

    result = add_profit_estimates(data, standard_assumptions())

    assert result.loc[0, "estimated_unit_net_profit"] == 30.0
    assert result.loc[0, "estimated_net_margin"] == 0.30
    assert result.loc[0, "estimated_monthly_net_profit"] == 300.0
    assert result.loc[0, "break_even_price"] == 57.14


def test_negative_cost_is_rejected():
    assumptions = ProfitAssumptions(
        product_cost=-1,
        shipping_cost=10,
        platform_fee_rate=0.15,
        advertising_cost_rate=0.10,
        return_rate=0.05,
    )

    with pytest.raises(ValueError, match="product_cost cannot be negative"):
        assumptions.validate()


def test_unsustainable_variable_rates_are_rejected():
    assumptions = ProfitAssumptions(
        product_cost=30,
        shipping_cost=10,
        platform_fee_rate=0.50,
        advertising_cost_rate=0.30,
        return_rate=0.20,
    )

    with pytest.raises(ValueError, match="must be lower than 100%"):
        assumptions.validate()
