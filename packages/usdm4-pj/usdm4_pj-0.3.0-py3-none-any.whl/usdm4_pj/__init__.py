from usdm4 import USDM4
from .simple_view import SimpleView
from .expanded_view import ExpandedView
from .procedure_costs import ProcedureCosts
from .additional_attributes import AdditionalAttributes
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class USDM4PJ:
    MODULE: str = "src.usdm4_pj.__init__.USDM4PJ"

    def __init__(self, errors: Errors) -> None:
        self._errors = errors
        self._costs = None
        self._activities = None

    def simple_view(
        self,
        usdm_filepath: str,
        study_design_id: str,
        activities_file_path: str = None,
        costs_file_path: str = None,
    ) -> str:
        try:
            self._load_info(usdm_filepath, activities_file_path, costs_file_path)
            sv = SimpleView(self._wrapper, self._errors, self._activities, self._costs)
            sv.process(study_design_id)
            sv.add_additional(self._activities)
            return sv.to_json()
        except Exception as e:
            self._errors.exception(
                f"Exception raised creating simple view from usdm4 file '{usdm_filepath}'",
                e,
                location=KlassMethodLocation(self.MODULE, "simple_view"),
            )
            return None

    def expanded_view(
        self,
        usdm_filepath: str,
        study_design_id: str,
        activities_file_path: str = None,
        costs_file_path: str = None,
    ) -> str:
        try:
            self._load_info(usdm_filepath, activities_file_path, costs_file_path)
            ev = ExpandedView(
                self._wrapper, self._errors, self._activities, self._costs
            )
            ev.process(study_design_id)
            ev.caculate_costs(self._costs)
            ev.add_additional(self._activities)
            return ev.to_json()
        except Exception as e:
            self._errors.exception(
                f"Exception raised creating expanded view from usdm4 file '{usdm_filepath}'",
                e,
                location=KlassMethodLocation(self.MODULE, "expanded_view"),
            )
            return None

    def _load_info(
        self, usdm_filepath: str, activities_file_path: str, costs_file_path: str
    ) -> None:
        usdm4: USDM4 = USDM4()
        self._wrapper = usdm4.load(usdm_filepath, self._errors)
        if costs_file_path:
            self._costs = ProcedureCosts(costs_file_path, self._errors)
            self._costs.process()
        if activities_file_path:
            self._activities = AdditionalAttributes(activities_file_path, self._errors)
            self._activities.process()
