import yaml
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class DataFile:
    MODULE = "usdm4_pj.data_file.DataFile"

    def __init__(self, filepath: str, errors: Errors) -> None:
        self._filepath = filepath
        self._errors = errors

    def read(self) -> dict | None:
        try:
            with open(self._filepath, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self._errors.exception(
                "Exception saving results file",
                e,
                KlassMethodLocation(self.MODULE, "read"),
            )
            return None
