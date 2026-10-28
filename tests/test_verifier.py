from app.agents.verifier import verify_repair

def test_verifier_uses_actual_exit_code():
    assert verify_repair({"passed": True,"exit_code": 0,"timed_out": False,"output": "","duration_seconds": 0.1}).passed

def test_verifier_rejects_timeout_even_with_zero_exit_code():
    assert not verify_repair({"passed": True,"exit_code": 0,"timed_out": True,"output": "","duration_seconds": 30}).passed
