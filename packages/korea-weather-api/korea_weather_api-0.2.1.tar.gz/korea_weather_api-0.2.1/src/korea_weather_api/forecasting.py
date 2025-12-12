from datetime import datetime
from typing import Optional

from .base import BaseApi


class Forecasting(BaseApi):
    @staticmethod
    def get_short_data():
        pass

    def get_medium_data(
        start_dt: datetime,
        end_dt: datetime,
        effect_start_dt: datetime,
        effect_end_dt: datetime,
        auth_key: str,
        region: Optional[str] = None,
    ):
        params = {
            "mode": "0",
            "disp": "1",
            "help": "0",
            "authKey": auth_key,
        }
