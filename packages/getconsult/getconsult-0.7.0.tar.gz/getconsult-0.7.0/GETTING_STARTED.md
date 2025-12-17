# Getting Started

This guide walks you through installation, basic usage, and understanding how Consult works.

## Installation

### Prerequisites

- Python 3.10+
- API key from at least one provider (Anthropic, OpenAI, or Google)

### Install from PyPI

```bash
pip install getconsult
```

### Configure API Keys

```bash
# Create config directory
mkdir -p ~/.consult

# Add your API key
echo 'ANTHROPIC_API_KEY=sk-ant-...' > ~/.consult/.env
chmod 600 ~/.consult/.env
```

Or set environment variables directly:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Development Install

For contributing or development:

```bash
git clone https://github.com/1x-eng/agentic-atlas.git
cd agentic-atlas
pip install -e ".[dev]"
```

### Verify

```bash
consult --version
consult --status
```

The `--status` command shows your current tier, limits, and usage.

## First Query

```bash
consult -p "Design a real-time chat application database"
```

This runs a consensus workflow with 3 experts (database, backend, infrastructure). They'll analyze your problem, review each other's work, and synthesize a final recommendation.

Output appears in your terminal. For longer outputs or team mode, add `--markdown` to save to `~/.consult/outputs/`.

## Understanding the Output

The final output includes:

1. **Recommendations** attributed to specific experts
2. **Areas of agreement** across the panel
3. **Trade-offs** and their implications
4. **Sequencing** (what depends on what - not fake "Week 1" timelines)

Each claim traces back to which expert proposed it.

## Interactive Mode (TUI)

For conversation continuity and real-time workflow visualization:

```bash
consult-tui
```

**Note**: TUI requires Pro tier. Free tier users can use the CLI with `--memory-session` for conversation continuity.

### TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Shift+Enter` | Send query |
| `D` | Toggle Detail Pane (agent reasoning traces) |
| `L` | Toggle Activity Log |
| `1-9` | Select agent in Detail Pane |
| `E` | Change experts |
| `P` | Change provider |
| `M` | Toggle single/team mode |
| `N` | New session |
| `?` | Help |
| `Q` | Quit |

### Detail Pane

Press `D` to see each agent's journey through the workflow:

- **Initial position**: First analysis before any feedback
- **Peer reviews received**: What other experts said about this solution
- **Revised position**: How they incorporated feedback
- **Approvals given**: How this agent rated others
- **Approvals received**: How others rated this agent

History is retained across queries in the same session.

## How It Works

```
YOUR PROBLEM
     │
     ▼
┌────────────────────────────────────────────────────┐
│  PHASE 1: INITIAL ANALYSIS                         │
│  Experts analyze independently (in parallel)       │
└────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│  PHASE 2: PEER FEEDBACK                            │
│  Each expert reviews the others' solutions         │
└────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│  PHASE 3: META REVIEW                              │
│  Separate review catches integration issues        │
└────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│  PHASE 4: REFINEMENT                               │
│  Experts update based on feedback                  │
└────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│  PHASE 5: CROSS-EXPERT APPROVAL                    │
│  "Would I sign off on THEIR solution?"             │
│  ├─ ≥80% approval → Final synthesis                │
│  └─ <80% → Iterate or orchestrator resolves        │
└────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────┐
│  PHASE 6: OUTPUT                                   │
│  Combines recommendations with attribution         │
└────────────────────────────────────────────────────┘
```

### Key Concepts

**Meta Reviewer, Orchestrator, Presentation Agent**: These use Opus 4.5 (SOTA model) for synthesis quality. The expert agents use cost-optimized models by default (Haiku 4.5, GPT-4o-mini, Gemini 2.5 Flash-Lite) since they run in parallel and need good cost/quality balance.

**Cross-Expert Approval**: Not "how similar are our solutions?" but "would I sign off on YOUR solution for production?" This creates explicit accountability.

**Traceable Output**: Every claim cites which expert proposed it. If the system synthesizes something beyond what experts said, it's marked as such.

## Understanding Consensus

The consensus mechanism is the core of Consult. Here's how it actually works.

### The Problem with Similarity

A naive approach would ask: "How similar are the experts' solutions?" This is meaningless because:

- Similar solutions aren't necessarily correct
- Experts rating their own alignment is biased
- No one explicitly vouches for anything

### Cross-Expert Approval

Instead, each expert reviews each OTHER expert's solution: **"Would I sign off on this going to production?"**

```
Database Expert reviews:
  → Backend Expert's solution: APPROVE
  → Infra Expert's solution: CONCERNS

Backend Expert reviews:
  → Database Expert's solution: APPROVE
  → Infra Expert's solution: APPROVE

Infrastructure Expert reviews:
  → Database Expert's solution: CONCERNS
  → Backend Expert's solution: APPROVE
```

### Verdicts

| Verdict | Score | Meaning |
|---------|-------|---------|
| **APPROVE** | 1.0 | "I would sign off on this for production" |
| **CONCERNS** | 0.7 | "Acceptable, but issues should be addressed" |
| **OBJECT** | 0.0 | "Cannot endorse - fundamental problems exist" |

### What Gets Evaluated

Each review covers 5 dimensions, weighted by production impact:

| Dimension | Weight | What's Checked |
|-----------|--------|----------------|
| Requirements | 30% | Are they solving the right problem? |
| Approach | 25% | Is the technical foundation sound? |
| Trade-offs | 20% | Are the compromises reasonable? |
| Architecture | 15% | Is the design maintainable? |
| Implementation | 10% | Can this actually be built? |

### When Consensus Fails

If approval stays below threshold after max iterations:

1. **Orchestrator** analyzes all positions
2. Identifies points of agreement and contention
3. Proposes a middle-ground resolution
4. Experts evaluate the proposal
5. Final output synthesizes everything with clear attribution

This is expected behavior when experts genuinely disagree. The output will show both the disagreement and the proposed resolution.

## Subscription Tiers

Consult uses BYOK (Bring Your Own Key). You provide your own API keys; Consult manages the workflow.

### Free Tier

- 5 queries/day, 3 queries/hour
- Max 2 experts per query
- 1 iteration only
- CLI only (no TUI)
- No session persistence
- No attachments or exports

Good for evaluating whether Consult fits your workflow.

### Pro Tier ($9/month)

- 100 queries/day, 20 queries/hour
- Unlimited experts and iterations
- Full TUI access
- Session persistence across queries
- Image and PDF attachments
- Markdown export to `~/.consult/outputs/`
- Team mode (multi-provider comparison)
- Custom expert configurations

### Activating Pro

License keys are cryptographically signed tokens. Once you have a key:

```bash
# Option 1: Environment variable
export CONSULT_LICENSE_KEY="CSL1_pro_..."

# Option 2: Save to file (persists across sessions)
echo "CSL1_pro_..." > ~/.consult/license
```

Check your status:

```bash
consult --status
```

## Expert Configuration

### Predefined Sets

```bash
# Most common
consult -p "..." --experts default         # database, backend, infrastructure

# Specialized
consult -p "..." --experts security_focused # security, backend, infrastructure
consult -p "..." --experts ai_system       # ml, backend, data, infrastructure
consult -p "..." --experts architecture    # architect, database, cloud
consult -p "..." --experts full_stack      # backend, frontend, database, infrastructure
```

### Custom Selection (Pro)

```bash
consult -p "..." --experts "database_expert,security_expert,ml_expert"
```

### Available Experts

| Expert | Focus |
|--------|-------|
| `database_expert` | Data systems, consistency, optimization |
| `backend_expert` | APIs, services, scalability |
| `infrastructure_expert` | Deployment, monitoring, ops |
| `security_expert` | Threats, compliance, secure coding |
| `performance_expert` | Profiling, caching, optimization |
| `software_architect` | System design, patterns |
| `cloud_engineer` | Cloud platforms, DevOps, IaC |
| `frontend_expert` | UI architecture, performance |
| `ml_expert` | ML systems, MLOps |
| `data_expert` | Pipelines, ETL, streaming |
| `ux_expert` | User research, interaction design |

List all with:

```bash
consult --list-experts
```

## Session Persistence

### CLI with Memory

```bash
# First query
consult -p "Design data model for e-commerce" --memory-session project.json

# Follow-up (references previous context)
consult -p "How should we handle inventory?" --memory-session project.json
```

### TUI

Sessions are automatic. Each query builds on previous context until you start a new session (`N` key).

## Team Mode (Pro)

Runs the same expert configuration across multiple providers in parallel:

```bash
consult -p "Microservices vs monolith" --mode team --markdown
```

Requires API keys for at least 2 providers. Useful for comparing how different models approach the same problem.

## Attachments (Pro)

Include images or PDFs in your analysis:

```bash
consult -p "Review this architecture" --attachments diagram.png
consult -p "Security review" --attachments spec.pdf architecture.png
```

Supported: JPEG, PNG, WebP, GIF, PDF (up to 20MB each).

## Data Directory

All Consult data lives in `~/.consult/`:

```
~/.consult/
├── sessions/     # Conversation history
├── outputs/      # Markdown exports
├── cache/        # Quota tracking
└── logs/         # Debug logs
```

Override with `CONSULT_HOME` environment variable.

API keys are **never** written to any of these files. Session files and logs automatically redact sensitive data.

## Configuration Reference

### Environment Variables

```bash
# Provider API keys (at least one required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Model overrides (defaults optimized for cost/quality)
# ANTHROPIC_MODEL=claude-haiku-4-5-20251001
# OPENAI_MODEL=gpt-4o-mini
# GEMINI_MODEL=gemini-2.5-flash-lite

# For frontier models, override with:
# ANTHROPIC_MODEL=claude-sonnet-4-20250514
# OPENAI_MODEL=gpt-4o
# GEMINI_MODEL=gemini-2.5-flash

# SOTA model for meta-reviewer/orchestrator/presentation
SOTA_MODEL=claude-opus-4-5-20251101

# Data directory (optional)
CONSULT_HOME=~/.consult
```

Consult loads `.env` from both your project directory and `~/.consult/.env`.

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `-p, --problem` | required | Problem statement |
| `-v, --version` | - | Show version |
| `-s, --status` | - | Show tier and usage |
| `--list-experts` | - | Show available experts |
| `-m, --mode` | single | `single` or `team` |
| `--provider` | anthropic | Provider for single mode |
| `-e, --experts` | default | Expert set or names |
| `-i, --max-iterations` | 1 | Max refinement cycles |
| `-t, --consensus-threshold` | 0.8 | Agreement threshold |
| `--markdown` | false | Save to file |
| `--memory-session` | - | Session file path |
| `-a, --attachments` | - | Files to analyze |

## Programmatic Usage

```python
from src.workflows import ConsensusWorkflow
from src.memory.memory_persistence import MemoryPersistence

# Optional: load existing session
memory = MemoryPersistence("project.json")
memory.load_state()

workflow = ConsensusWorkflow(
    consensus_threshold=0.8,
    max_iterations=2,
    expert_config="architecture",
    memory_manager=memory.memory_manager
)

result = await workflow.solve_problem("Design microservices architecture")

print(f"Consensus: {result.consensus_achieved}")
print(f"Method: {result.resolution_method}")
print(result.final_solution)

memory.save_state()
```

## Troubleshooting

**"Query limit reached"**

Free tier has 5 queries/day. Wait until tomorrow or upgrade.

**"Feature not available"**

Some features (TUI, team mode, attachments) require Pro tier. Check `consult --status`.

**API Key Errors**

Verify at least one provider key is set in `.env`. Check with:

```bash
consult --status
```

**Long Response Times**

Normal. Consensus workflow runs 3 experts + meta review + approval phase. Team mode runs 3x the agents. Single provider mode is faster.

**Consensus Not Reached**

Expected when experts genuinely disagree. The orchestrator will propose a resolution. The output will show both the disagreement and how it was resolved.
