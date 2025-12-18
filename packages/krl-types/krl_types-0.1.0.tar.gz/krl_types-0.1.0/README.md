# KRL Types

> **Version:** 0.1.0  
> **License:** MIT  
> **Python:** ≥3.9  
> **Status:** ⚠️ CRITICAL DEPENDENCY RISK

---

## ⚠️ CRITICAL: NOT PUBLISHED TO PyPI

**This package is NOT published to PyPI but is declared as a dependency by other packages.**

If `krl-data-connectors` or `krl-premium-backend` declare `krl-types` as a dependency in their `pyproject.toml`, then:

```bash
pip install krl-data-connectors  # WILL FAIL
```

### Impact

| Package | Declares krl-types? | Installation Impact |
|---------|---------------------|---------------------|
| krl-data-connectors | ⚠️ Yes | **Installation will fail** |
| krl-premium-backend | ⚠️ Possibly | Installation may fail |

### Resolution Required

1. **Option A:** Publish krl-types to PyPI immediately
2. **Option B:** Remove krl-types dependency from other packages and inline the types
3. **Option C:** Use a private PyPI index

---

## SECTION A — Executive & Strategic Overview

### What This Repository Does

KRL Types provides **shared type definitions** used across the KRL suite:

1. **Billing Enums** — `LicenseTier`, `BillingCycle`, `UsageType`
2. **Connector Enums** — `ConnectorTier`, `DataSourceType`
3. **Model Enums** — `ModelCategory`, `ModelTier`
4. **Pydantic Models** — Shared request/response schemas

### Why This Matters

Type consistency across packages:
- Ensures frontend and backend use same tier names
- Prevents "Community" vs "COMMUNITY" vs "community" bugs
- Enables IDE autocomplete across all packages

### Current State: **BROKEN DEPENDENCY**

| Criterion | Status |
|-----------|--------|
| Types defined | ✅ Yes |
| Package structure | ✅ Yes |
| Published to PyPI | ❌ **NO** |
| Git repository | ❌ **NO** (no .git folder) |
| Version pinned | 0.1.0 |

---

## SECTION B — Contents

### Billing Types

```python
from krl_types.billing import LicenseTier, BillingCycle

class LicenseTier(str, Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
```

### Connector Types

```python
from krl_types.connectors import ConnectorTier

class ConnectorTier(str, Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
```

---

## SECTION C — Engineering Notes

### Package Structure

```
krl-types/
├── src/
│   └── krl_types/
│       ├── __init__.py
│       ├── billing.py      # Billing enums
│       ├── connectors.py   # Connector enums
│       └── models.py       # Model enums
│
├── tests/                  # Minimal tests
├── pyproject.toml          # Package definition
└── README.md               # This file
```

### Local Installation

Since this is not on PyPI, install locally:

```bash
# From the krl-types directory
pip install -e .

# Or from another package directory
pip install -e ../krl-types
```

### pyproject.toml Fix

Until krl-types is on PyPI, other packages should use:

```toml
[project]
dependencies = [
    # krl-types @ git+https://github.com/KR-Labs/krl-types.git  # When git repo exists
    # OR remove dependency and inline types
]
```

---

## SECTION D — Action Required

### Immediate Priority: HIGH

1. **Create git repository** for krl-types
2. **Publish to PyPI** (or private index)
3. **Update dependent packages** to use published version

### Owner

- **Team:** KR-Labs Engineering
- **Escalation:** engineering@krlabs.dev

### Risk If Not Addressed

- `pip install krl-data-connectors` fails
- `pip install krl-premium-backend` may fail
- Customer onboarding blocked
- CI/CD pipelines fail

---

*Last updated: December 14, 2025 — Forensic audit identified CRITICAL deployment blocker*
