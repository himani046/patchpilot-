from typing import Literal

from pydantic import BaseModel, Field


class FailureReport(BaseModel):
    summary: str
    category: Literal["logic", "dependency", "configuration", "syntax", "test", "unknown"]
    failing_tests: list[str] = Field(default_factory=list)
    error_messages: list[str] = Field(default_factory=list)
    affected_files: list[str] = Field(default_factory=list)


class RepairPlan(BaseModel):
    root_cause: str
    reasoning: str
    files_to_change: list[str]
    proposed_changes: list[str]
    risks: list[str] = Field(default_factory=list)


class FileChange(BaseModel):
    path: str
    content: str


class RepairPatch(BaseModel):
    changes: list[FileChange]


class VerificationReport(BaseModel):
    passed: bool
    exit_code: int | None
    summary: str
    failing_tests: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class InvestigationResult(BaseModel):
    investigation_id: str
    status: str
    failure: FailureReport | None = None
    repair_plan: RepairPlan | None = None
    changed_files: list[str] = Field(default_factory=list)
    verification: VerificationReport | None = None
    attempts: int = 0
    events: list[dict] = Field(default_factory=list)
