# [The entire code from my previous response would go here]
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class SpanParams:
    """Parameters for SPAN calculation"""

    price_scan_range: float  # Price movement range (in %)
    volatility_scan_range: float  # Volatility movement range (in %)
    short_option_minimum: float  # Minimum charge for short options
    spot_charge_rate: float  # Additional charge for spot month
    inter_month_spread_charge: float  # Spread charge between months


class SpanCalculator:
    def __init__(self, params: SpanParams):
        self.params = params
        # Define 16 standard SPAN scenarios
        # (price_change, volatility_change)
        self.scenarios = [
            (1.0, 1.0),  # Scenario 1: Price up, Vol up
            (1.0, -1.0),  # Scenario 2: Price up, Vol down
            (-1.0, 1.0),  # Scenario 3: Price down, Vol up
            (-1.0, -1.0),  # Scenario 4: Price down, Vol down
            (2.0, 0.0),  # Scenario 5: Extreme price up
            (-2.0, 0.0),  # Scenario 6: Extreme price down
            (0.0, 2.0),  # Scenario 7: Extreme vol up
            (0.0, -2.0),  # Scenario 8: Extreme vol down
            # ... Additional scenarios would be defined here
        ]

    def calculate_risk_array(
        self,
        price: float,
        position_size: int,
        is_spot_month: bool,
        is_short_option: bool,
    ) -> np.ndarray:
        """Calculate risk array for a single position"""
        risk_array = []

        for price_shift, vol_shift in self.scenarios:
            # Calculate price stress
            price_stress = price * (
                1 + (price_shift * self.params.price_scan_range / 100)
            )

            # Calculate basic risk for scenario
            scenario_risk = (price_stress - price) * position_size

            # Add volatility effect (simplified)
            vol_effect = abs(
                price * vol_shift * self.params.volatility_scan_range / 100
            )
            scenario_risk += vol_effect

            risk_array.append(scenario_risk)

        risk_array = np.array(risk_array)

        # Apply spot month charge if applicable
        if is_spot_month:
            risk_array += abs(
                price * position_size * self.params.spot_charge_rate
            )

        # Apply short option minimum if applicable
        if is_short_option:
            risk_array = np.maximum(
                risk_array,
                self.params.short_option_minimum * abs(position_size),
            )

        return risk_array

    def calculate_portfolio_margin(
        self, positions: List[Dict]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate SPAN margin for a portfolio of positions

        Args:
            positions: List of dictionaries containing position details
                      Each dict should have:
                      - symbol: str
                      - price: float
                      - position_size: int
                      - is_spot_month: bool
                      - is_short_option: bool

        Returns:
            total_margin: Total margin requirement
            components: Breakdown of margin components
        """
        # Calculate risk arrays for each position
        position_risks = []
        for pos in positions:
            risk_array = self.calculate_risk_array(
                price=pos['price'],
                position_size=pos['position_size'],
                is_spot_month=pos['is_spot_month'],
                is_short_option=pos['is_short_option'],
            )
            position_risks.append(risk_array)

        # Combine risk arrays (accounting for portfolio effects)
        portfolio_risk_array = np.sum(position_risks, axis=0)

        # Scan risk is the largest possible loss
        scan_risk = abs(min(portfolio_risk_array))

        # Calculate inter-month spread charge (simplified)
        spread_charge = self.calculate_spread_charge(positions)

        # Calculate total margin
        total_margin = scan_risk + spread_charge

        components = {
            'scan_risk': scan_risk,
            'spread_charge': spread_charge,
            'total_margin': total_margin,
        }

        return total_margin, components

    def calculate_spread_charge(self, positions: List[Dict]) -> float:
        """Calculate inter-month spread charge"""
        # Simplified implementation
        # In reality, would need to consider actual calendar spreads
        total_position_value = sum(
            abs(p['price'] * p['position_size']) for p in positions
        )
        return total_position_value * self.params.inter_month_spread_charge


def example_usage():
    # Example parameters (these would normally come from exchange specifications)
    params = SpanParams(
        price_scan_range=15.0,  # 15% price movement
        volatility_scan_range=10.0,  # 10% vol movement
        short_option_minimum=100,  # $100 minimum for short options
        spot_charge_rate=0.01,  # 1% additional charge for spot month
        inter_month_spread_charge=0.005,  # 0.5% spread charge
    )

    # Initialize calculator
    calculator = SpanCalculator(params)

    # Example portfolio
    positions = [
        {
            'symbol': 'BTCUSD_231229',
            'price': 40000,
            'position_size': 1,
            'is_spot_month': False,
            'is_short_option': False,
        },
        {
            'symbol': 'BTCUSD_231229',
            'price': 41000,
            'position_size': -1,
            'is_spot_month': True,
            'is_short_option': False,
        },
    ]

    # Calculate margin
    margin, components = calculator.calculate_portfolio_margin(positions)

    print(f"Margin Components:")
    for component, value in components.items():
        print(f"{component}: ${value:,.2f}")


if __name__ == "__main__":
    example_usage()
