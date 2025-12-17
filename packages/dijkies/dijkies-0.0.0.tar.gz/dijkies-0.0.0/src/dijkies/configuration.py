import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, model_validator


class Configuration(BaseModel):

    # initialization
    name: str
    id: str = str(uuid.uuid4())
    start_investment_base: float = 0
    start_investment_quote: float = 0
    base: str
    start_base_price: float
    start_time: datetime = datetime.now(tz=timezone.utc)

    # metrics

    risk_free_rate_per_year: float
    candle_interval_in_minutes: int

    # exchange_settings

    fee_market_order: float
    fee_limit_order: float

    @property
    def initialization_value_in_quote(self) -> float:
        base_value = self.start_investment_base * self.start_base_price
        return self.start_investment_quote + base_value

    @model_validator(mode="after")
    def validate(self) -> "Configuration":
        assert self.fee_market_order > self.fee_limit_order
        assert (
            min(
                [
                    self.start_investment_base,
                    self.start_investment_quote,
                    self.start_base_price,
                    self.risk_free_rate_per_year,
                ]
            )
            > 0
        )

        return self
