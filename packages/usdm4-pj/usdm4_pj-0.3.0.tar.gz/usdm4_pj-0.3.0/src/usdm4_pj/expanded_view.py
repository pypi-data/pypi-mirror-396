import json
from .additional_attributes import AdditionalAttributes
from .procedure_costs import ProcedureCosts
from simple_error_log.errors import Errors
from usdm4 import Wrapper
from usdm4.expander.expander import Expander
from usdm4.api.study_design import StudyDesign
from simple_error_log.error_location import KlassMethodLocation


class ExpandedView:
    MODULE: str = "src.usdm4_pj.expanded_view.ExpandedView"

    def __init__(
        self,
        wrapper: Wrapper,
        errors: Errors,
        attributes: AdditionalAttributes,
        costs: ProcedureCosts,
    ) -> None:
        self._wrapper = wrapper
        self._errors = errors
        self._attributes = attributes
        self._costs = costs
        self._expander = None
        self._nodes = None
        self._total_cost = ProcedureCosts.zero_cost()

    def process(self, study_design_id: str) -> dict | None:
        sd: StudyDesign
        _, _, sd = self._wrapper.study_version_and_design(study_design_id)
        if sd:
            self._expander = Expander(sd, sd.main_timeline(), self._errors)
            self._expander.process()
            self._nodes = [x.to_dict() for x in self._expander.nodes]
        else:
            self._errors.error(
                f"Cannot find study design with id '{study_design_id}'",
                KlassMethodLocation(self.MODULE, "process"),
            )

    def add_additional(self, attributes: AdditionalAttributes):
        # print(f"ADD ADDITIONAL: {attributes}")
        if attributes is None:
            return
        if self._nodes:
            node: dict
            for node in self._nodes:
                activity: dict
                for activity in node["activities"]["items"]:
                    additional = attributes.attributes(activity["label"])
                    # print(f"ADDITIONAL: {additional}")
                    if additional:
                        for k, v in additional.items():
                            activity[k] = v

    def caculate_costs(self, costs: ProcedureCosts):
        # print(f"COSTS: {costs}")
        total = ProcedureCosts.zero_cost()
        if self._nodes:
            node: dict
            for node in self._nodes:
                if node["encounter"]:
                    if costs:
                        node["costs"] = costs.visit()
                        total = costs.add_costs(total, node["costs"])
                    else:
                        node["costs"] = ProcedureCosts.zero_cost()
                else:
                    node["costs"] = ProcedureCosts.zero_cost()
                for activity in node["activities"]["items"]:
                    if costs:
                        activity["costs"] = costs.activity(activity["label"])
                        total = costs.add_costs(total, activity["costs"])
                    else:
                        activity["costs"] = ProcedureCosts.zero_cost()
        self._total_cost = total

    def to_json(self) -> str:
        if self._nodes:
            result = {"nodes": self._nodes, "cost": self._total_cost}
            return json.dumps(result, indent=4)
        else:
            self._errors.warning(
                "No nodes detected", KlassMethodLocation(self.MODULE, "to_json")
            )
            return json.dumps({"nodes": [], "costs": ProcedureCosts.zero_cost()})
