# Work-computer handoff

## Paste this into the work-side coding assistant

You are integrating **Signal Atlas**, a synthetic RDF/SPARQL telemetry teaching module, into my existing work environment. Preserve the existing Paul OS architecture and approved data/security patterns. This transfer is one-way. Do not push work code, private ontologies, real data, credentials, company URLs or outputs back to a personal repository.

First read `README.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/EXPERT_CAPTURE.md`, `backend/adapters.py`, the ontology/shapes, the twelve queries and the test suite. Run the synthetic application and tests unchanged before touching work connections. Establish that you can reproduce 14,424 samples, 24 observations, three expired-evidence matches, four unknown-certificate observations and one channel-unit shape violation.

Next inspect the actual local work repository and available approved tools. Do not assume any private directory, service, dataset, credential or graph endpoint exists. Identify the existing front-end router/design system, API/auth patterns, environment management, logging, testing and deployment conventions. Treat this module as an additive read layer; do not replace BigQuery, dbt, existing telemetry storage or the application shell. The supplied UI is dependency-free JavaScript. Integrate its screens natively into the existing React/TypeScript app only after discovering the real conventions; do not introduce a parallel auth system.

Create `WORK_DISCOVERY.md` **inside the work repository only**, resolving these explicit hooks:

- `WORK_SENSOR_IDENTITY_OWNER`: who governs serials, acquisition tags and canonical sensor IDs?
- `WORK_DEPLOYMENT_HISTORY_SOURCE`: authoritative installations, validity and configuration revisions.
- `WORK_CALIBRATION_SOURCE`: approval, scope, range, revision, supersession and revocation semantics.
- `WORK_TEST_EVENT_TIME_CONTRACT`: time source, UTC conversion, first/last sample and late data policy.
- `WORK_RAW_TELEMETRY_READER`: approved BigQuery/time-series read path, permissions, bound parameters and result limits.
- `WORK_REQUIREMENT_REPORT_LINKS`: authoritative report/requirement identifiers and evidence relationships.
- `WORK_GRAPH_ENDPOINT_OR_LOCAL_APPROVAL`: approved graph technology, persistence, named-graph semantics and resource budgets.
- `WORK_AUTHORIZATION_ENFORCEMENT`: policies for graph facts, derivations, counts, raw samples and source documents.
- `WORK_SOURCE_COVERAGE_WATERMARK`: what a missing row or statement can and cannot mean.

Resolve each hook with evidence from the actual work environment and an owner review. Do not invent a value. Mark unresolved hooks as blocked and keep the module visibly synthetic. No silent fallback may show mock answers under a live-data label.

Use `docs/EXPERT_CAPTURE.md` to work with the knowledgeable SME. Choose one competency question before expanding the ontology. Capture approved definitions and counterexamples as versioned mappings, queries and regression tests. Preserve distinctions between unknown, expired, not-yet-valid, superseded, revoked and conflicting evidence; the supplied lab intentionally covers only a small subset.

Implement an approved adapter following the protocol in `backend/adapters.py` within the work repository. Return explicit source snapshot metadata, event and retrieval times, ownership, classification, mapping version and identity decisions. Quarantine ambiguous IDs. Keep existing raw numeric computation in its governed platform. Represent selected observations, context and lineage in the graph; do not mass-expand high-frequency telemetry into triples merely to match the demo.

Before enabling any live connection, produce a reviewed integration plan and permission test matrix. Start with the smallest approved read-only source slice. Gate free-form SPARQL separately from curated queries. Add identity-aware enforcement, query budgets, no-egress execution, provenance/coverage labels, auditing, stale-data handling and rollback. Replace the subset validator with an approved full SHACL engine only with explicit compatibility tests. Select an inference policy deliberately; no inference is currently enabled.

Deliver: a work-only discovery report; minimal integration diff; source-to-ontology mapping; approved competency question and ownership; positive/negative tests; access-control and leakage tests; live-vs-synthetic status labels; deployment/rollback instructions; and a second-person teach-back. Never interpret a passing query or shape report as flight readiness or engineering acceptance. Report unimplemented or unverified items plainly.

## Acceptance gates

**Synthetic demo gate:** all delivered tests pass unchanged and a second person can explain the scenario.

**Source mapping gate:** one owner-approved question; known identity/effectivity/unit rules; ambiguous records quarantined; event-time and source-coverage contracts documented.

**Permission gate:** users cannot infer or retrieve unauthorized records through direct facts, relationships, aggregates, exports, source previews or raw samples.

**Read-only pilot gate:** curated questions only, bounded source slice, current coverage label, documented refresh/rollback, audit evidence and owner review.

**Expansion gate:** measured investigation benefit justifies the extra ontology, adapter or graph-store complexity. Expand by validated question, not by importing every system at once.
