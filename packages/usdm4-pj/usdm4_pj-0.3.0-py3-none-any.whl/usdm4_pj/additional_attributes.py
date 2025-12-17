from simple_error_log.errors import Errors
from .data_file import DataFile


class AdditionalAttributes:
    def __init__(self, filepath, errors: Errors) -> None:
        self._filepath = filepath
        self._errors = errors
        self._data = None

    def process(self) -> None:
        df = DataFile(self._filepath, self._errors)
        raw_data = df.read()
        self._data = {}
        k: str
        for k, v in raw_data.items():
            self._data[k.upper()] = v

    def attributes(self, name: str) -> dict | None:
        name_u = name.upper()
        if name_u in self._data:
            return self._data[name_u]
        return None
