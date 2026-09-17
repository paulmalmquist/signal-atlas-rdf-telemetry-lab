# Security and trust boundaries

## This delivery

Local, synthetic, single-user teaching software. There is no identity provider, role-based authorization, row-level security, multi-tenant isolation, compliance assessment, formal threat model approval or production certification. Do not put it on a public interface or ingest sensitive work data.

The launcher binds only 127.0.0.1. FastAPI restricts accepted hosts, rejects mismatched POST origins, uses no wildcard CORS, serves local assets and emits a content security policy. Raw source viewing uses a fixed allowlist. SQL sample lookup is parameterized and bounded. User-controlled strings are HTML-escaped.

SPARQL is parsed before execution; SERVICE, FROM, updates and unsupported forms are rejected. Query workers load a fixed local TriG file, deny socket creation and have a six-second parent timeout. On supported Unix systems they also apply CPU and address-space limits. Output is capped at 250 rows/triples, and query length at 20 KB. These are prototype safeguards, not proof that all denial-of-service, side-channel or interpreter-level attacks are impossible.

The read model is immutable during a request. Scenario changes occur in an isolated copy and do not write back to the fixtures or baseline. The graph import path is not a public user-upload endpoint. Do not add arbitrary RDF/XML or JSON-LD URL parsing without a separate security review: RDF tooling can access files or network resources depending on format and execution features.

## Work-side gates before real data

1. **Ownership and classification:** identify owners for sensor identity, installation history, units, certificate authority, event time and reports. Classify raw and derived data; obtain approval for the exact fields.
2. **Authentication and authorization:** integrate the existing company identity and app patterns. Enforce permissions on every API, SPARQL pattern, source preview, graph edge and sample retrieval. Front-end hiding is insufficient.
3. **Inference leakage:** a hidden node can be disclosed through counts, relationships or derived results. Test both direct and inferential access paths. Named graphs alone are not access control.
4. **Constrained execution:** prefer approved parameterized query templates initially. Put any free-form SPARQL behind resource quotas, statement-level authorization, audited execution and a reviewed sandbox with no egress.
5. **Data lifecycle:** immutable approved source snapshots, signed or otherwise trusted provenance as needed, source coverage/watermarks, revocations, retention, deletion, recovery and audit.
6. **Deployment review:** private ingress, approved container base/dependency locks, SBOM, vulnerability scanning, workload identity, secrets manager and logging that does not leak values or unrestricted queries.
7. **Decision policy:** distinguish unknown, conflicting, stale, invalid and approved evidence. Every operational use needs an accountable human owner. A graph query must not silently become a test acceptance rule.

## Publication boundary

Keep the personal repository synthetic and private. Private GitHub is not an approved destination for company information. Move this prototype one way to work. Do not sync the work-side implementation, real fixture extracts, private ontology, credentials or company URLs back to the personal copy.

The private publishing script checks repository absence and final visibility, but its human synthetic-data confirmation is not a secret scanner. Review files before pushing. Treat a failed creation/push step as requiring inspection; do not assume it rolled back a partially created private repository.

The optional Docker and GitHub Actions files are scaffolding and were not executed during delivery. The pySHACL integration is also unverified. No security certification is claimed.

Reference: [RDFLib security considerations](https://rdflib.readthedocs.io/en/latest/security_considerations/).
