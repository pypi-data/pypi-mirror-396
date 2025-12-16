from typing import Any

from bluer_ugv.README.ugvs.comparison.features.classes import Feature

unlimited_range: int = 999


class RangeFeature(Feature):
    nickname = "range"
    long_name = "شعاع عملکرد عملیاتی"

    @property
    def score_as_str_(self) -> str:
        return f"{self.score} کیلومتر" if self.score != unlimited_range else "نامحدود"
