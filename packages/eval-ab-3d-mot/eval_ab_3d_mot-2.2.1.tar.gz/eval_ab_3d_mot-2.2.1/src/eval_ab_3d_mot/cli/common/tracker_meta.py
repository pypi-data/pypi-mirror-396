"""."""

from pydantic import BaseModel


AUTO = 'auto'


class TrackerMeta(BaseModel):
    threshold: float = 1000.0
    max_age: int = -1
    metric: str = AUTO
    algorithm: str = AUTO
