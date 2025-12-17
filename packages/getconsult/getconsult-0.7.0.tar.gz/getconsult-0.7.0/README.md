# Consult

[![CI](https://github.com/1x-eng/agentic-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/1x-eng/agentic-atlas/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/getconsult.svg)](https://pypi.org/project/getconsult/)
[![Python](https://img.shields.io/pypi/pyversions/getconsult.svg)](https://pypi.org/project/getconsult/)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)

Multi-agent consensus system. N LLM agents with domain-specific prompts analyze your problem in parallel, critique each other's outputs, iterate until approval threshold is met, then a synthesis agent produces one unified answer.

## When to Use This

Single LLM calls optimize for one dimension. Use this when:

- The problem spans multiple domains (security + performance + data modeling)
- You want structured disagreement before commitment
- The cost of a bad architecture decision exceeds the cost of slower, more expensive analysis
- You're making decisions that are expensive to reverse

Don't use this for simple questions. It's 3-10x the cost and latency of a single API call.

## Installation

```bash
pip install getconsult
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                         WORKFLOW                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. PARALLEL ANALYSIS                                            │
│     N agents with domain-specific system prompts                 │
│     analyze the problem concurrently                             │
│                                                                  │
│  2. PEER REVIEW                                                  │
│     Each agent reviews each other agent's output                 │
│     (N agents = N*(N-1) pairwise reviews)                        │
│                                                                  │
│  3. META REVIEW                                                  │
│     Cross-cutting analysis: integration gaps,                    │
│     unstated assumptions, conflicting recommendations            │
│                                                                  │
│  4. REVISION                                                     │
│     Agents incorporate peer + meta feedback, update solutions    │
│                                                                  │
│  5. APPROVAL VOTING                                              │
│     Each agent votes on each other's revised solution            │
│     APPROVE (1.0) / CONCERNS (0.7) / OBJECT (0.0)                │
│                                                                  │
│  6. RESOLUTION                                                   │
│     ≥80% aggregate approval → consensus                          │
│     <80%, iterations remain → back to step 2                     │
│     <80%, max iterations reached → orchestrator decides          │
│                                                                  │
│  7. SYNTHESIS                                                    │
│     Presentation agent produces ONE unified answer:              │
│     - Merges convergent recommendations                          │
│     - Highlights resolved trade-offs                             │
│     - Notes remaining caveats from peer review                   │
│     - Provides actionable next steps                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Output: Single synthesized recommendation, not N separate answers.
```

## Usage

```bash
consult -p "problem statement" [options]
```

### Examples

```bash
# Zero-downtime schema migration with constraints
consult -p "Migrating 200M row PostgreSQL table from UUID to bigint PKs. \
47 foreign key references, 12 indexes, 3k QPS. Cannot lock table. \
Current plan: add column, backfill, swap. Backfill estimated 9 hours. \
What's wrong with this plan and what's the alternative?"

# Production debugging with incomplete information
consult -p "Kubernetes pods OOMKilled. Container limit 4Gi, JVM heap 2Gi, \
G1GC on OpenJDK 17. RSS grows to 3.8Gi over 6 hours. Native memory \
tracking shows 800MB unaccounted. Happens in prod not staging (same image). \
What are we missing?"

# Multi-domain architecture decision
consult -p "Event sourcing vs state-based for order service. \
100k orders/day, need 7-year audit trail, eventual consistency acceptable \
for reads, strong consistency required for inventory decrements. \
Team has zero ES experience. What are the actual trade-offs we'll hit?"
```

### With Expert Selection

```bash
# Default: backend, database, infrastructure
consult -p "..."

# Security-focused (security, backend, infrastructure)
consult -p "..." -e security_focused

# Custom combination
consult -p "..." -e "database_expert,performance_expert,security_expert"
```

### With Multiple Iterations (Pro)

```bash
# 3 revision cycles
consult -p "..." -i 3

# 90% agreement threshold
consult -p "..." -t 0.9
```

### With Context (Pro)

```bash
# Include diagram
consult -p "Review for single points of failure" -a architecture.png

# Continue previous session
consult -p "Now add caching layer" --memory-session project-x
```

## CLI Reference

```
consult -p "problem" [options]

Required:
  -p, --problem TEXT          Problem statement

Expert Selection:
  -e, --experts TEXT          Set name or comma-separated types
                              Sets: essentials, architecture, security_focused,
                                    performance, full_stack, data_platform, ai_system
                              Types: database_expert, backend_expert, security_expert,
                                     performance_expert, infrastructure_expert,
                                     software_architect, frontend_expert, cloud_engineer,
                                     ml_expert, data_expert

Analysis:
  -m, --mode [single|team]    single = one provider, team = all three (Pro)
  --provider NAME             anthropic, openai, or google
  -i, --max-iterations N      Max revision cycles (default: 1, Pro: up to 5)
  -t, --consensus-threshold F Approval threshold (default: 0.8)

Output:
  --markdown                  Save to ~/.consult/outputs/
  --markdown-filename TEXT    Custom filename
  -c, --copy                  Copy to clipboard

Context:
  --memory-session NAME       Session identifier (Pro)
  -a, --attachments FILES     Images/PDFs to include (Pro)

Info:
  --status                    Tier, limits, usage
  --list-experts              Available experts and sets
  --dry-run                   Validate without API calls
  --version                   Version
```

## Expert Types

| Type | Domain |
|------|--------|
| `database_expert` | Schema, queries, consistency, migrations |
| `backend_expert` | API design, service boundaries, error handling |
| `security_expert` | Auth, validation, threat modeling, compliance |
| `infrastructure_expert` | Deployment, scaling, monitoring, reliability |
| `performance_expert` | Profiling, caching, bottleneck analysis |
| `software_architect` | System design, trade-offs, patterns |
| `frontend_expert` | UI architecture, state, rendering |
| `cloud_engineer` | Cloud services, IaC, containers, networking |
| `ml_expert` | ML pipelines, training, inference, MLOps |
| `data_expert` | Pipelines, ETL, streaming, warehousing |

### Expert Sets

| Set | Composition |
|-----|-------------|
| `essentials` | backend, frontend |
| `architecture` | architect, database, cloud |
| `security_focused` | security, backend, infrastructure |
| `performance` | performance, backend, database |
| `full_stack` | backend, frontend, database, infrastructure |

## Consensus Mechanism

Each agent votes on each other agent's solution:

| Verdict | Score | Meaning |
|---------|-------|---------|
| APPROVE | 1.0 | No blocking issues |
| CONCERNS | 0.7 | Acceptable with caveats |
| OBJECT | 0.0 | Blocking problems |

3 agents = 6 pairwise votes. Aggregate = mean of all votes.

After consensus (or orchestrator resolution), a **synthesis agent** produces one unified answer incorporating all expert perspectives. You get a single recommendation, not N separate outputs.

## Tiers

BYOK: you provide API keys, pay providers directly.

| | Free | [Pro ($9/mo)](https://getconsult.sysapp.dev) |
|-|------|-------------|
| Queries/day | 3 | 100 |
| Queries/hour | 2 | 20 |
| Max experts | 2 (`-e essentials` required) | 10 |
| Max iterations | 1 | 5 |
| Team mode | No | Yes |
| TUI | No | Yes |
| Sessions | No | Yes |
| Attachments | No | Yes |
| Export | No | Yes |

### License Key

```bash
export CONSULT_LICENSE_KEY="CSL2_pro_..."
# or
echo "CSL2_pro_..." > ~/.consult/license
```

## Configuration

```bash
# ~/.consult/.env

ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...      # optional
GOOGLE_API_KEY=...         # optional

# Model overrides (defaults are cost-optimized)
ANTHROPIC_MODEL=claude-sonnet-4-20250514
OPENAI_MODEL=gpt-4o
```

## Performance

| Configuration | Latency |
|---------------|---------|
| 2 experts, 1 iteration | 45-90s |
| 3 experts, 1 iteration | 90-150s |
| 3 experts, 3 iterations | 180-300s |

Latency dominated by sequential LLM calls per phase. Agents within each phase run in parallel.

## Data Storage

```
~/.consult/
├── .env              # API keys (chmod 600)
├── license           # License key
├── sessions/         # Session state (Pro)
├── outputs/          # Exports (Pro)
├── cache/            # Rate limit tracking
└── logs/             # Debug logs (keys redacted)
```

## Security

- API keys never logged or persisted outside .env
- Session files use hashed identifiers
- Logs redact sensitive patterns
- No telemetry or phone-home

## Development

```bash
git clone https://github.com/1x-eng/agentic-atlas.git
cd agentic-atlas
pip install -e ".[dev]"
pytest
```

## License

Proprietary. See [LICENSE](LICENSE).

Personal and internal business use permitted. Commercial distribution or SaaS integration requires separate license.

---

Built on [AutoGen](https://github.com/microsoft/autogen).
