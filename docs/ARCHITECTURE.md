# Architecture: context beside the samples

## The smallest useful system

```text
PLM fixture ──────────┐
Sensor registry ──────┤
Calibration fixture ─┤      Explicit IDs, mapping version,
Test-run fixture ────┼────> temporal joins and source hashes ──> RDFLib Dataset
QMS fixture ─────────┤                                            │
Requirements/reports ┤                                      SPARQL / SHACL subset
Telemetry CSV ───────┘                                            │
       └──────────────> indexed SQLite raw samples ───────> FastAPI read API
                                                                 │
                                                local HTML / CSS / JavaScript
```

This is a batch-built, local read model. It is not a streaming platform, a distributed triple store, an agent framework, an automatic data catalog or a source-system synchronization service. No application route changes the source systems or the baseline graph.

## Grain and identity

A **physical sensor** has a stable canonical IRI. A **channel** is a logical acquisition stream with a raw tag, sensor mapping and declared unit. A **deployment** relates a sensor to a component over a validity interval. A **test run** captures time, phase and configuration. A **summary observation** represents a specific run/channel window and its good-quality arithmetic mean. Raw samples retain their original sample identifiers.

A source identifier is not automatically globally unique. The mapping fixture records source system, source ID, canonical sensor, approval state and mapping version. No `owl:sameAs` is generated from fuzzy name similarity. The build uses the deliberately curated mappings; a real adapter must quarantine ambiguous and unmapped records rather than guess.

The fixture has one sensor per channel for the sampled windows. Production channel reassignment, sensor replacement, a revised bill of materials and aliases reused over time require their own versioned/effective mappings. The synthetic BOM is a snapshot; the time-bounded deployment example does not solve every configuration-history problem.

## Two storage grains

The fixture contains 14,424 samples: four runs × six channels × 601 samples. Samples include 0.0 and 60.0 seconds at 10 Hz. SQLite stores the detailed timestamps, values, units and quality flags. The graph contains 24 summary observations, metadata and evidence links rather than 14,424 sample-observation resources.

Each summary includes `sosa:madeBySensor`, `sosa:hasFeatureOfInterest`, `sosa:observedProperty`, `sosa:hasSimpleResult`, explicit unit, window boundaries, run, channel, deployment, procedure, count and a raw selector. Its result time is the fixed snapshot creation time. Its phenomenon interval is the sampled event-time window. An observation's historical component is determined from the deployment that covers that entire window.

The mean excludes samples whose quality is not `good`; the chart still displays all original values. P-103 has 597 good samples out of 601 per run. The summary retains raw unit evidence even when the channel registry's unit is missing. This intentionally does not conceal a registry defect by silently filling it.

In a work-side implementation, retain high-frequency storage and numeric workloads in the existing governed warehouse/time-series platform. Replace only the local sample reader with a permission-aware, parameterized, bounded query. Do not replace BigQuery because the demonstration happens to use SQLite.

## Time matters

Certificate and deployment validity intervals are **[validFrom, validTo)**. The upper bound is exclusive. Sample windows contain their final sampled instant. Therefore a covering interval must satisfy `validFrom <= firstSample` and `validTo > lastSample`.

P-101's first calibration expires on 2026-09-10T00:00:00Z. T-101 occurs September 9 and is covered. T-102 through T-104 are later and are review candidates. P-101 moves components on September 12: T-102 belongs to manifold A; T-103 and T-104 belong to manifold B. Querying today's installation would attach the wrong component to T-102.

Query 05 checks that an approved expired certificate exists and that no approved certificate covers the whole window. This prevents an old expired certificate from causing a false positive after replacement evidence is added. The fixture has simple certificate histories. A production implementation must handle supersession, revocation, approval timing, overlapping evidence, partial coverage, calibration scope and whether retrospective certification is permissible. These are owner-approved policies, not facts inferred from RDF.

Query 06 means **no certificate in this dataset**. It does not prove that a certificate does not exist in the world. A not-yet-valid certificate or partial source coverage would require additional states; the example is not a complete calibration decision system.

## Graphs, provenance and reasoning

Nine nonempty named graphs separate ontology, seven source families and catalog metadata. The application deliberately loads `Dataset(default_union=True)`. Unqualified query patterns see that union here; that behavior must be configured explicitly when migrating to another store. Use `GRAPH` when source context matters.

The source catalog stores SHA-256 hashes, snapshot timestamps and mapping version. `prov:wasDerivedFrom` points to the source fixture. This is useful evidence lineage, not a cryptographic signature, access-control mechanism, statement-level confidence model or guarantee of truth.

No automatic RDFS/OWL inference is enabled. Types needed by the examples are asserted explicitly. `ex:partOf+` traverses one or more edges; it does not materialize every ancestor relationship. `CONSTRUCT` returns a derived graph without inserting it. A production inference policy must declare rules, version, provenance, consistency handling and access-control behavior.

## Component boundaries

| Module | Responsibility |
|---|---|
| `backend/seed.py` | Deterministic fixture generation, explicit invocation only |
| `backend/build.py` | Read source contracts; build RDF and SQLite |
| `backend/query.py` | Parse/restrict queries; format RDF terms; isolated execution |
| `backend/query_worker.py` | Bounded query process, local RDF only |
| `backend/validation.py` | Supported shape subset; fail on unknown shape constructs |
| `backend/service.py` | Read models, raw sample retrieval, isolated what-if copies |
| `backend/app.py` | HTTP API, host/origin constraints and same-origin assets |
| `backend/adapters.py` | Work-side extension protocol; no live implementation |
| `frontend/src/app.js` | UI state, interactions, SVG views and learning modules |

The SPARQL endpoint implements a teaching subset of protocol behavior. Supported forms are SELECT, ASK and CONSTRUCT; updates, SERVICE, external datasets and DESCRIBE are rejected. Do not represent it as a full SPARQL server or a multi-tenant security boundary.

## Growth decisions

Keep this architecture until measured data size, query complexity, concurrency, persistence or governance needs justify a dedicated graph store. Evaluate an approved SPARQL endpoint with query limits and policy enforcement using the same competency-query tests. RDF modeling does not require a particular vendor.

Require repeatable semantic identifiers, versions, idempotent ingestion, deletion/tombstone behavior, late data handling, data quality quarantine and differential rebuilds before any continuous feed. Indexing, access control, stale-result indicators, cost budgets and query observability are prerequisites, not decorative follow-ups.

References: [RDF concepts](https://www.w3.org/TR/rdf11-concepts/), [SPARQL](https://www.w3.org/TR/sparql11-query/), [SOSA/SSN](https://www.w3.org/TR/vocab-ssn/), [PROV-O](https://www.w3.org/TR/prov-o/).
