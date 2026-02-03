"""
Bond Valuation Module
=====================

A focused, well-documented Bond class for fixed-income analytics.

Provides:
    - Bond pricing via discounted cash flow
    - Macaulay Duration
    - Modified Duration
    - Convexity
    - Price change estimation using duration-convexity adjustment

Conventions:
    - All rates expressed as decimals (5% = 0.05)
    - Time measured in years
    - Prices in same currency units as face value
"""

from typing import List, Tuple


class Bond:
    """
    Fixed-coupon bond with pricing and interest rate risk analytics.

    This class models a standard fixed-rate bond and provides methods to
    calculate its theoretical price and key risk measures (duration, convexity).

    Attributes:
        face_value (float): Par/principal value repaid at maturity
        coupon_rate (float): Annual coupon rate as decimal (e.g., 0.05 for 5%)
        years_to_maturity (int): Number of years until bond matures
        yield_to_maturity (float): Market discount rate as decimal
        payments_per_year (int): Coupon payment frequency (1=annual, 2=semi-annual, etc.)

    Example:
        >>> bond = Bond(
        ...     face_value=1000,
        ...     coupon_rate=0.06,
        ...     years_to_maturity=5,
        ...     yield_to_maturity=0.08,
        ...     payments_per_year=1
        ... )
        >>> print(f"Price: ${bond.price():.2f}")
        Price: $920.15
        >>> print(f"Modified Duration: {bond.modified_duration():.4f}")
        Modified Duration: 4.1105

    Note:
        The class assumes:
        - Settlement occurs on a coupon payment date (no accrued interest)
        - Flat yield curve (single rate for all cash flows)
        - No embedded options (not callable/putable)
    """

    def __init__(
        self,
        face_value: float,
        coupon_rate: float,
        years_to_maturity: int,
        yield_to_maturity: float,
        payments_per_year: int = 1
    ) -> None:
        """
        Initialize a Bond instance.

        Args:
            face_value: Par value of the bond (e.g., 1000)
            coupon_rate: Annual coupon rate as decimal (e.g., 0.06 for 6%)
            years_to_maturity: Years until maturity (must be positive integer)
            yield_to_maturity: Required yield/discount rate as decimal
            payments_per_year: Number of coupon payments per year (default: 1)

        Raises:
            ValueError: If any input parameter is invalid
        """
        # Validate inputs
        self._validate_inputs(
            face_value, coupon_rate, years_to_maturity,
            yield_to_maturity, payments_per_year
        )

        # Core attributes
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.years_to_maturity = years_to_maturity
        self.yield_to_maturity = yield_to_maturity
        self.payments_per_year = payments_per_year

        # Derived attributes (computed once for efficiency)
        self.total_periods = years_to_maturity * payments_per_year
        self.periodic_coupon = (coupon_rate * face_value) / payments_per_year
        self.periodic_yield = yield_to_maturity / payments_per_year

    def _validate_inputs(
        self,
        face_value: float,
        coupon_rate: float,
        years_to_maturity: int,
        yield_to_maturity: float,
        payments_per_year: int
    ) -> None:
        """
        Validate all constructor inputs.

        Raises:
            ValueError: With descriptive message for invalid inputs
        """
        if face_value <= 0:
            raise ValueError(f"face_value must be positive, got {face_value}")

        if coupon_rate < 0:
            raise ValueError(f"coupon_rate cannot be negative, got {coupon_rate}")

        if not isinstance(years_to_maturity, int) or years_to_maturity <= 0:
            raise ValueError(
                f"years_to_maturity must be a positive integer, got {years_to_maturity}"
            )

        # Allow negative yields (modern market reality)
        if yield_to_maturity <= -1:
            raise ValueError(
                f"yield_to_maturity must be greater than -1, got {yield_to_maturity}"
            )

        if payments_per_year not in (1, 2, 4, 12):
            raise ValueError(
                f"payments_per_year must be 1, 2, 4, or 12, got {payments_per_year}"
            )

    def _generate_cash_flows(self) -> List[Tuple[int, float]]:
        """
        Generate the bond's cash flow schedule.

        Returns:
            List of tuples: [(period_number, cash_flow_amount), ...]
            where period_number is 1, 2, ..., total_periods
        """
        cash_flows = []

        for t in range(1, self.total_periods + 1):
            if t == self.total_periods:
                # Final period: coupon + principal repayment
                cf = self.periodic_coupon + self.face_value
            else:
                # Regular period: coupon only
                cf = self.periodic_coupon
            cash_flows.append((t, cf))

        return cash_flows

    def price(self) -> float:
        """
        Calculate the bond's theoretical price.

        The price equals the present value of all future cash flows,
        discounted at the yield to maturity.

        Formula:
            P = Σ [CF_t / (1 + y)^t]

            where:
                CF_t = cash flow at period t
                y = periodic yield (annual yield / payments per year)
                t = period number

        Returns:
            Bond price in same currency units as face_value

        Example:
            >>> bond = Bond(1000, 0.06, 5, 0.08, 1)
            >>> bond.price()
            920.1458...
        """
        total_pv = 0.0

        for t, cf in self._generate_cash_flows():
            # PV = CF / (1 + y)^t
            discount_factor = (1 + self.periodic_yield) ** t
            total_pv += cf / discount_factor

        return total_pv

    def macaulay_duration(self) -> float:
        """
        Calculate Macaulay Duration.

        Macaulay Duration is the weighted average time to receive the bond's
        cash flows. The weights are the present values of each cash flow
        as a proportion of the bond's price.

        Formula:
            D_mac = Σ [t × PV(CF_t)] / Price

            where:
                t = time in years to cash flow
                PV(CF_t) = present value of cash flow at time t

        Returns:
            Duration in years

        Interpretation:
            - For a zero-coupon bond, duration equals maturity
            - Higher duration = greater sensitivity to interest rate changes
            - Can be thought of as the bond's "effective maturity"
        """
        bond_price = self.price()
        weighted_sum = 0.0

        for t, cf in self._generate_cash_flows():
            # Present value of this cash flow
            pv = cf / ((1 + self.periodic_yield) ** t)

            # Weight by time (in periods)
            weighted_sum += t * pv

        # Duration in periods, convert to years
        duration_in_periods = weighted_sum / bond_price
        return duration_in_periods / self.payments_per_year

    def modified_duration(self) -> float:
        """
        Calculate Modified Duration.

        Modified Duration measures the percentage change in bond price
        for a 1% (100 basis point) change in yield. It adjusts Macaulay
        Duration for the compounding effect.

        Formula:
            D_mod = D_mac / (1 + y/m)

            where:
                D_mac = Macaulay Duration
                y = annual yield to maturity
                m = payments per year

        Returns:
            Modified duration (dimensionless sensitivity measure)

        Interpretation:
            - If D_mod = 4.5, a 1% yield increase causes ~4.5% price decrease
            - First-order (linear) approximation of price sensitivity
            - Negative relationship: yields up → prices down

        Example:
            >>> bond = Bond(1000, 0.06, 5, 0.08, 1)
            >>> bond.modified_duration()
            4.1104...
        """
        return self.macaulay_duration() / (1 + self.periodic_yield)

    def convexity(self) -> float:
        """
        Calculate bond convexity.

        Convexity measures the curvature of the price-yield relationship.
        It captures the second-order effect that duration (linear) misses,
        improving price change estimates for larger yield movements.

        Formula:
            Convexity = [Σ CF_t × t × (t+1) / (1+y)^(t+2)] / (P × m²)

            where:
                CF_t = cash flow at period t
                y = periodic yield
                P = bond price
                m = payments per year

        Returns:
            Convexity in years squared

        Interpretation:
            - Always positive for option-free bonds (beneficial property)
            - Higher convexity means:
                * Larger price gains when yields fall
                * Smaller price losses when yields rise
            - Convexity effect becomes significant for yield changes > 100bp

        Example:
            >>> bond = Bond(1000, 0.06, 5, 0.08, 1)
            >>> bond.convexity()
            21.9107...
        """
        bond_price = self.price()
        convexity_sum = 0.0

        for t, cf in self._generate_cash_flows():
            # Discount factor for convexity: (1+y)^(t+2)
            discount = (1 + self.periodic_yield) ** (t + 2)
            convexity_sum += cf * t * (t + 1) / discount

        # Normalize by price and convert from periods² to years²
        return convexity_sum / (bond_price * (self.payments_per_year ** 2))

    def price_change_estimate(self, yield_change: float) -> Tuple[float, float, float]:
        """
        Estimate percentage price change using duration and convexity.

        This implements the Taylor series approximation for bond price changes,
        combining the first-order (duration) and second-order (convexity) effects.

        Formula:
            ΔP/P ≈ -D_mod × Δy + 0.5 × Convexity × (Δy)²

            where:
                D_mod = Modified Duration
                Δy = change in yield (as decimal)

        Args:
            yield_change: Change in yield as decimal (e.g., 0.01 for +100bp,
                         -0.005 for -50bp)

        Returns:
            Tuple containing:
                - total_change: Total estimated percentage price change
                - duration_effect: Contribution from duration (first-order)
                - convexity_effect: Contribution from convexity (second-order)

        Example:
            >>> bond = Bond(1000, 0.06, 5, 0.08, 1)
            >>> total, dur_eff, conv_eff = bond.price_change_estimate(0.01)
            >>> print(f"Total: {total*100:.2f}%")
            Total: -4.00%
            >>> print(f"Duration effect: {dur_eff*100:.2f}%")
            Duration effect: -4.11%
            >>> print(f"Convexity effect: {conv_eff*100:.2f}%")
            Convexity effect: +0.11%

        Note:
            - Duration effect is always opposite to yield change direction
            - Convexity effect is always positive (beneficial for bondholders)
            - Approximation accuracy decreases for very large yield changes
        """
        d_mod = self.modified_duration()
        conv = self.convexity()

        # First-order effect (linear, from duration)
        duration_effect = -d_mod * yield_change

        # Second-order effect (curvature, from convexity)
        convexity_effect = 0.5 * conv * (yield_change ** 2)

        # Total percentage price change
        total_change = duration_effect + convexity_effect

        return total_change, duration_effect, convexity_effect

    def summary(self) -> str:
        """
        Generate a formatted summary of all bond analytics.

        Returns:
            Multi-line string with bond details and calculated metrics
        """
        total_chg, dur_eff, conv_eff = self.price_change_estimate(0.01)

        return f"""
{'='*50}
BOND SUMMARY
{'='*50}

TERMS:
  Face Value:           ${self.face_value:,.2f}
  Coupon Rate:          {self.coupon_rate*100:.3f}%
  Years to Maturity:    {self.years_to_maturity}
  Payments per Year:    {self.payments_per_year}

VALUATION:
  Yield to Maturity:    {self.yield_to_maturity*100:.3f}%
  Price:                ${self.price():,.4f}
  Price (per 100):      {(self.price()/self.face_value)*100:.4f}

RISK METRICS:
  Macaulay Duration:    {self.macaulay_duration():.4f} years
  Modified Duration:    {self.modified_duration():.4f}
  Convexity:            {self.convexity():.4f}

SENSITIVITY (for +100bp yield change):
  Duration Effect:      {dur_eff*100:+.4f}%
  Convexity Effect:     {conv_eff*100:+.4f}%
  Total Price Change:   {total_chg*100:+.4f}%

{'='*50}
"""
