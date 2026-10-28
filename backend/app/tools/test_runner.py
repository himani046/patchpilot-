import subprocess, time
from pathlib import Path
from app.config import settings
def run_tests(workspace: str) -> dict:
    root = Path(workspace).resolve()
    if not root.is_dir(): raise ValueError("Workspace does not exist.")
    command = ["docker","run","--rm","--network=none","--memory=512m","--cpus=1","--pids-limit=128","--read-only","--cap-drop=ALL","--security-opt=no-new-privileges","--tmpfs=/tmp:rw,noexec,nosuid,size=64m","--mount",f"type=bind,source={root},target=/workspace,rw","--workdir=/workspace","patchpilot-runner:latest","python","-m","pytest","-q","--tb=short"]
    start = time.monotonic()
    try:
        result = subprocess.run(command,capture_output=True,text=True,timeout=settings.max_test_seconds,check=False)
        return {"passed":result.returncode==0,"exit_code":result.returncode,"output":(result.stdout+"\n"+result.stderr)[-20000:],"duration_seconds":round(time.monotonic()-start,2),"timed_out":False}
    except subprocess.TimeoutExpired:
        return {"passed":False,"exit_code":None,"output":"Test execution exceeded the time limit.","duration_seconds":settings.max_test_seconds,"timed_out":True}
    except FileNotFoundError as exc: raise RuntimeError("Docker CLI is unavailable to the backend worker.") from exc
