from app.schemas import VerificationReport
def verify_repair(test_result: dict) -> VerificationReport:
    passed = test_result.get("exit_code") == 0 and test_result.get("passed") is True and not test_result.get("timed_out", False)
    output = test_result.get("output", "")
    failing = [line.strip() for line in output.splitlines() if "FAILED " in line]
    summary = "The executed test suite passed." if passed else ("Verification timed out." if test_result.get("timed_out") else "The test suite did not pass.")
    return VerificationReport(passed=passed, exit_code=test_result.get("exit_code"), summary=summary, failing_tests=failing, duration_seconds=test_result.get("duration_seconds", 0.0))
