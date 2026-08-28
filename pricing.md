# Pricing: Sandlock

Last updated: 2026-08-28. Source: https://sandlock.io/enterprise.html

## Sandlock (open source)
- Price: $0
- License: Apache-2.0
- Includes: the sandbox core, CLI, Python SDK, Rust API, Go SDK, OCI runtime (sandlock-oci), MCP server, copy-on-write, HTTP ACL, credential injection, extension handlers
- Limits: none. No seat, node, or usage cap. No telemetry, no registration, no commercial relationship required at any scale.
- Install: https://sandlock.io/docs/getting-started.html

## Sandbox HTTP API (commercial)
- Price: annual license, sized to the fleet; quote on request
- Deployment: your cloud account or your data center. No hosted or shared-tenant option.
- Includes: HTTP API and client SDKs over the open-source core; sandboxes with stable IDs that persist across runs; container images as rootfs; named checkpoints and restore; long-running service processes; remote MCP transports; scoped API keys with per-key usage accounting
- Limits: per deployment; unlimited sandboxes and API keys within it

## Sandbox Scheduler (commercial)
- Price: annual license, priced by node count; quote on request
- Deployment: your cloud account or your data center
- Includes: placement of sandboxes across a fleet using checkpoint and restore, so a node holds memory only for the duration of a call
- Limits: per deployment

## Terms common to commercial licenses
- Trial: a pilot on your infrastructure against real traffic precedes any contract
- Support: engineering support and a response SLA included
- Exit: the Apache-2.0 core, SDKs, CLI, OCI runtime, and MCP server remain usable with no license

## Contact
- Email: contact@multikernel.io (include expected node count and peak concurrent sandboxes)
- Technical call: https://calendar.app.google/nc1upkqQoUeoukdD9
