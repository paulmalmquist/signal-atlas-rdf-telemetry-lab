/* Signal Atlas training deck. Rebuild: npm install pptxgenjs@4.0.0 && node training/build_deck.js
   The runtime app does not depend on Node. Screenshot assets are supplied beside this file. */
const pptxgen = require('pptxgenjs');
const path = require('path');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Signal Atlas Lab';
pptx.subject = 'Hands-on RDF, telemetry context and SPARQL training with synthetic data';
pptx.title = 'Signal Atlas — From signals to evidence';
pptx.company = 'Synthetic teaching prototype';
pptx.lang = 'en-US';
pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'en-US' };
const C={bg:'0B1020', panel:'141C30', raised:'1C2640', line:'2C3956', text:'F3F5FF', muted:'ABB8D0', purple:'BCA3FF', mint:'7EDCC6', amber:'F1BC71', red:'F39AA4'};
const S=pptx.ShapeType;
const W=13.333,H=7.5;
let index=0;
function tx(sl,text,x,y,w,h,size=18,color=C.text,more={}){sl.addText(text,{x,y,w,h,fontFace:'Arial',fontSize:size,color,margin:0,breakLine:false,valign:'mid',paraSpaceAfterPt:7,...more});}
function box(sl,x,y,w,h,fill=C.panel,line=C.line,r=0.12){sl.addShape(S.roundRect,{x,y,w,h,rectRadius:r,radius:r,fill:{color:fill},line:{color:line,width:0.7}});}
function line(sl,x1,y1,x2,y2,color=C.line,arrow=false,width=1.4){sl.addShape(S.line,{x:x1,y:y1,w:x2-x1,h:y2-y1,line:{color,width,...(arrow?{beginArrowType:'none',endArrowType:'triangle'}:{})}});}
function pill(sl,text,x,y,w,color=C.purple){box(sl,x,y,w,.34,C.raised,C.raised);tx(sl,text,x+.12,y+.01,w-.24,.3,10,color,{bold:true,charSpacing:.6});}
function slide(kicker,title,subtitle='',source=''){
 const sl=pptx.addSlide();sl.background={color:C.bg};index++;
 tx(sl,'SIGNAL ATLAS',.55,.27,3,.25,10,C.purple,{bold:true,charSpacing:2});
 tx(sl,kicker.toUpperCase(),8.2,.27,4.55,.25,9,C.muted,{align:'right',charSpacing:1});
 tx(sl,title,.55,.85,12.2,.74,31,C.text,{bold:true,fit:'shrink'});
 if(subtitle)tx(sl,subtitle,.58,1.67,12.1,.58,15,C.muted,{valign:'top'});
 line(sl,.55,6.95,12.78,6.95);
 tx(sl,'SYNTHETIC LAB  /  NO OPERATIONAL ACCEPTANCE DECISIONS',.58,7.1,8,.16,7.5,C.muted,{charSpacing:.5});
 tx(sl,String(index).padStart(2,'0'),12.1,7.03,.6,.28,11,C.purple,{align:'right'});
 if(source)tx(sl,source,.58,6.64,11.8,.21,8.2,C.muted);
 return sl;
}
function card(sl,title,body,x,y,w,h,accent=C.purple){box(sl,x,y,w,h);sl.addShape(S.rect,{x:x+.18,y:y+.2,w:.045,h:.35,fill:{color:accent},line:{color:accent}});tx(sl,title,x+.38,y+.18,w-.58,.48,18,accent,{bold:true});tx(sl,body,x+.25,y+.82,w-.5,h-1.0,16,C.text,{valign:'top',breakLine:false});}
function code(sl,text,x,y,w,h,size=16){box(sl,x,y,w,h,'090E1B',C.line);tx(sl,text,x+.25,y+.2,w-.5,h-.4,size,C.mint,{fontFace:'Consolas',valign:'top',breakLine:false,paraSpaceAfterPt:0,fit:'shrink'});}
function screenshot(sl,name,x,y,w,h){const p=path.join(__dirname,name+'-screen.png');const bytes=require('fs').readFileSync(p);const iw=bytes.readUInt32BE(16),ih=bytes.readUInt32BE(20);const scale=Math.min(w/iw,h/ih);const sw=iw*scale,sh=ih*scale;sl.addImage({path:p,x:x+(w-sw)/2,y:y+(h-sh)/2,w:sw,h:sh});}
function note(sl,text){sl.addNotes(text);}
function small(sl,label,body,x,y,w,accent=C.purple){tx(sl,label,x,y,w,.4,16,accent,{bold:true});tx(sl,body,x,y+.54,w,1.3,15,C.text,{valign:'top'});}

// 01
{
let sl=slide('Hands-on training','From signals to evidence.','RDF + telemetry context + SPARQL, learned through a working application.');
pill(sl,'A REAL LOCAL APPLICATION',.6,2.45,2.75);tx(sl,'Signal\nAtlas',.62,3.02,5.2,2.12,58,C.text,{bold:true,breakLine:false});
const nodes=[['OBSERVATION',7.0,2.75],['SENSOR',9.95,2.75],['COMPONENT',7.0,4.55],['EVIDENCE',9.95,4.55]];
line(sl,8.4,3.16,9.94,3.16,C.purple,true,2);line(sl,7.85,3.6,7.85,4.54,C.mint,true,2);line(sl,10.8,3.6,10.8,4.54,C.amber,true,2);
for(const [t,x,y] of nodes){box(sl,x,y,2.15,.84);tx(sl,t,x+.12,y+.15,1.91,.48,14,C.text,{bold:true,align:'center'});}
tx(sl,'One investigation. Seven sources.\nTwelve executable questions.',.65,5.42,5.3,.8,20,C.muted);
note(sl,'Audience: a data architect or engineer who knows SQL and telemetry but is new to RDF/SPARQL. The outcome is practical literacy, not a claim of semantic-web mastery. Start the running app before presenting. All data is invented for a generic civil ground-test rig. This is not company engineering data or a physics model. Emphasize that the graph adds context and traceability; it does not replace experts or the raw sample store. Suggested session: 75–90 minutes with hands-on exercises.');
}
//02
{
let sl=slide('Start with a question','Which results need an evidence review?','A signal can look normal while the evidence supporting its interpretation is incomplete.');
card(sl,'THE INVESTIGATION','Find observations whose sensor calibration did not cover the full sampled window.',.6,2.45,5.7,2.35);
card(sl,'THE PAYOFF','Explain the sensor, its location at that time, the affected report and the exact source evidence.',6.5,2.45,6.2,2.35,C.mint);
box(sl,.6,5.12,12.1,1.05,C.raised,C.raised);tx(sl,'Not: “Is this hardware safe to fly?”',.9,5.3,11.5,.6,25,C.amber,{bold:true});
note(sl,'Open Mission overview and choose Start the investigation. Ask participants what information would be needed to answer correctly: observation time, physical sensor identity, certificate validity/approval, installation history, and report links. The lab makes those dependencies visible. It deliberately does not infer that a suspect measurement caused an issue or that a test passed or failed. This question is a candidate for an internal pilot; the actual company SME should decide whether calibration, configuration history or channel discovery is the best real starting point.');
}
//03
{
let sl=slide('The application','A workbench, not just a graph picture.','Seven pages connect exploration, query editing, raw values, evidence and learning.');
screenshot(sl,'overview',.5,2.25,8.5,4.12);
small(sl,'EXPLORE','Follow actual RDF edges and inspect their source graph.',9.3,2.48,3.25);
small(sl,'EXECUTE','Edit SPARQL and run it against the local RDFLib dataset.',9.3,4.1,3.25,C.mint);
note(sl,'Show the actual UI: Mission overview, Graph explorer, Telemetry, SPARQL workbench, Evidence & quality, Learning path and Source catalog. The dark interface is intended to transfer as a reference into the existing work app rather than impose a new application shell. Important distinction: the standalone HTML preview replays saved results and deliberately has a read-only query editor. The running FastAPI application executes arbitrary supported SPARQL through a bounded local worker. There are no external model calls and no company integrations.');
}
//04
{
let sl=slide('Architecture','Keep numeric scale and semantic context separate.','This is a design choice for the lab, not a limitation of RDF.');
card(sl,'7 SOURCE FIXTURES','PLM · registry · calibration\nTests · QMS · requirements\nTelemetry CSV',.6,2.58,3.25,2.8);
card(sl,'2 READ MODELS','RDF: identity, relationships,\nsummary observations, evidence\n\nSQLite: original samples',4.52,2.58,3.98,2.8,C.mint);
card(sl,'1 APPLICATION','FastAPI read API\nSPARQL + bounded SQL\nSeven-page front end',9.12,2.58,3.59,2.8);
line(sl,3.85,3.93,4.5,3.93,C.purple,true,2);line(sl,8.5,3.93,9.1,3.93,C.purple,true,2);
tx(sl,'At work: retain the existing governed warehouse / telemetry platform.',.8,5.75,11.9,.45,20,C.amber,{bold:true});
note(sl,'The mapper builds a local RDF dataset plus an indexed SQLite sample table from seven supplied source fixtures. The app is batch-built, not streaming. At work, the numeric branch should usually remain the existing governed BigQuery or time-series reader. The graph is a contextual read layer. Do not import every high-frequency sample as RDF merely because this is a graph exercise. Conversely, selected observation values can be useful in RDF; the example includes 24 summary observations. No live BigQuery adapter or remote graph endpoint has been implemented.');
}
//05
{
let sl=slide('RDF in one minute','A triple is a typed statement.','Subject → predicate → object. Resource identifiers are not just display labels.','Reference: W3C RDF 1.1 Concepts · w3.org/TR/rdf11-concepts/');
for(const [t,b,x,w,c]of[['SUBJECT','ex:P-101',.6,3.3,C.purple],['PREDICATE','sosa:observes',4.48,4.0,C.mint],['OBJECT','ex:Pressure',9.08,3.6,C.purple]]){box(sl,x,2.8,w,1.3);tx(sl,t,x+.2,3.0,w-.4,.26,11,c,{bold:true});tx(sl,b,x+.2,3.4,w-.4,.43,24,C.text,{bold:true});}
line(sl,3.93,3.55,4.43,3.55,C.muted,true);line(sl,8.52,3.55,9.03,3.55,C.muted,true);
code(sl,'ex:P-101  rdfs:label  "Primary pressure sensor" .',.6,4.65,12.1,.88,20);
tx(sl,'An IRI names a resource. A literal carries a value, such as text, a number or a date.',.65,5.85,12.0,.46,18,C.muted);
note(sl,'Explain RDF without jargon overload. A graph is a set of statements. In the first example, the subject and object are resources named by IRIs and the predicate is a relationship IRI. In the second, the object is a string literal. Prefixes such as ex: and sosa: are compact syntax for full IRIs, not a separate identity mechanism. Have learners find these statements in the graph inspector. RDF models relationships; it does not automatically know what internal names mean or which source is authoritative. Source: https://www.w3.org/TR/rdf11-concepts/');
}
//06
{
let sl=slide('Grain','14,424 samples. Just 24 observation summaries.','The graph points back to the precise sample window instead of hiding the raw data.');
for(const [num,label,x,c]of[['14,424','RAW SAMPLE ROWS',.7,C.muted],['24','RDF WINDOW SUMMARIES',4.95,C.mint],['928','BASELINE STATEMENTS',9.0,C.purple]]){tx(sl,num,x,2.75,3.65,1.0,49,c,{bold:true});tx(sl,label,x,3.91,3.7,.36,12,C.text,{bold:true,charSpacing:.7});}
code(sl,'observation → run + channel + time window\n            → sensor + component + procedure + unit\n            → source evidence + raw-data selector',.65,4.75,12.0,1.45,21);
note(sl,'There are four runs, six channels and 601 samples per run/channel. At 10 Hz from 0 through 60 seconds inclusive, that is 14,424 rows. Each run/channel produces one mean-window summary observation, for 24 total. Means use only good-quality samples. P-103 has 597 good samples out of 601; the raw chart retains the suspect samples rather than erasing them. These counts are baseline fixture facts, not scale claims. The graph has 928 distinct baseline statements and nine nonempty named graphs. The application retains a bound run/channel selector to retrieve original rows through SQL.');
}
//07
{
let sl=slide('Reuse vocabulary','Use familiar terms before inventing an ontology.','A small custom namespace handles the local relationships the exercise needs.','References: w3.org/TR/vocab-ssn/ · w3.org/TR/prov-o/ · qudt.org/vocab/unit/');
card(sl,'SOSA','Sensor\nObservation\nObserved property\nFeature of interest',.6,2.6,3.85,3.45);
card(sl,'PROV + UNITS','Source derivation\nGeneration time\n\nExplicit QUDT unit IRIs',4.72,2.6,3.87,3.45,C.mint);
card(sl,'ex: LAB TERMS','TestRun · Channel\nDeployment · Calibration\nRequirement · Report\npartOf · validity bounds',8.85,2.6,3.86,3.45,C.amber);
note(sl,'SOSA provides a compact vocabulary for sensors and observations. PROV provides reusable derivation/generation terms. The lab reuses QUDT unit identifiers but does not implement a dimensional-analysis or unit-conversion service. The ex: namespace contains the minimal application-specific types and relationships. Do not confuse reuse of vocabulary with complete ontology conformance or an approved company semantic model. No automatic reasoner is enabled. Sources: https://www.w3.org/TR/vocab-ssn/ ; https://www.w3.org/TR/prov-o/ ; https://qudt.org/vocab/unit/ .');
}
//08
{
let sl=slide('Identity','Sensor ≠ channel ≠ deployment.','The distinction prevents a current location from rewriting historical observations.');
card(sl,'PHYSICAL SENSOR','P-101\nThe same instrument persists across the move.',.6,2.65,3.83,2.77);
card(sl,'ACQUISITION CHANNEL','CH-P-101\nA stream definition with a raw tag and declared unit.',4.74,2.65,3.83,2.77,C.mint);
card(sl,'DEPLOYMENT','DEP-P-101-A / B\nWhere the instrument was installed, with effectivity.',8.88,2.65,3.83,2.77,C.amber);
tx(sl,'Source IDs need explicit mappings and owners. Similar names are not proof of identity.',.7,5.78,11.95,.55,19,C.text,{bold:true});
note(sl,'The physical instrument, its logical acquisition stream and its installation are different entities. The lab keeps their identifiers separate. Work-side source tags may be reused, renamed or reassigned; the mapping must account for time and source scope. Do not use owl:sameAs on fuzzy label matches. The fixture contains approved identity mappings, but it does not solve automated entity resolution. Ask the expert which system owns each identity and what happens during replacement, rework or acquisition reconfiguration. If that answer is uncertain, quarantine the mapping rather than manufacture a confident relationship.');
}
//09
{
let sl=slide('Historical context','The same sensor. A different component.','P-101 moves at 2026-09-12 00:00 UTC. Each observation preserves its measurement-time context.');
line(sl,1.1,3.55,12.1,3.55,C.line,false,4);
const data=[['T-101','SEP 09','manifold A',1.25],['T-102','SEP 11','manifold A',4.17],['T-103','SEP 12','manifold B',7.15],['T-104','SEP 13','manifold B',10.15]];
for(const [r,d,c,x]of data){sl.addShape(S.ellipse,{x:x+.68,y:3.43,w:.24,h:.24,fill:{color:x<6?C.purple:C.mint},line:{color:C.bg,width:2}});tx(sl,d,x,2.9,1.72,.34,13,C.muted,{align:'center'});tx(sl,r,x,3.95,1.72,.4,22,C.text,{align:'center',bold:true});tx(sl,c,x-.1,4.53,1.92,.4,15,x<6?C.purple:C.mint,{align:'center'});}
line(sl,6.4,2.64,6.4,5.14,C.amber,false,1.4);pill(sl,'MOVE EFFECTIVE',5.48,5.4,2.01,C.amber);
tx(sl,'Do not join every past observation to “where the sensor is today.”',.65,6.05,12.0,.36,19,C.text,{bold:true});
note(sl,'Walk through query 02 and then query 05. T-102 must still point to manifold A although the current/last deployment is manifold B. T-103 and T-104 belong to manifold B. The mapping uses event-time windows, not the time the dashboard happens to be opened. The fixture BOM itself is a snapshot; production configuration history requires additional revision/effectivity modeling. This example demonstrates one important historical relationship but is not a complete digital-twin history implementation. Ask the learner to describe a counterexample involving a sensor replacement or reused channel tag.');
}
//10
{
let sl=slide('Provenance','“Which source said this?” is a queryable question.','Source grouping, file hashes and mapping versions travel with the graph.','References: W3C RDF datasets and PROV-O · w3.org/TR/prov-o/');
code(sl,'GRAPH ?sourceGraph {\n  ex:P-101 ?predicate ?object .\n}',.65,2.63,6.1,2.04,23);
card(sl,'SOURCE CATALOG','Source file + SHA-256\nSnapshot time + mapping version\nSynthetic / live status\nAuthority remains a separate question',7.0,2.63,5.69,3.36,C.mint);
tx(sl,'A hash identifies bytes. It does not prove truth, completeness or permission.',.7,5.58,6.0,.78,20,C.amber,{bold:true});
note(sl,'Run query 08 and inspect the source catalog. The P-101 inventory assertions are in the registry graph. Nine nonempty named graphs exist in the baseline. The app explicitly uses a union default graph so unqualified patterns can join across them; do not assume a new SPARQL service uses that setting. Named graphs are a context mechanism, not access control by themselves. The source hash establishes which fixture bytes were mapped, not that the records are correct or complete. See https://www.w3.org/TR/rdf11-concepts/ and https://www.w3.org/TR/prov-o/ .');
}
//11
{
let sl=slide('Your first query','SPARQL joins by sharing variables.','Read each pattern as a statement with a blank to fill.','Reference: W3C SPARQL 1.1 Query Language · w3.org/TR/sparql11-query/');
code(sl,'PREFIX sosa: <http://www.w3.org/ns/sosa/>\n\nSELECT ?sensor ?property WHERE {\n  ?sensor a sosa:Sensor .\n  ?sensor sosa:observes ?property .\n}\nORDER BY ?sensor',.65,2.55,8.0,3.55,19);
small(sl,'?sensor','The same variable connects the two patterns.',9.0,2.73,3.5);
small(sl,'EXPECTED','Six sensor rows in the supplied baseline.',9.0,4.4,3.5,C.mint);
note(sl,'Run query 01, then edit it using this example. Reusing ?sensor is the join. The shorthand a means rdf:type. PREFIX expands the short names into full IRIs. SELECT chooses which bound variables are returned; ORDER BY stabilizes the displayed order. The UI preserves RDF term types in result metadata rather than treating every value as an untyped string. This query executes locally in RDFLib; the offline HTML preview deliberately cannot edit/run it. Ask the learner to add a label without excluding sensors lacking that label, using OPTIONAL. Source: https://www.w3.org/TR/sparql11-query/');
}
//12
{
let sl=slide('Traversal','A path finds reachable things; it does not infer a cause.','The + operator follows one or more edges. The * operator also permits zero hops.','Reference: SPARQL property paths · w3.org/TR/sparql11-query/');
code(sl,'SELECT ?component WHERE {\n  ?component ex:partOf+ ex:rig-01 .\n}',.65,2.6,7.15,1.73,25);
card(sl,'TRY IT','Run query 03: 4 descendants.\nChange + to *: 5 results, including rig-01 itself.',8.1,2.6,4.6,2.92,C.mint);
tx(sl,'Traversal ≠ automatic inference ≠ physical causality',.7,5.35,7.1,.9,25,C.amber,{bold:true});
note(sl,'The part hierarchy has four descendants beneath rig-01 in the relevant graph. Plus requires at least one edge; star permits a zero-length match and includes rig-01 itself. Property paths are useful for variable-depth relationships such as a bill of materials. This app does not materialize transitive closures or execute OWL/RDFS reasoning. Merely finding a path from a sensor to a nonconformance does not prove one caused the other. A SQL recursive query can also answer traversal questions; the choice of graph technology must be justified by the broader semantic and workload requirements.');
}
//13
{
let sl=slide('Temporal evidence','Coverage must include the whole sampled window.','Certificate validity is [validFrom, validTo). The final sample is still a measured instant.');
box(sl,.65,2.65,12.0,1.18);tx(sl,'validFrom ≤ first sample      AND      validTo > last sample',.93,2.93,11.4,.54,25,C.mint,{bold:true,align:'center'});
card(sl,'THE BASELINE','P-101 expires September 10.\nT-101 is covered.\nT-102 / T-103 / T-104 need review.',.65,4.15,5.84,2.1);
card(sl,'THE COUNTEREXAMPLE','An approved replacement covers the window.\nThe old expired record must not keep raising an alert.',6.75,4.15,5.9,2.1,C.amber);
note(sl,'Use a boundary example: a certificate ending at exactly the last sampled instant does not cover that instant because the upper bound is exclusive. A certificate starting exactly at the first sample does cover the start. The tests include both cases and an expiry inside the sample window. In real calibration policy, validity may depend on range, procedure, configuration, revocation and approval timing; these must come from the authoritative SME and records. The lab has simplified, explicitly stated semantics. It does not assume that an added certificate may legitimately be backdated.');
}
//14
{
let sl=slide('The key query','Find expired evidence, then exclude covering replacements.','Query 05 expresses the domain rule. The full executable query is in the app and training guide.');
code(sl,'?cert ex:sensor ?sensor ;\n      ex:validTo ?expiry ; ex:status "approved" .\nFILTER(?expiry <= ?end)\nFILTER NOT EXISTS {\n  ?cover ex:sensor ?sensor ; ex:status "approved" ;\n         ex:validFrom ?from ; ex:validTo ?to .\n  FILTER(?from <= ?start && ?to > ?end)\n}',.65,2.55,9.04,3.58,17.5);
tx(sl,'3',10.04,2.88,2.28,1.15,65,C.amber,{bold:true,align:'center'});tx(sl,'review candidates',9.94,4.18,2.55,.85,19,C.text,{align:'center'});
note(sl,'This is an excerpt, not a standalone query: the full file first binds each observation to its sensor, component, run and window. The expired certificate pattern is insufficient alone because histories may contain an old certificate even after a valid replacement exists. NOT EXISTS excludes any approved covering certificate. The actual result is P-101 in T-102, T-103 and T-104. The prototype fixture has simple certificate histories; a work implementation must handle supersession, partial coverage and overlapping/revoked records, and may need to deduplicate at observation grain. The domain rule is authored policy, not intrinsic RDF semantics.');
}
//15
{
let sl=slide('Evidence states','Expired, unknown and structurally incomplete are different.','Do not collapse uncertainty into a false “pass / fail” label.');
card(sl,'3 · EXPIRED EVIDENCE','P-101 observations have known expired records and no covering approved replacement.',.6,2.66,3.86,3.06,C.amber);
card(sl,'4 · UNKNOWN EVIDENCE','P-103 observations have no certificate in this snapshot. That is not proof calibration never happened.',4.74,2.66,3.86,3.06,C.purple);
card(sl,'1 · UNIT CONTRACT','CH-AUX-401 lacks a declared unit in the channel registry. Raw voltage samples still exist.',8.88,2.66,3.84,3.06,C.mint);
tx(sl,'These counts have different grains: observations, observations, channel.',.72,6.0,11.96,.35,16,C.muted);
note(sl,'Explain both evidence state and counting grain. Three and four are observation counts; one is a channel contract violation. These are not eight failed sensors. Query 06 is an absence check against this snapshot, not a universal real-world statement. If the source is incomplete, still syncing, stale or unauthorized, missing records must be interpreted in that context. Passing shape validation does not resolve calibration evidence and vice versa. This separation is one of the most valuable habits the lab should teach before any enterprise deployment.');
}
//16
{
let sl=slide('Raw-data drill-through','Move from a relationship to the original samples.','Select T-103 / CH-P-103 to see why “unknown evidence” does not erase the signal.');
screenshot(sl,'telemetry',.55,2.26,8.45,4.18);
small(sl,'601 SAMPLES','The detailed values remain in the numeric store.',9.35,2.7,3.18,C.mint);
small(sl,'597 GOOD','Four suspect samples are retained; the mean excludes them.',9.35,4.38,3.18,C.amber);
note(sl,'The screenshot is a real application capture. Change run and channel and observe the chart, context and evidence labels. The app uses parameterized SQL, not string interpolation, to retrieve the raw run/channel rows. The chart is not a predictive model or anomaly detector. The unusual pressure segment in one fixture is illustrative noise/shape, not a realistic engine transient. Discuss source quality flags, observed property, units, procedure, phase and configuration before comparing numeric windows. Metadata provides context for a decision; it does not substitute for the engineering analysis itself.');
}
//17
{
let sl=slide('Derived results','SELECT returns rows. ASK returns a Boolean. CONSTRUCT returns a graph.','A returned graph is not a write-back operation.','Reference: SPARQL query forms · w3.org/TR/sparql11-query/');
card(sl,'SELECT','Which observations?\n\nResult bindings you can inspect or tabulate.',.6,2.65,3.86,3.28);
card(sl,'ASK','Does a condition match?\n\nTrue / false against the selected dataset.',4.73,2.65,3.86,3.28,C.mint);
card(sl,'CONSTRUCT','What review graph follows?\n\n15 temporary triples for 3 review candidates.',8.86,2.65,3.86,3.28,C.amber);
note(sl,'Run query 09 and export the Turtle result. It describes review candidates but does not add facts to the baseline. The app has no SPARQL update endpoint. Ask participants what would be required to publish derived assertions in a work system: ownership, rule version, source provenance, permissions, approval, lifecycle/revocation and audit. Also explain ASK: false means the query found no matching pattern in its active dataset; it is not a universal negative about the world. No LLM creates these conclusions. Source: https://www.w3.org/TR/sparql11-query/');
}
//18
{
let sl=slide('Structural contracts','SHACL asks whether the graph satisfies declared shapes.','The lab evaluates an explicitly limited subset; it is not a full SHACL implementation.','Reference: W3C Shapes Constraint Language · w3.org/TR/shacl/');
code(sl,'ex:ChannelShape a sh:NodeShape ;\n  sh:targetClass ex:Channel ;\n  sh:property [\n    sh:path ex:unit ;\n    sh:minCount 1 ; sh:maxCount 1 ;\n    sh:nodeKind sh:IRI\n  ] .',.65,2.53,7.5,3.63,18);
small(sl,'BASELINE','One violation: a missing unit on CH-AUX-401.',8.55,2.7,3.98,C.amber);
small(sl,'LIMIT','Supported shapes only. Unknown constructs fail closed. No truth or safety guarantee.',8.55,4.37,3.98,C.mint);
note(sl,'This shape is a structural contract: each targeted channel must have exactly one unit IRI. The local evaluator supports NodeShape, targetClass, direct IRI property paths, minCount, maxCount, datatype, nodeKind IRI and messages. It rejects unsupported constructs rather than silently claiming they passed. The supplied optional pySHACL integration was not run because that package was unavailable in the build environment. A full approved engine is required for wider SHACL use. Calibration validity is implemented separately as a domain query. Source: https://www.w3.org/TR/shacl/');
}
//19
{
let sl=slide('What-if experiments','Change a copy. Preserve the evidence.','Both scenarios recompute an isolated graph; neither overwrites the baseline.');
card(sl,'COVERING CALIBRATION','3 → 0\n\nExpired-evidence matches disappear in the hypothesis only.\nP-103 remains unknown.',.65,2.6,5.85,3.56,C.amber);
card(sl,'DECLARE THE UNIT','1 → 0\n\nThe structural violation disappears in the hypothesis only.\nNo operational acceptance follows.',6.79,2.6,5.86,3.56,C.mint);
note(sl,'Run each action on Evidence & quality. The app loads a fresh dataset copy, adds explicitly hypothetical statements and recomputes the query or shape report. Run the original query again to prove its answer remains unchanged. A hypothetical covering certificate is not a claim that such a certificate exists or may be legally/operationally backdated. The unit scenario demonstrates the effect of a registry correction, not automatic permission to infer units from raw values. For work-side adoption, hypotheses need distinct provenance, access control and a reviewed path before any assertion becomes approved evidence.');
}
//20
{
let sl=slide('Practice','Three edits make the mental model stick.','Use the real app for these edits; the offline HTML only replays saved results.');
card(sl,'01 · PATH DEPTH','Query 03: change + to *.\n\nPredict the extra result before executing.',.6,2.65,3.86,3.2);
card(sl,'02 · MISSING DATA','Query 04: make the OPTIONAL unit relationship required.\n\nWhich observations vanish?',4.73,2.65,3.86,3.2,C.mint);
card(sl,'03 · SOURCE CONTEXT','Query 08: inspect the named graph and compare it with the source catalog.\n\nWhat does the hash prove?',8.86,2.65,3.86,3.2,C.amber);
note(sl,'Give learners time to make each prediction. Answers: changing plus to star adds rig-01 via a zero-hop path, taking four results to five. Requiring the previously optional channel unit removes four observations for CH-AUX-401, taking 24 to 20. The source hash identifies the fixture bytes used, not truth or completeness. Have the learner explain why an inner join can hide precisely the records that need data-quality review. The facilitator guide includes all twelve executable queries and expected answers.');
}
//21
{
let sl=slide('Fair comparison','Use a graph when relationships earn their complexity.','SQL can answer these questions too. The choice is not a contest between query languages.');
card(sl,'STAY WITH SQL','Large numeric scans\nStable tabular joins\nAggregates and time-series analysis\nExisting governed marts',.65,2.6,5.85,3.39,C.mint);
card(sl,'CONSIDER RDF','Shared cross-system identities\nReusable relationship meaning\nChanging traversal questions\nExplainable evidence links',6.79,2.6,5.86,3.39);
note(sl,'This is a design recommendation for the proposed work, not a performance finding. No benchmark of real company data was run. If the task is a straightforward aggregation of one good table, SQL is likely simpler. RDF can be valuable when the same cross-domain concepts and relationships recur across investigations and need portable meaning, provenance and traversal. The hybrid architecture keeps numerical scale where it belongs. Do not promise subsecond answers, reduced cost or less engineering effort until those are measured on the real workload with representative permissions and source coverage.');
}
//22
{
let sl=slide('Possible internal pilots','Expand by useful question, not by system count.','These are hypotheses to validate with the SME, not claims about existing company capability.');
small(sl,'CALIBRATION IMPACT','Which downstream evidence needs review?',.68,2.62,5.5,C.amber);
small(sl,'CHANNEL DISCOVERY','Find signals by property, unit and historical component.',6.86,2.62,5.55,C.mint);
small(sl,'COMPARISON ELIGIBILITY','Select windows with approved contextual compatibility.',.68,4.53,5.5,C.purple);
small(sl,'REPORT LINEAGE','Trace a report or requirement to exact source observations.',6.86,4.53,5.55,C.mint);
note(sl,'Use these as candidate application ideas rather than a roadmap commitment. Ask which one currently causes repeated manual investigation or depends most heavily on the single expert. Choose a narrow, read-only pilot with an accountable owner and a known expected answer. Configuration-aware comparison needs more than shared units: procedure, phase, environment, hardware revision, uncertainty and engineering judgment may matter. Requirement evidence may have complex acceptance logic. Start by selecting eligible evidence and explaining lineage, not by automating an operational judgment. See docs/OPPORTUNITIES.md for proof points and caveats.');
}
//23
{
let sl=slide('Capture the expertise','Turn the expert’s explanation into executable knowledge.','The target is a second person who can reproduce the answer and explain its limits.');
const labels=['QUESTION','DEFINITION','MAPPING','QUERY','TEST'];
for(let i=0;i<labels.length;i++){const x=.65+i*2.45;box(sl,x,2.96,2.16,1.0);tx(sl,labels[i],x+.12,3.22,1.92,.43,15,i%2?C.mint:C.purple,{bold:true,align:'center'});if(i<4)line(sl,x+2.17,3.48,x+2.43,3.48,C.muted,true);}
box(sl,.65,4.65,12.0,1.41,C.raised,C.raised);tx(sl,'For every rule, capture a counterexample and an owner.',.93,4.9,11.44,.57,25,C.amber,{bold:true,align:'center'});
note(sl,'Use the expert-capture guide. Start with one competency question, walk backward through authoritative source records, resolve identity and event-time assumptions, then ask for counterexamples. Each approved answer should produce a definition with an owner, a mapping contract, a source-backed synthetic case, an executable SPARQL query and positive/negative tests. Preserve uncertainty and disputed source authority explicitly rather than turning it into an asserted fact. A second person should complete the investigation while the expert observes rather than drives. This reduces dependence on tacit knowledge without pretending the technology replaces domain expertise.');
}
//24
{
let sl=slide('Work-side adoption','Transfer the synthetic prototype one way.','Preserve existing Paul OS, governed data access and company security patterns.');
card(sl,'DISCOVER','Read the real work repository.\nResolve source owners, IDs, event time, effectivity and coverage.\nDo not invent connections.',.6,2.64,3.86,3.3);
card(sl,'GATE','Authentication and authorization\nGraph / sample / inference access\nQuery limits and audit\nApproved source slice',4.74,2.64,3.86,3.3,C.amber);
card(sl,'PILOT','Curated read-only questions\nEvidence and freshness labels\nSME-reviewed counterexamples\nSecond-person teach-back',8.88,2.64,3.84,3.3,C.mint);
note(sl,'No company integration is present. backend/adapters.py is a typed extension contract, not a working BigQuery or source-system connector. The handoff document contains explicit WORK_* discovery hooks. Resolve them only inside the approved work environment, using actual local evidence and owners. Do not sync work code, private ontologies, credentials, real fixture extracts or company URLs back into a personal repository, even a private one. Named graphs are not authorization. Derived edges, counts and exports can leak restricted information. Free-form SPARQL requires a separate permission and execution design before real data.');
}
//25
{
let sl=slide('Delivery evidence','What has been checked—and what has not.','Use the validation report rather than inferring production readiness from a polished interface.');
card(sl,'EXECUTED','43 automated tests passed\n9 browser interaction checks\nAll seven pages at phone width\nActual RDFLib queries and SQL samples',.65,2.6,5.85,3.46,C.mint);
card(sl,'NOT CLAIMED','Remote GitHub repository or deployment\nLive company adapters or authentication\nDocker / GitHub Actions execution\nFull SHACL conformance or pySHACL run',6.79,2.6,5.85,3.46,C.amber);
note(sl,'The browser checks used exact front-end assets connected to real FastAPI handlers through an in-process bridge. Chromium loopback navigation is blocked by policy in the build environment, so this was not a hosted/network browser test; no policy was disabled. Automated tests cover query outcomes, source hashes, historical deployment, window boundaries, replacement evidence, isolated scenarios, input restrictions and API behavior. Direct dependencies are pinned but not a full transitive lock. Remote repository creation was unavailable through the connected tools; a complete local repository/bundle and authenticated private-publication script are supplied. See docs/VALIDATION_REPORT.md and artifacts for exact evidence.');
}
//26
{
let sl=slide('First session and references','Start with the app. Finish with a teach-back.','The best next step is a narrow investigation with the single expert—not an enterprise ontology project.');
card(sl,'FIRST SESSION','Open the lab → run query 05\nFollow the historical deployment\nInspect original samples and sources\nChange one query and explain the result',.65,2.55,6.1,3.63);
tx(sl,'PRIMARY REFERENCES',7.09,2.69,5.31,.35,13,C.purple,{bold:true,charSpacing:1});
const refs=['RDF: w3.org/TR/rdf11-concepts/','SPARQL: w3.org/TR/sparql11-query/','SOSA: w3.org/TR/vocab-ssn/','PROV: w3.org/TR/prov-o/','SHACL: w3.org/TR/shacl/'];
refs.forEach((r,i)=>tx(sl,r,7.09,3.3+i*.5,5.36,.31,14,C.muted));
note(sl,'Close by having someone other than the SME explain an answer: which observations are review candidates; where the sensor was installed then; what evidence is missing versus expired; how to retrieve the original samples; and why no operational acceptance follows. Full references and source URLs are in docs/SOURCES.md. The training guide includes eight labs, a capstone, a teach-back rubric and every query. The complete project includes the offline HTML tour, running Python app, raw fixtures, ontology/shapes, query library, tests, local Git bundle and work-side handoff. Choose one real competency question and owner before expanding.');
}

pptx.writeFile({ fileName: path.join(__dirname,'Signal_Atlas_Training.pptx') });
