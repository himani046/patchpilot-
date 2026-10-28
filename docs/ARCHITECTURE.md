# PatchPilot architecture

1. Accept a bounded ZIP archive and validate paths, symlinks, entry count and expanded size before manual extraction.
2. Scan supported source files and run baseline pytest in Docker.
3. Nemotron-backed triage emits validated `FailureReport` JSON.
4. Planning emits a validated `RepairPlan`; coding emits structured replacements for approved existing files.
5. The patcher validates all paths; Docker executes tests with networking disabled, resource limits, dropped capabilities and a read-only image filesystem.
6. Verification trusts actual process exit code and timeout state, not an LLM claim.

Logical agent roles are triage, root-cause/planning, coding, and verification. They may share one model endpoint. Test execution, path validation, and exit-code checks are deterministic code.

Before public deployment, move execution to an isolated worker queue, use fresh workspaces per attempt, preserve baseline code, generate diffs, implement evidence-driven retries, add authentication/rate limits/database persistence, disk quotas and cancellation, and expose asynchronous status/event APIs.
