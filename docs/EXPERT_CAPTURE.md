# Make the expertise transferable

The goal is not to replace the single knowledgeable person with a graph. It is to give that person a fast way to make crucial meaning explicit, reviewable and executable, then enable a second person to use it correctly.

## Begin with one investigation, not an enterprise ontology

Ask the expert to demonstrate a recent *type* of investigation using approved synthetic examples first. Record the sequence of decisions: where they look, which identifiers they trust, what time interval matters, which source overrides another and what would make them stop. Do not bring real sensitive examples into this personal repo.

A suggested 60-minute work-side session:

| Time | Activity | Output |
|---|---|---|
| 0–10 min | Choose a valuable question and the decision it supports | One competency question and a human decision owner |
| 10–25 min | Walk backward from answer to source records | Entity/relationship sketch, authoritative sources, missing data |
| 25–40 min | Explain tricky identities and time boundaries | Sensor vs channel vs serial vs installation; effectivity rules |
| 40–50 min | Describe counterexamples | Replaced sensor, reused tag, revoked certificate, late update, unit mismatch |
| 50–60 min | Review an executable query and teach-back | Signed-off expected result and one second-person explanation |

## Five competency questions to start

1. Which observations depend on a sensor whose approved calibration did not cover the whole observation window?
2. Where was that physical sensor installed when those observations occurred, not where is it installed now?
3. Which reports or requirements reference those observations, and can we show the exact source evidence?
4. Which channels describe the same measured property with compatible units and procedure, within the relevant configuration and phase?
5. Where is the evidence unknown, stale or contradictory, rather than demonstrably valid or invalid?

These are proposed questions, not a claim about the company's existing systems. Confirm that at least one is genuinely hard, frequent and worth solving.

## Interview prompts that expose hidden assumptions

“What does this tag uniquely identify?” “Can it be reused?” “What distinguishes a replaced sensor from a renamed channel?” “Which system owns the serial number?” “Is this timestamp measurement time, acquisition time or ingestion time?” “Are time-zone and leap/clock behavior relevant?” “Does a calibration cover the device, a particular range, a configuration or a particular procedure?” “When do revisions become effective?” “What is a revocation?” “What does missing data mean?” “Which conflicting source wins, and who authorized that rule?”

Ask the expert for **one counterexample to every rule**. A clean happy-path demonstration can hide the most valuable knowledge.

## Turn each answer into five artifacts

For every approved concept or rule, create: a definition and owner; an identity/mapping contract; a source-backed example; a SPARQL competency query; and a positive plus negative regression test. Preserve the expert's uncertainty as a decision needing review instead of converting it into an asserted fact.

Suggested decision record fields:

```yaml
question_id: CQ-001
question: Which observations need calibration evidence review?
owner: WORK_OWNER_TO_RESOLVE
sources: WORK_AUTHORITATIVE_SOURCES_TO_RESOLVE
identity_rule: WORK_REVIEW_REQUIRED
effectivity_rule: WORK_REVIEW_REQUIRED
unknown_behavior: retain_unknown_do_not_guess
expected_fixture_result: [T-102, T-103, T-104]
negative_cases: [covering_approved_replacement,_unapproved_replacement]
query_path: queries/05-expired.rq
review_status: proposed
approved_at: null
```

These markers are intentional work-side handoff hooks, not unfinished credentials or invitations to infer private connections.

## A useful proof that learning transferred

Have a second engineer, without the expert driving, find the affected observations, identify the historical component, explain unknown vs expired evidence, inspect the raw source and modify one query. Then introduce a counterexample and ask what should change. A successful teach-back is stronger evidence than a presentation attendance count.

Measure before and after: time to reproduce an investigation, number of unresolved identity mappings, share of answers with source evidence, number of SME-approved competency queries and percentage of negative-case tests passing. Establish baselines before promising an improvement percentage.
