from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ProfitAssumptions:
    """Cost and rate assumptions used for early-stage profit screening."""

    product_cost: float
    shipping_cost: float
    platform_fee_rate: float
    advertising_cost_rate: float
    return_rate: float

    def validate(self) -> None:
        costs = {
            "product_cost": self.product_cost,
            "shipping_cost": self.shipping_cost,
        }
        for name, value in costs.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative")

        rates = {
            "platform_fee_rate": self.platform_fee_rate,
            "advertising_cost_rate": self.advertising_cost_rate,
            "return_rate": self.return_rate,
        }
        for name, value in rates.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")

        if self.contribution_rate <= 0:
            raise ValueError(
                "The combined platform fee, advertising cost and return rate "
                "must be lower than 100%."
            )

    @property
    def fixed_cost_per_unit(self) -> float:
        return self.product_cost + self.shipping_cost

    @property
    def variable_rate(self) -> float:
        return (
            self.platform_fee_rate
            + self.advertising_cost_rate
            + self.return_rate
        )

    @property
    def contribution_rate(self) -> float:
        return 1 - self.variable_rate


@dataclass(frozen=True)
class ProfitEstimate:
    gross_profit_per_unit: float
    net_profit_per_unit: float
    net_margin: float
    break_even_price: float
    estimated_monthly_net_profit: float


def estimate_profit(
    price: float,
    monthly_sales: float,
    assumptions: ProfitAssumptions,
) -> ProfitEstimate:
    """Estimate unit and monthly profit for one product."""

    assumptions.validate()
    if price < 0:
        raise ValueError("price cannot be negative")
    if monthly_sales < 0:
        raise ValueError("monthly_sales cannot be negative")

    gross_profit = price - assumptions.fixed_cost_per_unit
    net_profit = (
        price * assumptions.contribution_rate
        - assumptions.fixed_cost_per_unit
    )
    net_margin = net_profit / price if price > 0 else 0.0
    break_even_price = (
        assumptions.fixed_cost_per_unit / assumptions.contribution_rate
    )

    return ProfitEstimate(
        gross_profit_per_unit=round(gross_profit, 2),
        net_profit_per_unit=round(net_profit, 2),
        net_margin=round(net_margin, 4),
        break_even_price=round(break_even_price, 2),
        estimated_monthly_net_profit=round(net_profit * monthly_sales, 2),
    )


def add_profit_estimates(
    data: pd.DataFrame,
    assumptions: ProfitAssumptions,
) -> pd.DataFrame:
    """Add profit-estimation columns to a cleaned market DataFrame."""

    assumptions.validate()
    result = data.copy()

    prices = pd.to_numeric(result["price"], errors="coerce").fillna(0).clip(lower=0)
    monthly_sales = (
        pd.to_numeric(result["monthly_sales"], errors="coerce")
        .fillna(0)
        .clip(lower=0)
    )

    raw_gross_profit = prices - assumptions.fixed_cost_per_unit
    raw_net_profit = (
        prices * assumptions.contribution_rate
        - assumptions.fixed_cost_per_unit
    )

    result["estimated_unit_gross_profit"] = raw_gross_profit.round(2)
    result["estimated_unit_net_profit"] = raw_net_profit.round(2)
    result["estimated_net_margin"] = np.where(
        prices > 0,
        raw_net_profit / prices,
        0.0,
    ).round(4)
    result["break_even_price"] = round(
        assumptions.fixed_cost_per_unit / assumptions.contribution_rate,
        2,
    )
    result["estimated_monthly_net_profit"] = (
        raw_net_profit * monthly_sales
    ).round(2)

    return result
