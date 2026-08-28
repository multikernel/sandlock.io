# Product Marketing Context

**Document version:** v1
**Last updated:** 2026-08-28

## Product Overview
**One-liner:** Sandlock is a lightweight Linux process sandbox that confines untrusted code with kernel-enforced policy, with no root, no container, and no VM.
**What it does:** Sandlock compiles a policy (filesystem, network, IPC, syscalls, resources) into Landlock and seccomp-bpf rules applied to a process before it executes, and runs a small supervisor over seccomp user notification for decisions the kernel cannot make statically (destination IPs, HTTP method and path rules, credential injection, copy-on-write writes, memory caps). Startup overhead is about 5 ms. The commercial layer (Sandbox HTTP API, Sandbox Scheduler) turns single-host sandboxes into a fleet you operate on your own infrastructure.
**Product category:** Sandbox / code execution isolation for AI agents and untrusted workloads (searched as "AI agent sandbox", "Linux sandbox", "code execution sandbox", "container alternative").
**Product type:** Open-core developer infrastructure. Open-source library, CLI, SDKs, OCI runtime, MCP server; licensed self-hosted software on top.
**Business model:** Apache-2.0 core, free at any scale. Annual licenses for the Sandbox HTTP API and Sandbox Scheduler, deployed into the customer's cloud account or data center. No hosted or shared-tenant offering. Pricing sized to fleet (node count, concurrent sandboxes); quote on request.

## Target Audience
**Target companies:** Teams running untrusted code at volume: AI agent platforms, code execution products (notebooks, interpreters, eval harnesses), developer platforms (CI, build services), and security engineering groups approving untrusted execution on shared infrastructure. Typically Series A to public, Linux-native, with a platform or infrastructure team.
**Decision-makers:** Platform / infrastructure engineering leads (champion and technical buyer), security engineering (approver), CTO or VP Engineering (financial buyer for enterprise licenses).
**Primary use case:** Running code the team did not write (model-generated shell commands, third-party scripts, tool plugins, customer submissions) without giving it the machine.
**Jobs to be done:**
- Confine an AI agent's tool calls so a prompt injection cannot reach credentials, the filesystem, or the network.
- Run untrusted CI builds and per-request code execution on shared hosts without per-job VMs or a Docker socket.
- Run thousands of mostly idle agent sessions without paying reserved memory for all of them.
**Use cases:**
- AI agent tool execution and MCP servers with one sandbox per call
- Untrusted CI and build steps
- Per-request code execution and function-as-a-service backends
- Prompt-injection defense via split-trust pipelines and credential injection
- Kubernetes via the OCI runtime (namespace-less, cgroup-less)

## Personas
| Persona | Cares about | Challenge | Value we promise |
|---------|-------------|-----------|------------------|
| Platform engineer (user, champion) | Startup latency, ops simplicity, no root | Containers and microVMs are heavy, need privilege, image builds, and KVM | 5 ms startup, one binary, policy as code, no daemon |
| Security engineer (technical influencer) | Precise, auditable boundary; default deny | Wrappers (chroot, ulimit) are weak; container escapes are hard to explain to auditors | Kernel-enforced allowlists, TOCTOU-safe, posture reports and audit trails |
| Head of infra / CTO (decision maker) | Cost per session, vendor lock-in, data residency | Per-session VM memory bill; hosted sandboxes put customer code on someone else's kernel | Up to 48x sessions per host; runs in your account; Apache-2.0 exit path |
| Finance / procurement (financial buyer) | Predictable cost, no usage surprises | Usage-metered sandbox clouds | Annual license per deployment, no per-call metering |

## Problems & Pain Points
**Core problem:** Teams must run code they cannot trust, and every existing isolation option trades away something they need: containers need privilege and images, microVMs need KVM and cost memory, hosted sandbox clouds take the workload off the team's infrastructure.
**Why alternatives fall short:**
- Containers: root or user namespaces, image builds, ~200 ms startup, shared kernel anyway
- MicroVMs (Firecracker): KVM required, per-VM memory reserved while idle, no HTTP-level policy
- gVisor: syscall-compatibility gaps, throughput cost
- bubblewrap / firejail / chroot / ulimit: no dynamic policy, no HTTP ACL, weak resource control
- Hosted sandbox clouds (E2B, Modal, Vercel Sandbox, Cloudflare): customer code on a vendor kernel, metered pricing, vendor dependency
**What it costs them:** Reserved memory for idle sessions (2 TB for 1,000 sessions at 2 GB each under reservation), per-job VM line items, engineering time maintaining images and seccomp profiles, audit findings.
**Emotional tension:** Fear of a prompt-injected agent exfiltrating keys; anxiety about approving shared-infrastructure execution; frustration that "secure" means "slow and expensive".

## Competitive Landscape
**Direct:** Nono, Fence, Matchlock, Pent, Anthropic sandbox-runtime (srt), Codex's Landlock+seccomp sandbox. Fall short because: no HTTP ACL or credential injection, no COW, no dynamic policy, no fleet layer, and most are single-purpose wrappers rather than a policy engine with SDKs.
**Secondary:** Firecracker / Kata / gVisor / Docker. Fall short because: privilege or KVM required, image builds, idle memory reserved, slower startup.
**Indirect:** Hosted sandbox clouds (E2B, Modal, Daytona, Vercel Sandbox, Cloudflare Sandbox). Fall short because: workload leaves the customer's trust boundary, metered cost, operational dependency.

## Differentiation
**Key differentiators:**
- Kernel-enforced allowlists (Landlock + seccomp) with a narrow supervisor for runtime decisions; no root, no namespaces, no cgroups, no KVM
- HTTP method/host/path ACL with zero-config HTTPS interception and credential injection the workload never sees
- Copy-on-write filesystem with commit, abort, dry-run; COW fork clones a running sandbox in ~530 us
- Programmable: policy callbacks and extension handlers inside the supervisor
- Every interface from one core: CLI, Python, Rust, Go, OCI runtime, MCP server
- Commercial layer runs in the customer's account; checkpoint-store scheduling gives ~48x sessions per host at 1,000 sessions
**How we do it differently:** Split static policy (kernel) from runtime decisions (supervisor), so the fast path never leaves the kernel and the supervisor stays small enough to audit.
**Why that's better:** 5 ms startup, 97% of bare-metal throughput, TOCTOU-safe path rules, and a boundary you can state precisely.
**Why customers choose us:** The only option that is simultaneously unprivileged, fast, HTTP-aware, and deployable in their own account with an Apache-2.0 exit.

## Objections
| Objection | Response |
|-----------|----------|
| "It shares the host kernel; a kernel exploit escapes it." | True, and stated in the security model. Sandlock is not a VM. If the threat model includes a burned kernel 0-day, put Sandlock inside a VM boundary; the commercial layer packs density inside each boundary you choose. |
| "Why not just use Firecracker / E2B?" | Firecracker needs KVM and reserves memory per idle VM; hosted clouds move customer code onto a vendor kernel. Sandlock runs unprivileged in your account and provisions memory only while a session executes. |
| "Kernel 6.12 is too new for our fleet." | The strict default refuses to start without full Landlock ABI v6; individual protections can be waived explicitly, and the OCI runtime tolerates older kernels. |
| "What happens if we stop paying?" | The Apache-2.0 core, SDKs, CLI, OCI runtime, and MCP server keep working. Only the HTTP API and Scheduler are licensed, and there is no license server to cut you off. |

**Anti-persona:** Teams that need a separate guest kernel per workload, need to boot a full OS, run on non-Linux hosts, need hard CPU/memory guarantees (cgroups), need rotating secrets inside the sandbox, or run a single sandbox on a single host (the open-source project is the whole answer there).

## Switching Dynamics
**Push:** Idle-session memory bills, per-job VM costs, image maintenance, KVM unavailability on cloud VMs, audit pressure on shared-infrastructure execution, discomfort with customer code on a vendor's kernel.
**Pull:** 5 ms startup, no root, HTTP-level policy, credential injection, COW, deployable in own account, open-source exit.
**Habit:** Existing Docker/Firecracker pipelines and images; team familiarity with container tooling.
**Anxiety:** Shared-kernel risk, kernel version floor, a young project, supervisor as a single component to trust, small vendor.

## Customer Language
**How they describe the problem:**
- "We need to run untrusted code on shared infrastructure."
- "Our agents spend 99% of their time waiting on the model and we pay for the memory the whole time."
- "I can't explain a container escape to our auditor."
**How they describe us:**
- "Kernel-level sandboxing for AI agents without the container tax."
- "The lightest AI sandbox: no container, no VM, no privilege."
**Words to use:** confine, policy, allowlist, default deny, kernel-enforced, unprivileged, process sandbox, supervisor, your infrastructure, trust boundary, evidence.
**Words to avoid:** "unbreakable", "military-grade", "zero-trust" as a slogan, "serverless sandbox", claiming VM-equivalent isolation, "phone home"-style features.
**Glossary:**
| Term | Meaning |
|------|---------|
| Landlock | Linux unprivileged access-control LSM for filesystem, TCP ports, and IPC scoping |
| seccomp-bpf | Kernel syscall filter installed with NO_NEW_PRIVS |
| seccomp user notification | Mechanism that hands selected syscalls to a userspace supervisor for a verdict |
| Supervisor | Sandlock's async process that handles runtime decisions and virtualized effects |
| COW | Copy-on-write staging of the workload's writes with commit, abort, dry-run |
| COW fork | Cloning a running sandbox, ~530 us per clone |
| HTTP ACL | Method, host, and path rules enforced through a transparent proxy |
| Credential injection | Attaching a secret at the proxy so the workload never holds it |
| Pipeline | Multi-stage execution where each stage has its own policy |
| Sandbox HTTP API | Commercial REST layer: sandboxes with identity, checkpoints, scoped keys |
| Sandbox Scheduler | Commercial placement layer using a checkpoint store as a session's home |
| No-supervisor mode | Landlock plus kernel-only seccomp filter, no supervisor (used for nesting) |

## Brand Voice
**Tone:** Measured, technical, candid about limits.
**Style:** Direct declarative sentences; specific mechanisms over adjectives; states what is out of scope as readily as what is in.
**Personality:** Precise, honest, engineer-to-engineer, unhurried, understated.

## Proof Points
**Metrics:** ~5 ms startup (44x faster than Docker start); 97.1% of bare-metal Redis throughput; COW fork ~530 us per clone, ~1,900 forks/s, 1,000 sandboxes in 718 ms; Scheduler model: 1,000 sessions at 2 GB in 42 GB (~48x), approaching 91x at 100k sessions.
**Customers:** None public yet.
**Testimonials:** None yet.
**Value themes:**
| Theme | Proof |
|-------|-------|
| Strict without the weight | 5 ms startup, no root, no image, 97% throughput |
| A boundary you can state | Security model page, arXiv 2605.26298, default-deny, TOCTOU-safe Landlock rules |
| Programmable confinement | policy_fn, extension handlers, HTTP ACL, credential injection |
| Fleet economics | ~48x sessions per host via checkpoint-store scheduling |
| Yours, not ours | Runs in your account, no license server, Apache-2.0 exit |

## Goals
**Business goal:** Adoption of the open-source core by AI agent and code-execution teams, converting fleet-scale operators to HTTP API and Scheduler licenses.
**Conversion action:** Book a technical call (calendar link) or email contact@multikernel.io; secondary: install from the package index.
**Current metrics:** Not tracked in the repo.

## Changelog
*Newest first. One line per revision: what changed and why.*
- v1 (2026-08-28) — Initial context, auto-drafted from the site, README, and the Sandlock paper.
