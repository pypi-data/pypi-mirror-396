from pydantic import BaseModel


class RefreshCfg(BaseModel):
    concurrency: int = 4
    buffer: int = 300
    tick: int | float = 60
    max_batch: int = 20
    refresh_timeout: int | float = 30.0
    min_refresh_interval: int | float = 1.0  # Minimum seconds between refresh attempts
