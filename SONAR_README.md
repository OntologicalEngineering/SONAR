# SONAR: System for Ontological Navigation and Regulation

**Published:** Greene, A. (2026). Mitigating Model Collapse in Recursive Neurosymbolic Agents: The SONAR Benchmark for Semantic Plasticity. Ontological Engineering Pty Ltd.
**Archive DOI:** 10.5281/zenodo.18203600
**Author:** Andrew Greene | ORCID: 0009-0003-7735-8000
**Organisation:** Ontological Engineering Pty Ltd | ontologicalengineering.com.au

---

## Overview

This repository contains the official implementation of the **SONAR Benchmark**,
a neurosymbolic evaluation protocol designed to detect and mitigate model collapse
in recursive agentic loops.

SONAR exposes the Metrology Gap: cosine divergence alone cannot distinguish
Artifactual Divergence (hallucinatory thrashing) from Structural Divergence
(genuine epistemic grounding). This finding is extended and empirically validated
in OE-TR-2026-03 (DOI: 10.5281/zenodo.20066480).

---

## Repository Contents

| File | Description |
|---|---|
| `sonar_benchmark_nesy.py` | Main SONAR benchmark engine (FULL mode with rupture) |
| `sonar_ablation_control.py` | Ablated control group (no rupture mechanism) |
| `sonar_graph_generator.py` | Figure generation from execution traces |
| `sonar_journal_data.json` | Full N=30 execution traces (published dataset) |
| `requirements.txt` | Python dependencies |
| `figure_1_longitudinal_divergence.png` | Figure 1 from published paper |
| `figure_2_distribution_boxplot.png` | Figure 2 from published paper |
| `LICENSE.txt` | Ontological Engineering Research Use License v1.0 |

---

## Archived Dataset

Full N=60 independent execution traces permanently archived at Zenodo:
**DOI: 10.5281/zenodo.18203600**

---

## Related Publications

| Document | DOI |
|---|---|
| SONAR Benchmark Paper (this repo) | 10.5281/zenodo.18203600 |
| OE-TR-2026-01 — The Right to Refuse | 10.5281/zenodo.19970815 |
| OE-EV-2026-01 — Empirical Dataset | 10.5281/zenodo.20337734 |
| OE-TR-2026-03 — The Case for Defective Design | 10.5281/zenodo.20066480 |

---

## Licence

See `LICENSE.txt` for full terms.

Academic replication, regulatory audit, and independent compliance
verification are permitted at no charge under open-access conditions.

Commercial use prohibited without written agreement.

Contact: andrew.greene@ontologicalengineering.com.au

---

## Citation

If you use this benchmark, please cite:

```
Greene, A. (2026). Mitigating Model Collapse in Recursive Neurosymbolic
Agents: The SONAR Benchmark for Semantic Plasticity.
Ontological Engineering Pty Ltd.
DOI: 10.5281/zenodo.18203600
```

And the empirical extension:

```
Greene, A. (2026). The Case for Defective Design: Surplus Fluency,
Constraint-Induced Fabrication, Evidentiary Concealment, and the
Consumer Right to Epistemic Warning. OE-TR-2026-03.
Ontological Engineering Pty Ltd.
DOI: 10.5281/zenodo.20066480
```
