"""Hand-curated inputs for the SQLD Learning DAG build.

Everything in this package is a deliberate, reviewable decision:
- structure.py      : placement overrides, synthetic (integration/structure) nodes, explicit edge review
- prerequisites.py  : inferred prerequisite edges (each with a reason)
- content.py        : definitions, core rules, exam traps, examples, aliases
- comparisons.py    : exam comparison cards (CONTRASTS-like relations live here, not in the DAG)
- dialects.py       : ANSI / Oracle / SQL Server differences
"""
