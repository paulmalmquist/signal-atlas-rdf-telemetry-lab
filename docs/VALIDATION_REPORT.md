# Delivery validation report

Build date: September 16, 2026. Dataset snapshot: September 14, 2026, 00:00 UTC. All data synthetic.

## Executed checks

- **43 automated tests passed** under Python 3.13.5. Includes every preset query, deterministic source hashes, raw/summary counts, historical deployment, event-window boundaries, unknown vs expired evidence, unapproved/covering certificate cases, isolated scenarios, SQL parameterization, SPARQL resource restrictions and API behavior.
- **Nine browser checks passed**, with no JavaScript page errors. Verified actual query execution, editing a query, telemetry selectors, RDF recentering, both scenarios, lesson interaction, source inspection and all seven pages at 390px width. Screenshots were visually inspected at desktop and phone sizes.
- Browser testing used exact application assets connected to real FastAPI handlers through an in-process bridge. Chromium loopback navigation is blocked by policy in this build environment. No browser policy was disabled, and no network/hosted deployment test is claimed.

A clean clone restored from the Git bundle also passed all 43 tests. The Python launcher served real loopback HTTP successfully: health, HTML, JavaScript, an edited six-sensor SPARQL query and a 601-point raw series. This is an HTTP smoke check, not a hosted browser deployment. See `artifacts/clean-clone-report.json`.

Machine-readable evidence: `artifacts/pytest-results.xml`, `artifacts/pytest-output.txt` and `artifacts/browser-report.json`. Screenshots are in `artifacts/`.

## Expected baseline

| Check | Result |
|---|---:|
| Synthetic raw sources | 7 |
| Raw samples | 14,424 |
| Physical sensors | 6 |
| Test runs | 4 |
| Deployment records | 7 |
| Summary observations | 24 |
| RDF statements in baseline union | 928 |
| Nonempty named graphs | 9 |
| Expired-evidence observations | 3 |
| No-certificate-in-dataset observations | 4 |
| Missing channel-unit shape violations | 1 |
| Eligible comparison windows in query 11 | 5 |
| Temporary review triples from CONSTRUCT | 15 |

## Not executed / not provided

No remote GitHub repository, GitHub Actions run, cloud deployment, company integration, streaming data, distributed triple-store benchmark, Docker execution, automatic RDFS/OWL reasoning, full SHACL conformance test or pySHACL run. No authentication/authorization system or operational acceptance model is implemented.

The direct dependency versions match the build environment. Transitive dependencies are not fully locked. Known RDFLib/pyparsing deprecations are scoped out of the test summary, not fixed upstream by this project. Tests do not establish production security, performance at real telemetry volume or engineering validity.

Additional packaging, offline-preview and deck-render checks are recorded in `artifacts/delivery-checks.json` when the release files are built.
