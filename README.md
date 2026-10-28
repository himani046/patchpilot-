# PatchPilot — Autonomous CI Failure Investigation & Repair

PatchPilot is an AI software-engineering agent that reproduces CI failures, investigates likely root causes with NVIDIA Nemotron through Nebius Token Factory, proposes code patches, and verifies them with real tests in a restricted Docker container.

## Current MVP
- FastAPI API with ZIP upload and health endpoint
- Nemotron-powered triage, root-cause planning, and code generation
- Path-validated patcher and pytest sandbox runner
- React/Vite dashboard with investigation events and verification status
- Broken billing demo fixture and basic tests

This is a hackathon scaffold and has **not been run end-to-end in this environment**. Review `docs/SECURITY.md` before any public deployment. The current upload endpoint executes a workflow synchronously and is not suitable for arbitrary public uploads without moving execution into a dedicated sandbox worker host.

## Requirements
- Python 3.11+
- Node.js 20+
- Docker available to the backend worker
- Nebius Token Factory API access and an available NVIDIA Nemotron model

## Backend setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r backend/requirements.txt
cp .env.example .env       # add your real NEBIUS_API_KEY locally
```

Build the sandbox image from the repository root:

```bash
docker build -f backend/sandbox.Dockerfile -t patchpilot-runner:latest .
```

Start the API:

```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

Health check: `http://127.0.0.1:8000/api/health`.

## Frontend setup

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Optional: create `frontend/.env` using `frontend/.env.example` and set `VITE_API_BASE_URL` if the backend URL differs. Never put API keys in frontend environment variables.

## Nebius / Nemotron

The backend uses the OpenAI-compatible Token Factory API. Check the current model catalog and account access before relying on `NEBIUS_MODEL`; identifiers can change. Start with a real smoke test:

```bash
cd backend
PYTHONPATH=. python test_nebius.py
```

Docs: https://api.tokenfactory.nebius.com/docs

## Safety and known gaps

- Uploaded repositories are untrusted; the included Docker restrictions are a baseline, not a full container security guarantee.
- Never mount the Docker socket, host credentials, or API keys into project containers.
- The MVP supports simple Python/pytest projects; it does not install arbitrary project dependencies.
- Each repair attempt uses a fresh copy; the uploaded original is not modified.
- Passing tests is evidence only for the tests that actually ran, not proof of universal correctness.
- Add authentication, rate limits, background workers, durable persistence, streaming statuses, and stronger isolation before a public multi-user deployment.

See `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, and `docs/EVALUATION.md`.

## License
MIT — see `LICENSE`.
