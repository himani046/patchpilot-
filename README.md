# PatchPilot — Autonomous CI Failure Investigation & Repair

PatchPilot is an AI software-engineering agent that reproduces CI failures, investigates likely root causes with NVIDIA Nemotron through Nebius Token Factory, proposes a minimal patch, and verifies the result by executing tests in an isolated Docker container.

> Hackathon build status: repository scaffold and first vertical slice. Review `docs/SECURITY.md` before exposing this to public uploads. Never commit API keys or secrets.

## Architecture

1. **Triage** — classify a reproducible test failure.
2. **Root-cause / planning** — analyze logs and relevant source files.
3. **Coding** — return structured replacement file contents.
4. **Patch validation** — restrict changes to approved existing files and workspace paths.
5. **Execution** — run pytest inside a resource-limited Docker container with networking disabled.
6. **Verification** — treat test exit status as authoritative; an LLM's claim is not proof.

FastAPI exposes upload and health endpoints. The React/Vite frontend displays an investigation summary, repair plan, and verification status.

## Requirements

- Python 3.11+ for the backend
- Node.js 20+ for the frontend
- Docker available to the backend worker
- Nebius Token Factory API access and a supported NVIDIA Nemotron model

## Local setup

### 1. Configure secrets

Copy `.env.example` to `.env` and add your Token Factory API key. `.env` is ignored by Git. Do not put secrets in frontend variables.

### 2. Backend

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\Activate.ps1
pip install -r backend/requirements.txt
cp .env.example .env            # then edit .env
```

Build the test runner image from the repository root:

```bash
docker build -f backend/sandbox.Dockerfile -t patchpilot-runner:latest .
```

Start the API:

```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

Health check: `http://127.0.0.1:8000/api/health`.

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to the backend URL if it is not `http://127.0.0.1:8000`.

### 4. Confirm Nebius access

Make a real inference call before running a repair. Confirm that `NEBIUS_MODEL` is available for your account. Model availability and identifiers can change; use the current Token Factory catalog. API docs: https://api.tokenfactory.nebius.com/docs

## Safety model and limitations

- Uploaded code is untrusted. Do not execute it in the API process.
- The sandbox uses Docker limits, no network, dropped capabilities and a read-only root filesystem. This is a development baseline, not a guarantee against every container escape.
- Use a dedicated isolated worker/host for public deployments; never mount Docker socket, application secrets, or host credentials into the sandbox.
- Validate ZIP archives before extraction, enforce upload/uncompressed size limits, and isolate each investigation workspace.
- The scaffold focuses on existing Python files and pytest projects. It does not install arbitrary project dependencies automatically.
- Passing tests is not proof of complete correctness; show test results separately from optional code-review findings.
- The initial workflow is synchronous and should be moved to a background worker for production.

## Demo fixture

`tests/fixtures/broken_billing_project/` intentionally contains a discount calculation bug. Use it to demonstrate baseline failure, patch generation, and actual post-patch verification. Do not fake test results in the UI.

## Evaluation

See `docs/EVALUATION.md` for a benchmark plan and `docs/ARCHITECTURE.md` for the workflow design.

## License

MIT — see `LICENSE`.