from simple_error_log.errors import Errors
from .data_file import DataFile


class ProcedureCosts:
    def __init__(self, filepath, errors: Errors) -> None:
        self._filepath = filepath
        self._errors = errors
        self._data = None

    def process(self) -> None:
        df = DataFile(self._filepath, self._errors)
        raw_data = df.read()
        self._data = {}
        self._data = {
            "visit": raw_data["visit"],
            "activities": {k.upper(): v for k, v in raw_data["activities"].items()},
        }

    def visit(self) -> dict:
        if self._data:
            return self._data["visit"] if "visit" in self._data else self._no_costs()
        return self._no_costs()

    def activity(self, name: str) -> dict:
        u_name = name.upper()
        if self._data:
            if "activities" in self._data:
                return (
                    self._data["activities"][u_name]
                    if u_name in self._data["activities"]
                    else self._no_costs()
                )
            return self._no_costs
        return self._no_costs()

    @classmethod
    def zero_cost(cls) -> dict:
        return cls._no_costs()

    def add_costs(self, a: dict, b: dict) -> dict:
        items = [
            "burden_cost_no_overhead",
            "burden_cost_overhead",
            "burden_participant_time",
            "burden_site_time",
        ]
        result = self._no_costs()
        for item in items:
            result[item] = a[item] + b[item]
        return result

    @staticmethod
    def _no_costs():
        return {
            "burden_cost_no_overhead": 0,
            "burden_cost_overhead": 0,
            "burden_participant_time": 0,
            "burden_site_time": 0,
        }
