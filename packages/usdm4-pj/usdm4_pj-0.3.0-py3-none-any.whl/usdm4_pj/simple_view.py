import json
from .additional_attributes import AdditionalAttributes
from .procedure_costs import ProcedureCosts
from simple_error_log.errors import Errors
from usdm4 import Wrapper
from usdm4.api.study_design import StudyDesign
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4.api.scheduled_instance import ScheduledActivityInstance
from usdm4.api.activity import Activity
from usdm4.api.timing import Timing
from simple_error_log.error_location import KlassMethodLocation


class SimpleView:
    MODULE: str = "src.usdm4_pj.expanded_view.SimpleView"

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
        self._visits = None

    def process(self, study_design_id: str) -> None:
        visits = []

        sd: StudyDesign
        _, _, sd = self._wrapper.study_version_and_design(study_design_id)
        if sd:
            all_activities = sd.activity_list()

            #
            timeline: ScheduleTimeline = sd.main_timeline()
            if timeline:
                for e in sd.encounters:
                    timepoints = []
                    for tp in timeline.instances:
                        if isinstance(tp, ScheduledActivityInstance):
                            tp: ScheduledActivityInstance
                            if tp.encounterId:
                                if tp.encounterId == e.id:
                                    timepoints.append(tp)
                    fixed_activities = []
                    if timepoints:
                        timepoint: ScheduledActivityInstance
                        for timepoint in timepoints:
                            activityIds = [y for y in timepoint.activityIds]
                            activities = [
                                x for x in all_activities if x.id in activityIds
                            ]
                            fixed_activities = self._get_activities(activities)
                            visit = {}
                            visit["title"] = f"{timepoint.label}"
                            visit["notes"] = ",".join(e.notes)
                            visit["type"] = ",".join([x.decode for x in e.contactModes])
                            timing = timeline.find_timing_from(timepoint.id)
                            # print(f"TIMING: {timing}, {type(timing)}")
                            if timing:
                                visit["timing"] = self._make_timing_text(
                                    timeline, timepoint, timing
                                )
                                visit["duration"] = timing.value
                            else:
                                visit["timing"] = "none"
                                visit["duration"] = "none"
                            visit["activities"] = fixed_activities
                            visits.append(visit)
                    else:
                        self._errors.info(
                            f"Encounter '{e.id}' does not have timepoints",
                            KlassMethodLocation(self.MODULE, "process"),
                        )
                self._visits = visits
            else:
                self._errors.error(
                    f"No main timeline found for study design with id '{study_design_id}'",
                    KlassMethodLocation(self.MODULE, "process"),
                )
        else:
            self._errors.error(
                f"No study design found with id '{study_design_id}'",
                KlassMethodLocation(self.MODULE, "process"),
            )

    def add_additional(self, attributes: AdditionalAttributes):
        # print(f"ADD ADDITIONAL: {attributes}")
        if attributes is None:
            return
        if self._visits:
            node: dict
            for node in self._visits:
                activity: dict
                for activity in node["activities"]:
                    additional = attributes.attributes(activity["title"])
                    # print(f"ADDITIONAL: {additional}")
                    if additional:
                        for k, v in additional.items():
                            activity[k] = v

    def to_json(self) -> str:
        return json.dumps({"visits": self._visits if self._visits else []}, indent=4)

    def _make_timing_text(
        self,
        timeline: ScheduleTimeline,
        timepoint: ScheduledActivityInstance,
        timing: Timing,
    ):
        to_timepoint: ScheduledActivityInstance = timeline.find_timing_to(timepoint.id)
        direction = timing.type.decode
        relation = timing.relativeToFrom.decode
        if direction == "Before":
            timing_txt = f"'{direction}'  '{timepoint.label}'  '{relation}'"
        else:
            timing_txt = f"'{direction}'  '{to_timepoint.label if to_timepoint else ''}'  '{relation}'"
        return timing_txt

    def _get_activities(self, activities):
        items = []
        activity: Activity
        for activity in activities:
            item = {}
            item["title"] = activity.label
            item["procedures"] = (
                [x.label for x in activity.definedProcedures]
                if activity.definedProcedures
                else []
            )
            item["notes"] = ",".join(activity.notes)
            items.append(item)
        return items
