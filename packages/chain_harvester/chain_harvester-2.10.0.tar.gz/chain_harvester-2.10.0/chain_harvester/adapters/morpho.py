from chain_harvester.constants import SECONDS_PER_YEAR
from chain_harvester.utils.solidity_math import MathLib, from_wad, to_wad


class AdaptiveCurveIrm:
    """
    Copied over with minor adjustments: https://github.com/morpho-org/adaptive-curve-irm-py
    """

    WAD = MathLib.WAD
    SECONDS_PER_YEAR = 365 * 24 * 60 * 60

    def __init__(self, last_update=0):
        # Constants (converted to %/year)
        self.CURVE_STEEPNESS = 4 * self.WAD
        self.ADJUSTMENT_SPEED = 50 * self.WAD // self.SECONDS_PER_YEAR
        self.TARGET_UTILIZATION = 9 * self.WAD // 10
        self.INITIAL_RATE_AT_TARGET = 4 * self.WAD // 100 // self.SECONDS_PER_YEAR
        self.MIN_RATE_AT_TARGET = self.WAD // 1000 // self.SECONDS_PER_YEAR
        self.MAX_RATE_AT_TARGET = 2 * self.WAD // self.SECONDS_PER_YEAR

        # State variables
        self.rate_at_target = 0
        self.last_update = last_update

        # Memoization list for borrow rates and current time
        self.memoized_rates = []

    def borrow_rate(
        self,
        total_borrow_assets,
        total_supply_assets,
        current_time,
        rate_at_target=None,
    ):
        """
        Calculate the borrow rate based on the current state of the market.

        Args:
            total_borrow_assets (int): Total borrowed assets in WAD (1 WAD = 10^18).
            total_supply_assets (int): Total supplied assets in WAD.
            current_time (int): Current timestamp in seconds.
            rate_at_target (int, optional): Custom rate at target utilization in WAD per second.
                                            If None, uses the internal state.

        Returns:
            tuple: A tuple containing:
                - int: The calculated borrow rate in WAD per second.
                - int: The updated rate at target utilization in WAD per second.

        Note:
            All input values (except current_time) and the return value are in WAD units.
            The current_time is in seconds.
        """
        utilization = (
            MathLib.w_div_down(total_borrow_assets, total_supply_assets)
            if total_supply_assets > 0
            else 0
        )

        err_norm_factor = (
            (self.WAD - self.TARGET_UTILIZATION)
            if utilization > self.TARGET_UTILIZATION
            else self.TARGET_UTILIZATION
        )
        err = MathLib.w_div_to_zero(utilization - self.TARGET_UTILIZATION, err_norm_factor)

        start_rate_at_target = rate_at_target if rate_at_target else self.rate_at_target

        if start_rate_at_target == 0:
            avg_rate_at_target = self.INITIAL_RATE_AT_TARGET
            end_rate_at_target = self.INITIAL_RATE_AT_TARGET
        else:
            speed = MathLib.w_mul_to_zero(self.ADJUSTMENT_SPEED, err)
            elapsed = current_time - self.last_update
            linear_adaptation = speed * elapsed

            if linear_adaptation == 0:
                avg_rate_at_target = start_rate_at_target
                end_rate_at_target = start_rate_at_target
            else:
                end_rate_at_target = self._new_rate_at_target(
                    start_rate_at_target, linear_adaptation
                )
                mid_rate_at_target = self._new_rate_at_target(
                    start_rate_at_target, linear_adaptation // 2
                )
                avg_rate_at_target = (
                    start_rate_at_target + end_rate_at_target + 2 * mid_rate_at_target
                ) // 4

        self.rate_at_target = end_rate_at_target
        self.last_update = current_time

        rate = self._curve(avg_rate_at_target, err)

        # Memoize the borrow rate and current time
        self.memoized_rates.append((current_time, rate))

        return rate, self.rate_at_target

    def _curve(self, rate_at_target, err):
        coeff = (
            self.WAD - MathLib.w_div_to_zero(self.WAD, self.CURVE_STEEPNESS)
            if err < 0
            else self.CURVE_STEEPNESS - self.WAD
        )
        return MathLib.w_mul_to_zero(MathLib.w_mul_to_zero(coeff, err) + self.WAD, rate_at_target)

    def _new_rate_at_target(self, start_rate_at_target, linear_adaptation):
        new_rate = MathLib.w_mul_to_zero(start_rate_at_target, self._w_exp(linear_adaptation))
        return max(min(new_rate, self.MAX_RATE_AT_TARGET), self.MIN_RATE_AT_TARGET)

    def _w_exp(self, x):
        LN_2_INT = 693147180559945309  # ln(2) * WAD
        LN_WEI_INT = -41446531673892822312  # ln(1e-18) * WAD
        # ln(type(int256).max / 1e36) * WAD
        WEXP_UPPER_BOUND = 93859467695000404319
        # wExp(WEXP_UPPER_BOUND)
        WEXP_UPPER_VALUE = 57716089161558943949701069502944508345128422502756744429568

        if x < LN_WEI_INT:
            return 0
        if x >= WEXP_UPPER_BOUND:
            return WEXP_UPPER_VALUE

        rounding_adjustment = -LN_2_INT // 2 if x < 0 else LN_2_INT // 2
        q = (x + rounding_adjustment) // LN_2_INT
        r = x - q * LN_2_INT

        exp_r = self.WAD + r + (r * r) // self.WAD // 2

        if q >= 0:
            return exp_r << q
        else:
            return exp_r >> (-q)


def calculate_morpho_apr(
    total_borrow_assets, total_supply_assets, last_update=0, current_time=0, rate_at_target=None
):
    """
    Calculate the Annual Percentage Rate (APR) for Morpho protocol.

    This function uses the AdaptiveCurveIrm to calculate the borrow rate and converts it to
    an annual rate.

    To get most similar behaviur to the one in the contract (https://github.com/morpho-org/morpho-blue-irm/blob/4f09910c8d13700d2a9e160847cd34c02717be72/src/adaptive-curve-irm/AdaptiveCurveIrm.sol#L76)
    you must pass last_update, current_time and rate_at_target values.

    Args:
        total_borrow_assets (Decimal): The total amount of borrowed assets.
        total_supply_assets (Decimal): The total amount of supplied assets.
        last_update (int, optional): The timestamp of the last update. Defaults to 0.
        current_time (int, optional): The current timestamp. Defaults to 0.
        rate_at_target (Decimal, optional): The target rate. Defaults to None.

    Returns:
        tuple: A tuple containing two elements:
            - Decimal: The calculated APR as a decimal (e.g., 0.05 for 5% APR).
            - Decimal: The new rate at target.
    """
    irm = AdaptiveCurveIrm(last_update)
    borrow_rate_lib_apr, new_rate_at_target = irm.borrow_rate(
        int(to_wad(total_borrow_assets)),
        int(to_wad(total_supply_assets)),
        current_time=current_time,
        rate_at_target=int(to_wad(rate_at_target)) if rate_at_target else None,
    )
    return from_wad(borrow_rate_lib_apr) * SECONDS_PER_YEAR, from_wad(new_rate_at_target)
