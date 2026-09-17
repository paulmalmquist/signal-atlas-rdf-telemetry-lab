# Signal Atlas · RDF Telemetry Lab

**A real, local application for learning RDF and SPARQL by investigating synthetic test evidence.**

Start with one question: **Which test results need review because a sensor's calibration evidence did not cover the observation window?** Then follow the result to the physical sensor, its installation at that time, the measured component, the source record and the original samples.

This is a teaching prototype, not a flight-readiness system. Every component, sample, certificate, issue and requirement is invented. There are no company connections, real engineering limits, credentials, external AI calls or production acceptance decisions.

## Start here

For a no-install tour, open `preview/Signal_Atlas_Preview.html` in a desktop browser. It is a self-contained snapshot: all saved query results, sources and charts are included. The query editor is deliberately read-only in that file. Use the application below to execute and edit real SPARQL.

### Run the real application

Python **3.13** was tested. Python 3.11+ is the intended range but was not separately tested. No Node, cloud account, graph-server account or API key is needed. Package installation needs your normal package index; runtime uses only local files.

```bash
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/run_lab.py
```

Open **http://127.0.0.1:8000**. Stop with Ctrl+C. Use `python scripts/run_lab.py --port 8010` if port 8000 is busy. The launcher builds RDF and SQLite from the supplied raw fixtures; it does not overwrite those fixtures.

To regenerate the original synthetic fixture set explicitly:

```bash
python -m backend.seed
python -m backend.build
```

Restart the server after changing source files; its read models are cached. Never point this personal teaching copy at company sources. The source generator intentionally overwrites the fixtures only when explicitly invoked.

## Your first investigation

1. **Mission overview → Start the investigation.** Query 05 returns three P-101 observations with expired evidence: T-102, T-103 and T-104.
2. **Graph explorer.** Follow P-101 and its deployments. It moves from manifold A to manifold B on September 12, 2026. Historical observations retain the correct component.
3. **Telemetry.** Select T-102 / CH-P-101. Inspect 601 original samples and the good-quality mean. Switch to P-103 and distinguish unknown calibration evidence from known expired evidence.
4. **SPARQL workbench.** Run inventory, property paths, OPTIONAL, NOT EXISTS, GRAPH, CONSTRUCT and ASK. Edit the query; the local RDFLib engine actually executes it.
5. **Evidence & quality.** Run both isolated what-if scenarios. Expired matches go from 3 to 0; the unit-contract violation goes from 1 to 0. The original fixture and graph remain unchanged.
6. **Learning path.** Complete eight modules, then use the capstone in `docs/TRAINING_GUIDE.md`.

## What is included

| Area | Delivered |
|---|---|
| Application | Seven responsive pages, interactive RDF neighborhood, editable SPARQL, SQL-backed sample chart, source inspector, quizzes and isolated scenarios |
| Data | Seven synthetic sources; 14,424 raw samples; six sensors; four runs; seven deployments |
| Graph | 928 baseline RDF statements, nine nonempty named graphs, 24 summary observations, source hashes and mapping version |
| Query library | 12 executable `.rq` examples with questions, explanations and challenges |
| Validation | Declared SHACL shapes and a deliberately bounded validator for the subset those shapes use |
| Training | PowerPoint with speaker notes, PDF, eight labs, query answer key and expert-interview guide |
| Transfer | Architecture, security, adapter contract, work handoff and private GitHub publishing script |
| Tests | 43 automated tests and nine browser checks; see the exact boundaries below |

Raw samples remain in **SQLite**, standing in for an existing time-series store or BigQuery. RDF holds identity, context, selected summaries and evidence links. This is a deliberate hybrid design, not a recommendation to encode every high-frequency sample as triples.

## Honest capability boundaries

The running application uses genuine RDFLib SPARQL, not canned answers. The standalone preview replays saved results and cannot run arbitrary queries. No automatic RDFS/OWL reasoner is enabled. A property path traverses asserted edges; it does not prove physical causality. No live federation, streaming ingestion or write-back is implemented.

The bundled SHACL evaluator supports only the NodeShape / targetClass / direct-property-path / minCount / maxCount / datatype / IRI nodeKind subset needed by the included shapes. Unknown constructs fail closed. It is **not a general SHACL engine**. `scripts/validate_full_shacl.py` provides an optional pySHACL path, but pySHACL was unavailable in the build environment and that integration was not executed.

There is no authentication. The server is for a trusted, single-user, **loopback-only** lab. Do not expose it to the internet or put real restricted data behind it without the work-side gates in `docs/SECURITY.md`.

## Tests and reproducibility

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The shipped evidence records 43 passing tests and nine passing browser interaction checks. Browser checks exercised the exact UI files against real FastAPI handlers through an in-process transport because the build environment blocks Chromium loopback navigation. They are not a hosted deployment test. Docker, remote GitHub Actions, pySHACL and a company integration were not run.

Optional browser checks need Playwright and Chromium, neither required by the application:

```bash
python -m pip install playwright==1.57.0
# Set CHROMIUM_PATH to your locally installed Chromium executable.
python scripts/check_browser.py
```

The dependency files pin direct packages, not the complete transitive dependency graph. Use your approved resolver, lockfile, SBOM and vulnerability review before work-side adoption. The test configuration suppresses only known RDFLib/pyparsing deprecation messages; it does not suppress test failures or arbitrary warnings.

## Repository status and private publication

**This delivery contains a complete local Git repository snapshot and a portable Git bundle. A remote GitHub repository was not created from this chat.** The connected GitHub tool could read and modify existing repositories but did not expose repository creation, and the build environment had no authenticated GitHub CLI.

After extracting the ZIP and authenticating your own GitHub CLI, run:

```bash
gh auth login
python scripts/publish_private.py
```

The script creates **paulmalmquist/signal-atlas-rdf-telemetry-lab** with `--private`, pushes the source and verifies visibility. It refuses an existing repository or any existing `origin` rather than risk publishing to the wrong place. It never asks you to paste tokens into a file.

To restore the supplied Git history instead of initializing from the ZIP, clone the separate bundle into an empty directory:

```bash
git clone Signal_Atlas_Repository.bundle signal-atlas
cd signal-atlas
git remote remove origin
```

A bundle clone's origin points at the local bundle; remove that local origin before using the publishing script. GitHub publication is a user-authenticated action, not something already completed.

## Optional Docker path

```bash
docker compose up --build
```

This scaffolding binds port 8000 to 127.0.0.1 and uses a non-root container user. It was supplied but not executed in the build environment. The Python launcher above is the tested path.

## Training and work transfer

- `training/Signal_Atlas_Training.pptx` — editable slides and detailed presenter notes.
- `training/Signal_Atlas_Training.pdf` — phone-friendly reference.
- `docs/TRAINING_GUIDE.md` — eight guided labs and all query answers.
- `docs/EXPERT_CAPTURE.md` — turn the single expert's knowledge into shared, testable artifacts.
- `docs/WORK_HANDOFF.md` — one-way, synthetic-to-work integration instructions.
- `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/VALIDATION_REPORT.md` — design and limits.
- `docs/SOURCES.md` — official standards and library references.

The project carries no external open-source license grant by default. Choose any intended distribution license deliberately; third-party packages retain their own licenses.
