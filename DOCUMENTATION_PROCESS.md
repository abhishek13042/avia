# Project 3 — Documentation Process

## Purpose

Documentation is a required project output, not an optional final activity.

Every important project decision, implementation, test, verification result, evidence item, and quality-gate decision must be saved in a Markdown file.

## Required file format

Use `.md` files for project documentation.

The project will use Markdown for:

- Discovery.
- Architecture.
- Phase definitions.
- Specifications.
- Tasks.
- Implementation records.
- Test records.
- Verification records.
- Evidence indexes.
- Quality gates.
- Experiment logs.
- Error analysis.
- Runtime benchmarks.
- Final audits.

## Required documentation locations

```text
PROJECT_DISCOVERY_AND_ARCHITECTURE.md
EXECUTION_ORDER.md
DOCUMENTATION_PROCESS.md
README.md
phases/
├── README.md
├── EXECUTION_STATUS.md
├── TASK_EXECUTION_TEMPLATE.md
├── phase-01-*/
│   ├── PHASE.md
│   ├── TASKS.md
│   ├── specs/
│   ├── tasks/
│   ├── evidence/
│   └── reports/
├── phase-02-*/
├── phase-03-*/
├── phase-04-*/
└── phase-05-*/
```

## Documentation rules

### Rule 1 — Document before implementation

Before implementing a task, the corresponding SPEC and TASK must exist in Markdown.

### Rule 2 — Document the decision

Every architectural or scientific decision must include:

- decision;
- reason;
- evidence;
- alternatives considered;
- limitations;
- date/status.

### Rule 3 — Document the task before starting it

Every task record must contain:

- task ID;
- task name;
- phase;
- SPEC;
- objective;
- scope;
- non-goals;
- dependencies;
- inputs;
- planned implementation;
- acceptance criteria.

### Rule 4 — Document implementation results

After implementation, record:

- files changed;
- commands executed;
- configuration used;
- inputs used;
- outputs produced;
- known limitations;
- unresolved problems.

### Rule 5 — Document tests

Every task must record tests in Markdown:

| Test | Command/procedure | Expected result | Actual result | Status |
|---|---|---|---|---|
| | | | | |

Do not mark a task complete from intention alone.

### Rule 6 — Document verification

Verification must compare expected and observed behavior:

- expected behavior;
- observed behavior;
- comparison;
- pass/fail;
- reason;
- reviewer or verification method.

### Rule 7 — Save evidence paths

Every task must list evidence paths, including where applicable:

- report;
- log;
- metric file;
- visualization;
- rendered video;
- screenshot;
- checkpoint;
- configuration;
- benchmark output;
- API response.

Large binary files may be stored outside Git, but the Markdown evidence file must contain their location, checksum, and description.

### Rule 8 — Record quality gates

Every task must end with:

- gate name;
- pass/fail/blocked status;
- evidence used;
- reason;
- follow-up task if failed.

### Rule 9 — Never overwrite history silently

When a decision changes:

1. Preserve the previous decision.
2. Record the new decision.
3. Explain why it changed.
4. Record impact on phases, specs, tasks, experiments, and evidence.

### Rule 10 — Keep facts separate from assumptions

Use explicit labels:

- `Verified fact`
- `Measured result`
- `Assumption`
- `Unknown`
- `Decision`
- `Limitation`

### Rule 11 — Record compute location

Every training or benchmark record must state:

- Local or Kaggle.
- Hardware.
- GPU model.
- VRAM.
- CPU/RAM.
- Framework version.
- CUDA/runtime version.
- Dataset version/hash.
- Split version/hash.
- Seed.
- Duration.
- Peak memory.

### Rule 12 — Record dataset and code versions

Every result must link to:

- source dataset;
- dataset version;
- manifest hash;
- split hash;
- code commit or source version;
- configuration file;
- model checkpoint;
- evaluation script version.

### Rule 13 — Document failures

Failures are evidence. Record:

- what failed;
- when it failed;
- inputs;
- error message or behavior;
- cause if known;
- correction;
- regression test;
- remaining risk.

### Rule 14 — Do not claim undocumented behavior

If a capability has not been tested and documented, do not claim that the system supports it.

This applies especially to:

- real-time performance;
- generalization;
- anomaly detection;
- irrigation intelligence;
- plant stress;
- disease detection;
- production deployment.

## Task completion template

Use:

```text
phases/TASK_EXECUTION_TEMPLATE.md
```

## Required task lifecycle files

For each completed task, create or update:

```text
TASK-<id>-<name>.md
```

The record must remain available after the task is complete.

Suggested location:

```text
phases/phase-XX-name/tasks/
```

## Required evidence files

Evidence should be indexed in Markdown:

```text
phases/phase-XX-name/evidence/EVIDENCE-<task-id>.md
```

The evidence file should link to generated images, videos, reports, metrics, logs, or artifacts.

## Required phase completion report

At the end of each phase, create:

```text
phases/phase-XX-name/reports/PHASE-XX-COMPLETION.md
```

It must contain:

- phase objective;
- completed tasks;
- deferred tasks;
- implementation summary;
- tests summary;
- verification summary;
- evidence index;
- failures;
- limitations;
- quality-gate decision;
- approval to begin the next phase.

## Required final documentation

The finished project must contain Markdown documentation for:

- project discovery;
- dataset card;
- problem definition;
- architecture;
- all SPECs;
- all TASKs;
- all implementation records;
- all tests;
- all verification results;
- all experiment results;
- all error analysis;
- all runtime benchmarks;
- all failure cases;
- final audit;
- reproducibility instructions;
- final claims and limitations.

## Documentation quality gate

Documentation is complete only when another person can understand:

1. What the project solves.
2. Why the dataset was selected.
3. What every model does.
4. What every metric means.
5. How every result was produced.
6. Which claims are verified.
7. Which limitations remain.
8. How to reproduce the work.
