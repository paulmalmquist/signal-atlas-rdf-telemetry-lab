# Candidate opportunities to validate, not promises

| Candidate application | Why a graph may help | First proof | Important limit |
|---|---|---|---|
| Calibration evidence impact | Traverse observations → sensors → certificates → reports across source boundaries | Reproduce one SME-reviewed investigation and its counterexamples | Evidence review is not an automatic acceptance decision |
| Telemetry discovery | Search by measured property, unit, component and historical deployment rather than memorized tag | Find a known set of channels with provenance | Identity and unit mappings require ownership; matching labels is insufficient |
| Configuration-aware comparison | Select windows satisfying phase, procedure, unit and configuration constraints | Recover the expert's eligible comparison set | Eligibility does not prove statistical comparability or causal equivalence |
| Requirement/report lineage | Show which observation supports which report and requirement revision | Trace a report to raw source and exact window | Requirements can involve complex evidence logic not captured by a simple edge |
| Change-impact review | Identify derived products downstream of a revised source assertion | Replay a controlled change and compare affected evidence | Need revision/effectivity and deletion semantics before production use |
| Shared expert knowledge | Turn tacit relationship knowledge into definitions, mappings and executable questions | Second person completes investigation and explains negative cases | The expert remains essential to validate meaning |

## My recommended starting point

Run the calibration investigation as a learning exercise, then ask the SME whether calibration, configuration history or channel discovery is the strongest real pilot. Choose a question with a clear owner, a small approved source slice and a reproducible answer. Prove that someone other than the expert can answer it correctly and explain uncertainty.

Do not begin with a company-wide ontology, natural-language agent, mass triple conversion, autonomous operational decision or write-back connector. Those can obscure whether the basic identities and relationships are even right.

## Compare fairly against SQL

SQL can answer these questions too. A graph is worth considering when shared identifiers, relationship reuse, changing traversal patterns and cross-domain semantics reduce repeated custom joins and improve explainability. If the problem is simply filtering or aggregating one well-modeled table, SQL is likely the simpler choice. Benchmark both on the real workload before claiming speed, cost or productivity advantages.

The lab intentionally separates numerical storage from semantic context. A graph is not a universal warehouse replacement, and RDF alone does not make the organization synchronized, intelligent or correct.
