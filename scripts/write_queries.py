from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P='''PREFIX ex: <https://example.org/signal-atlas/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX unit: <http://qudt.org/vocab/unit/>
'''
expired='''  ?obs a sosa:Observation ; ex:run ?run ;
       sosa:madeBySensor ?sensor ; sosa:hasFeatureOfInterest ?component ;
       ex:windowStart ?start ; ex:windowEnd ?end .
  ?cert a ex:Calibration ; ex:sensor ?sensor ; ex:validTo ?expiry ; ex:status "approved" .
  FILTER(?expiry <= ?end)
  FILTER NOT EXISTS {
    ?cover a ex:Calibration ; ex:sensor ?sensor ; ex:status "approved" ;
           ex:validFrom ?from ; ex:validTo ?to .
    FILTER(?from <= ?start && ?to > ?end)
  }
'''
Q=[
('01-sensors','Meet your sensors','SELECT · triples · types','Start with physical instruments, not channel-name strings.',
 '''SELECT ?sensor ?label ?property WHERE {
  ?sensor a sosa:Sensor ; rdfs:label ?label ; sosa:observes ?property .
} ORDER BY ?sensor''',
 'Six instruments. The same ?sensor binds facts together, just like a join key. a abbreviates rdf:type.',
 'Add FILTER(?property = ex:Pressure) inside WHERE. You should get three pressure sensors.'),
('02-deployments','Where was it installed?','JOIN · identity · time','Find installations rather than assigning one timeless location to a sensor.',
 '''SELECT ?sensor ?component ?from ?to WHERE {
  ?deployment a ex:Deployment ; ex:sensor ?sensor ; ex:component ?component ;
              ex:validFrom ?from ; ex:validTo ?to .
} ORDER BY ?sensor ?from''',
 'Seven deployment records. P-101 moved from Manifold A to Manifold B on September 12.',
 'Filter for ex:P-101, then compare the two half-open intervals [from, to).'),
('03-bom','Follow the hardware hierarchy','PROPERTY PATH · +','Walk one or more direct BOM links.',
 '''SELECT ?component ?ancestor WHERE {
  VALUES ?component { ex:manifold-a ex:manifold-b }
  ?component ex:partOf+ ?ancestor .
} ORDER BY ?component ?ancestor''',
 'Four component/ancestor pairs. + means one or more hops; * would also include the starting component.',
 'Replace + with * and explain the two extra rows. A path match is not a newly stored inferred triple.'),
('04-observations','Numbers with context','OPTIONAL · typed values','Observe the difference between window summaries and raw samples.',
 '''SELECT ?run ?sensor ?mean ?unit ?goodSamples WHERE {
  ?obs a sosa:Observation ; ex:run ?run ; sosa:madeBySensor ?sensor ;
       sosa:hasSimpleResult ?mean ; ex:goodSamples ?goodSamples ; ex:channel ?channel .
  OPTIONAL { ?channel ex:unit ?unit }
} ORDER BY ?run ?sensor''',
 '24 summary observations, not 14,424 raw samples. AUX-401 has unbound metadata units, retained by OPTIONAL.',
 'Remove OPTIONAL and its braces. Four rows disappear; inner joins can hide incomplete metadata.'),
('05-expired','Which results need review?','FILTER NOT EXISTS · dates','Expired evidence is not proof the hardware failed.',
 'SELECT DISTINCT ?run ?sensor ?component ?expiry WHERE {\n'+expired+'} ORDER BY ?run',
 'Three results use P-101 after the old certificate expired, with no covering approved replacement in this snapshot.',
 'Use the what-if certificate experiment. A covering newer certificate must suppress a false expired-calibration alert.'),
('06-unknown','Find missing evidence','NOT EXISTS · unknown ≠ false','Distinguish unknown calibration from a known expired certificate.',
 '''SELECT DISTINCT ?run ?sensor WHERE {
  ?obs a sosa:Observation ; ex:run ?run ; sosa:madeBySensor ?sensor .
  FILTER NOT EXISTS { ?cert a ex:Calibration ; ex:sensor ?sensor }
} ORDER BY ?run ?sensor''',
 'Four P-103 results lack any certificate in this snapshot. Do not describe them as proven uncalibrated.',
 'Explain why “no matching triple” does not establish that a real-world calibration never happened.'),
('07-impact','Trace the evidence impact','MULTI-HOP JOIN · reports','Connect questionable evidence to draft reports and the relevant requirement.',
 '''SELECT DISTINCT ?run ?sensor ?component ?report ?requirement WHERE {
'''+expired+'''  ?report a ex:Report ; ex:forRun ?run ; ex:addresses ?requirement .
  ?requirement ex:property ex:Pressure .
} ORDER BY ?run''',
 'Three draft evidence packages and the pressure-evidence requirement need review. The graph identifies a review scope, not a disposition.',
 'Add ?report ex:status ?status and include ?status in SELECT. Where should human approval happen?'),
('08-provenance','Ask who supplied a fact','GRAPH · provenance','Keep source assertions attributable even when IDs join across systems.',
 '''SELECT ?graph ?predicate ?object WHERE {
  GRAPH ?graph { ex:P-101 ?predicate ?object }
} ORDER BY ?graph ?predicate''',
 'Facts about P-101 remain in the instrument-registry named graph. Provenance metadata for each graph is in the catalog graph.',
 'Replace ex:P-101 with ex:CAL-P-101. Explain why a graph name is not itself proof that a source is correct.'),
('09-construct','Build a review subgraph','CONSTRUCT · explicit rule','Derive a temporary set of review facts without changing the source dataset.',
 '''CONSTRUCT {
  ?obs a ex:ReviewCandidate ; ex:reviewReason "No covering approved calibration; prior evidence expired" ;
       ex:affectedReport ?report ; prov:wasDerivedFrom ?cert ; ex:rule ex:impact-rule-v1 .
} WHERE {
'''+expired+'''  ?report ex:forRun ?run .
}''',
 '15 derived triples for three observations. CONSTRUCT returns a graph; it does not INSERT it. No automatic OWL reasoning is running.',
 'Inspect prov:wasDerivedFrom and the rule identifier. What extra approval would publication of this graph require?'),
('10-contract','Is a channel missing its unit?','ASK · data contract','Use a Boolean check, then inspect the separate shape-validation report.',
 '''ASK {
  ?channel a ex:Channel .
  FILTER NOT EXISTS { ?channel ex:unit ?unit }
}''',
 'True in the baseline: CH-AUX-401 lacks a declared unit. Raw sample units are still present; the adapter does not silently fix the registry.',
 'Run the unit-repair experiment. Only the isolated copy is changed; source fixtures remain intact.'),
('11-comparable','Select comparable evidence','VALUES · validity · phase','Match property, unit, procedure, test phase and configuration before drilling into samples.',
 '''SELECT ?run ?sensor ?channel ?mean WHERE {
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
} ORDER BY ?run ?sensor''',
 'Five summaries: P-101 only at T-101, plus P-102 at every run. This is eligibility filtering, not proof of statistical comparability.',
 'Open a result in Telemetry. SPARQL finds the context; parameterized SQL retrieves the sample series.'),
('12-sources','Inventory the assertion sources','GRAPH · GROUP BY','Understand the dataset boundary before interpreting absence.',
 '''SELECT ?graph (COUNT(*) AS ?triples) WHERE {
  GRAPH ?graph { ?s ?p ?o }
} GROUP BY ?graph ORDER BY ?graph''',
 'Nine nonempty named graphs: ontology, six source registries, telemetry summaries, and a provenance catalog.',
 'Inspect the Sources page: file hash, snapshot time, version and source attribution. None proves the real world is complete.'),
]
catalog=[]
for id,title,concept,question,query,explanation,challenge in Q:
    text=P+'\n'+query+'\n'
    (ROOT/'queries'/f'{id}.rq').write_text(text)
    catalog.append(dict(id=id,title=title,concept=concept,question=question,query=text,explanation=explanation,challenge=challenge))
(ROOT/'queries'/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
