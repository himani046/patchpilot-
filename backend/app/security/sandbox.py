"""Sandbox policy notes.

Untrusted repository code must execute only in a disposable isolated worker.
The Docker runner is a baseline defense, not a complete security boundary.
Never mount host credentials, the Docker socket, or application secrets into
project containers. For public deployment use a dedicated worker host or a
stronger isolation service and apply CPU, memory, PID, disk and wall-clock caps.
"""
