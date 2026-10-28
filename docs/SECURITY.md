# Security considerations

PatchPilot executes untrusted source code. Docker limits are a baseline, not a complete protection against all container escapes.

- Never execute uploaded tests inside the API process or host shell.
- Never mount the Docker socket, host root, developer home, credentials or Nebius API key into project containers.
- Disable sandbox networking and enforce CPU, memory, PID, disk and wall-clock limits.
- Validate ZIP paths, reject symlinks and limit compressed size, expanded size, entry count and individual file size.
- Use disposable isolated workspaces and treat source/log text as untrusted prompt input.
- Keep model keys server-side; never put secrets in `VITE_*` variables.
- Require human review before publishing patches.
- Add authentication, request throttling, hardened worker isolation, audit logs and monitoring before public deployment.
