# Signal Atlas training guide

## Outcome

By the end, explain an RDF triple; distinguish a sensor, channel and deployment; edit a SPARQL query; follow historical context to raw samples; distinguish unknown from expired evidence; and explain why a shape passing does not prove engineering acceptance.

Use the running application for query editing. The standalone HTML is a saved-result tour and cannot execute new SPARQL. Training data is synthetic. This is a suggested 75–90 minute learning session, not a promise about task completion time.

## Suggested session

| Segment | Minutes | What you do |
|---|---:|---|
| First investigation | 10 | Start query 05; identify the three review candidates |
| Identity and historical graph | 15 | Compare sensor/channel/deployment; follow P-101 across the move |
| Query editing | 20 | SELECT, OPTIONAL, property paths, NOT EXISTS, GRAPH and ASK |
| Samples and evidence | 15 | Inspect the selected 601-sample window, quality flags and provenance |
| What-if and validation | 10 | Compare baseline with isolated repairs; explain limits |
| Capstone and teach-back | 15 | Reproduce and explain an answer without relying on the expert |

## Lab 1 — One statement, three roles

Open Graph explorer, search P-101 and inspect its outgoing predicates. Identify a subject, predicate and object. Find a literal and a resource IRI. Explain why `P-101` is a display label/short identifier while its full IRI carries the canonical identity in this lab.

Run query 01. **Expected:** six sensors. Modify it to also return each sensor's observed property. **Check:** the repeated sensor variable joins the patterns; do not assume the label itself is the key.

## Lab 2 — Separate numbers from their meaning

Open Telemetry and select T-102 / CH-P-101. Inspect the chart and the summary. **Expected:** 601 samples, 0 through 60 seconds inclusive; one RDF summary observation for that run/channel. Switch to P-103. **Expected:** 597 good samples and four suspect flags per run; the summary mean uses only good samples, while the plot keeps all samples.

Explain the path from selected RDF observation to the parameterized SQLite run/channel lookup. This is a local replacement for a governed raw-data reader, not a real BigQuery connection. No numeric value is an engineering acceptance limit.

## Lab 3 — Follow a physical sensor through time

Run query 02, then query 05. P-101 is the same physical sensor throughout. It has two deployments. **Expected:** T-102 resolves to manifold A; T-103 and T-104 resolve to manifold B. The move becomes effective at midnight UTC on September 12, 2026.

Ask what would go wrong if the mapper joined to the current installation for every historical observation. Answer: the T-102 observation would be attached to the wrong component. Explain the half-open validity interval and why the final sampled instant must be strictly before the interval's end.

## Lab 4 — Learn graph patterns by editing

Run query 03. **Expected:** four descendants of rig-01. Change `ex:partOf+` to `ex:partOf*`. **Expected:** five matching components including rig-01 itself. This is path traversal, not automatic inference.

Run query 04. **Expected:** 24 observations, including four whose channel-unit variable is unbound. OPTIONAL preserves rows when a relationship is missing. Change OPTIONAL to a required unit pattern. **Expected:** 20 observations remain. Explain why losing those rows might hide a data-quality defect.

## Lab 5 — Distinguish evidence states

Run query 05: **three** expired-evidence observations. Run query 06: **four** observations with no certificate in the snapshot. Do not combine these under a single claim that all readings are invalid.

In Evidence & quality, simulate covering calibration evidence. **Expected:** query 05 falls from 3 to 0 in the isolated copy, while P-103 remains unknown. Return to the baseline query to confirm the original still returns 3. Discuss why the scenario is not permission to backdate or invent a real certificate.

## Lab 6 — Explain your answer with provenance

Run query 08 and find the registry assertions for P-101. Open Source catalog, inspect the registry source and find the source hash and mapping version. **Expected:** four registry triples about P-101 in that query; nine nonempty graphs in query 12.

What does the hash establish? It identifies the file bytes used. It does not establish authority, correctness or completeness. Named graphs are source grouping, not authorization by themselves. This application explicitly configures a union default graph; ask what your work-side endpoint does before moving queries.

## Lab 7 — A returned graph and a structural contract

Run query 09. **Expected:** 15 temporary triples describing three review candidates. Explain why CONSTRUCT does not mutate the dataset. There is no INSERT route.

Run query 10. **Expected:** true, because CH-AUX-401 lacks a declared unit. Inspect the shape report and simulate the unit repair. **Expected:** one structural violation becomes zero in the isolated copy. The raw voltage samples were always present; the registry contract was incomplete. This does not make the unknown calibration state disappear.

The local validator supports only the explicitly documented subset of SHACL used by the supplied shapes. It is not a full SHACL implementation. Domain evidence rules and structural contracts are separate in this lab.

## Lab 8 — Decide what deserves a graph

Run query 11. **Expected:** five eligible pressure windows: P-101 in T-101 and P-102 in all four runs. The filters require common property, unit, procedure, configuration, phase and covering approved calibration. Eligibility is not proof of statistical comparability or physical equivalence.

Compare the same question with SQL joins. Identify the benefit you actually need: shared IDs, reusable relationship semantics, changing cross-domain traversal or evidence explainability. No speedup or cost saving is assumed.

## Capstone: another person can reproduce your answer

Without looking at the preset title, find the affected reports and requirement for expired calibration evidence. Explain each hop from observation to sensor/certificate and report/requirement. **Expected:** three affected report rows linked to REQ-P: RPT-T-102, RPT-T-103 and RPT-T-104. (The exact fixture strings are shown in query 07 results.) Then add source context to a query or inspect it through GRAPH and the source catalog.

Demonstrate both a positive and negative case: an expired certificate with no covering replacement; and a covering approved replacement that suppresses that match. Explain what would happen with an unapproved replacement and a certificate that expires exactly at the final sample time.

### Teach-back rubric

Score one point each: identifies the correct candidates; uses historical deployment; explains unknown vs expired; traces raw evidence; distinguishes CONSTRUCT from write-back; explains structural validation scope. **Suggested success threshold:** six out of six and no claim of operational acceptance. This is a local training rubric, not a credential.

## Complete query answer key

Results below are computed from the supplied baseline. Queries can be copied into the running workbench. Source fixtures are the authority for this teaching snapshot; edited data changes the expected answers.

### 01-sensors — Meet your sensors

**Question:** Start with physical instruments, not channel-name strings.

**Expected:** 6 rows.

Six instruments. The same ?sensor binds facts together, just like a join key. a abbreviates rdf:type.

**Try:** Add FILTER(?property = ex:Pressure) inside WHERE. You should get three pressure sensors.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?sensor ?label ?property WHERE {
  ?sensor a sosa:Sensor ; rdfs:label ?label ; sosa:observes ?property .
} ORDER BY ?sensor
```

### 02-deployments — Where was it installed?

**Question:** Find installations rather than assigning one timeless location to a sensor.

**Expected:** 7 rows.

Seven deployment records. P-101 moved from Manifold A to Manifold B on September 12.

**Try:** Filter for ex:P-101, then compare the two half-open intervals [from, to).

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?sensor ?component ?from ?to WHERE {
  ?deployment a ex:Deployment ; ex:sensor ?sensor ; ex:component ?component ;
              ex:validFrom ?from ; ex:validTo ?to .
} ORDER BY ?sensor ?from
```

### 03-bom — Follow the hardware hierarchy

**Question:** Walk one or more direct BOM links.

**Expected:** 4 rows.

Four component/ancestor pairs. + means one or more hops; * would also include the starting component.

**Try:** Replace + with * and explain the two extra rows. A path match is not a newly stored inferred triple.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?component ?ancestor WHERE {
  VALUES ?component { ex:manifold-a ex:manifold-b }
  ?component ex:partOf+ ?ancestor .
} ORDER BY ?component ?ancestor
```

### 04-observations — Numbers with context

**Question:** Observe the difference between window summaries and raw samples.

**Expected:** 24 rows.

24 summary observations, not 14,424 raw samples. AUX-401 has unbound metadata units, retained by OPTIONAL.

**Try:** Remove OPTIONAL and its braces. Four rows disappear; inner joins can hide incomplete metadata.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?run ?sensor ?mean ?unit ?goodSamples WHERE {
  ?obs a sosa:Observation ; ex:run ?run ; sosa:madeBySensor ?sensor ;
       sosa:hasSimpleResult ?mean ; ex:goodSamples ?goodSamples ; ex:channel ?channel .
  OPTIONAL { ?channel ex:unit ?unit }
} ORDER BY ?run ?sensor
```

### 05-expired — Which results need review?

**Question:** Expired evidence is not proof the hardware failed.

**Expected:** 3 rows.

Three results use P-101 after the old certificate expired, with no covering approved replacement in this snapshot.

**Try:** Use the what-if certificate experiment. A covering newer certificate must suppress a false expired-calibration alert.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT DISTINCT ?run ?sensor ?component ?expiry WHERE {
  ?obs a sosa:Observation ; ex:run ?run ;
       sosa:madeBySensor ?sensor ; sosa:hasFeatureOfInterest ?component ;
       ex:windowStart ?start ; ex:windowEnd ?end .
  ?cert a ex:Calibration ; ex:sensor ?sensor ; ex:validTo ?expiry ; ex:status "approved" .
  FILTER(?expiry <= ?end)
  FILTER NOT EXISTS {
    ?cover a ex:Calibration ; ex:sensor ?sensor ; ex:status "approved" ;
           ex:validFrom ?from ; ex:validTo ?to .
    FILTER(?from <= ?start && ?to > ?end)
  }
} ORDER BY ?run
```

### 06-unknown — Find missing evidence

**Question:** Distinguish unknown calibration from a known expired certificate.

**Expected:** 4 rows.

Four P-103 results lack any certificate in this snapshot. Do not describe them as proven uncalibrated.

**Try:** Explain why “no matching triple” does not establish that a real-world calibration never happened.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT DISTINCT ?run ?sensor WHERE {
  ?obs a sosa:Observation ; ex:run ?run ; sosa:madeBySensor ?sensor .
  FILTER NOT EXISTS { ?cert a ex:Calibration ; ex:sensor ?sensor }
} ORDER BY ?run ?sensor
```

### 07-impact — Trace the evidence impact

**Question:** Connect questionable evidence to draft reports and the relevant requirement.

**Expected:** 3 rows.

Three draft evidence packages and the pressure-evidence requirement need review. The graph identifies a review scope, not a disposition.

**Try:** Add ?report ex:status ?status and include ?status in SELECT. Where should human approval happen?

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT DISTINCT ?run ?sensor ?component ?report ?requirement WHERE {
  ?obs a sosa:Observation ; ex:run ?run ;
       sosa:madeBySensor ?sensor ; sosa:hasFeatureOfInterest ?component ;
       ex:windowStart ?start ; ex:windowEnd ?end .
  ?cert a ex:Calibration ; ex:sensor ?sensor ; ex:validTo ?expiry ; ex:status "approved" .
  FILTER(?expiry <= ?end)
  FILTER NOT EXISTS {
    ?cover a ex:Calibration ; ex:sensor ?sensor ; ex:status "approved" ;
           ex:validFrom ?from ; ex:validTo ?to .
    FILTER(?from <= ?start && ?to > ?end)
  }
  ?report a ex:Report ; ex:forRun ?run ; ex:addresses ?requirement .
  ?requirement ex:property ex:Pressure .
} ORDER BY ?run
```

### 08-provenance — Ask who supplied a fact

**Question:** Keep source assertions attributable even when IDs join across systems.

**Expected:** 4 rows.

Facts about P-101 remain in the instrument-registry named graph. Provenance metadata for each graph is in the catalog graph.

**Try:** Replace ex:P-101 with ex:CAL-P-101. Explain why a graph name is not itself proof that a source is correct.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?graph ?predicate ?object WHERE {
  GRAPH ?graph { ex:P-101 ?predicate ?object }
} ORDER BY ?graph ?predicate
```

### 09-construct — Build a review subgraph

**Question:** Derive a temporary set of review facts without changing the source dataset.

**Expected:** 15 temporary triples (not inserted).

15 derived triples for three observations. CONSTRUCT returns a graph; it does not INSERT it. No automatic OWL reasoning is running.

**Try:** Inspect prov:wasDerivedFrom and the rule identifier. What extra approval would publication of this graph require?

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

CONSTRUCT {
  ?obs a ex:ReviewCandidate ; ex:reviewReason "No covering approved calibration; prior evidence expired" ;
       ex:affectedReport ?report ; prov:wasDerivedFrom ?cert ; ex:rule ex:impact-rule-v1 .
} WHERE {
  ?obs a sosa:Observation ; ex:run ?run ;
       sosa:madeBySensor ?sensor ; sosa:hasFeatureOfInterest ?component ;
       ex:windowStart ?start ; ex:windowEnd ?end .
  ?cert a ex:Calibration ; ex:sensor ?sensor ; ex:validTo ?expiry ; ex:status "approved" .
  FILTER(?expiry <= ?end)
  FILTER NOT EXISTS {
    ?cover a ex:Calibration ; ex:sensor ?sensor ; ex:status "approved" ;
           ex:validFrom ?from ; ex:validTo ?to .
    FILTER(?from <= ?start && ?to > ?end)
  }
  ?report ex:forRun ?run .
}
```

### 10-contract — Is a channel missing its unit?

**Question:** Use a Boolean check, then inspect the separate shape-validation report.

**Expected:** ASK = True.

True in the baseline: CH-AUX-401 lacks a declared unit. Raw sample units are still present; the adapter does not silently fix the registry.

**Try:** Run the unit-repair experiment. Only the isolated copy is changed; source fixtures remain intact.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

ASK {
  ?channel a ex:Channel .
  FILTER NOT EXISTS { ?channel ex:unit ?unit }
}
```

### 11-comparable — Select comparable evidence

**Question:** Match property, unit, procedure, test phase and configuration before drilling into samples.

**Expected:** 5 rows.

Five summaries: P-101 only at T-101, plus P-102 at every run. This is eligibility filtering, not proof of statistical comparability.

**Try:** Open a result in Telemetry. SPARQL finds the context; parameterized SQL retrieves the sample series.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?run ?sensor ?channel ?mean WHERE {
  ?obs a sosa:Observation ; ex:run ?run ; sosa:madeBySensor ?sensor ;
       sosa:observedProperty ex:Pressure ; sosa:usedProcedure ex:mean-window-v1 ;
       ex:unit unit:KiloPA ; ex:channel ?channel ; sosa:hasSimpleResult ?mean ;
       ex:windowStart ?start ; ex:windowEnd ?end .
  ?run ex:phase "hold" ; ex:configuration "CFG-A" .
  FILTER EXISTS {
    ?cert a ex:Calibration ; ex:sensor ?sensor ; ex:status "approved" ;
          ex:validFrom ?from ; ex:validTo ?to .
    FILTER(?from <= ?start && ?to > ?end)
  }
} ORDER BY ?run ?sensor
```

### 12-sources — Inventory the assertion sources

**Question:** Understand the dataset boundary before interpreting absence.

**Expected:** 9 rows.

Nine nonempty named graphs: ontology, six source registries, telemetry summaries, and a provenance catalog.

**Try:** Inspect the Sources page: file hash, snapshot time, version and source attribution. None proves the real world is complete.

```sparql
PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>

SELECT ?graph (COUNT(*) AS ?triples) WHERE {
  GRAPH ?graph { ?s ?p ?o }
} GROUP BY ?graph ORDER BY ?graph
```

## References

See `docs/SOURCES.md`. RDF, SPARQL, SOSA, PROV and SHACL concepts are grounded in the linked primary specifications. All investigations and fixtures in this guide are original synthetic examples.
