"""Generate the facilitator guide from the same query catalog used by the app."""
from pathlib import Path
import json, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.service import query_id
ROOT=Path(__file__).resolve().parents[1]
intro='''# Signal Atlas training guide

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

'''
cat=json.loads((ROOT/'queries/catalog.json').read_text())
sections=[intro]
for q in cat:
    res=query_id(q['id'])
    if res.get('kind')=='CONSTRUCT': answer=f"{len(res['rows'])} temporary triples (not inserted)."
    elif 'rows' in res: answer=f"{len(res['rows'])} rows."
    elif 'boolean' in res: answer=f"ASK = {res['boolean']}."
    else: answer=f"{res.get('triple_count',len(res.get('triples',[])))} triples."
    sections.append(f"### {q['id']} — {q['title']}\n\n**Question:** {q['question']}\n\n**Expected:** {answer}\n\n{q.get('explanation','')}\n\n**Try:** {q.get('challenge','')}\n\n```sparql\n{q['query'].strip()}\n```\n\n")
sections.append('## References\n\nSee `docs/SOURCES.md`. RDF, SPARQL, SOSA, PROV and SHACL concepts are grounded in the linked primary specifications. All investigations and fixtures in this guide are original synthetic examples.\n')
(ROOT/'docs/TRAINING_GUIDE.md').write_text(''.join(sections))
print('training guide written')
