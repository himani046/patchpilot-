from typing import TypedDict


class PatchPilotState(TypedDict, total=False):
    investigation_id: str
    workspace: str
    original_test_output: str
    current_test_output: str
    failure_report: dict
    repair_plan: dict
    patch: dict
    changed_files: list[str]
    attempts: int
    max_attempts: int
    verification_passed: bool
    status: str
    events: list[dict]
