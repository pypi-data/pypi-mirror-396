from decimal import Decimal


class RateUtils:

    @staticmethod
    def percent_to_bps(percent: str | float | Decimal) -> int:
        """
        Convert a percent to basis points (bps).
        e.g., 2.9 -> 290 bps
        """
        return int(Decimal(str(percent)) * Decimal(100))

    @staticmethod
    def bps_to_percent(bps: int) -> Decimal:
        """
        Convert basis points (bps) to a percent value.
        e.g., 290 -> Decimal('2.9')
        """
        return Decimal(bps) / Decimal(100)

    @staticmethod
    def fee_from_rate_bps(amount_cents: int, rate_bps: int) -> int:
        """
        Compute the fee (in cents) from an amount (in cents) and a rate in bps.
        Uses integer arithmetic with half-up rounding to the nearest cent.
        """
        if amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        return (amount_cents * rate_bps + 5_000) // 10_000