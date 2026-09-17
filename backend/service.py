"""Read models for the app. All records and evidence are synthetic."""
from __future__ import annotations
import json, sqlite3
from functools import lru_cache
from rdflib import Dataset, Literal
from rdflib.namespace import RDF, RDFS
from backend.build import ROOT, RAW, GENERATED, GRAPH_FILE, DB_FILE, EX, UNIT, dt, load_dataset
from backend.query import execute_local
from backend.validation import validate_graph

def short(value):
    s=str(value)
    for ns,prefix in [(str(EX),'ex:'),(str(UNIT),'unit:'),('http://www.w3.org/ns/sosa/','sosa:'),('http://www.w3.org/ns/prov#','prov:'),('http://www.w3.org/2000/01/rdf-schema#','rdfs:'),('http://www.w3.org/1999/02/22-rdf-syntax-ns#','rdf:')]:
        if s.startswith(ns): return prefix+s[len(ns):]
    return s.rsplit('#',1)[-1].rsplit('/',1)[-1]

@lru_cache(maxsize=1)
def dataset(): return load_dataset()
@lru_cache(maxsize=1)
def catalog(): return json.loads((ROOT/'queries'/'catalog.json').read_text())
def query_id(id,ds=None):
    q=next(q for q in catalog() if q['id']==id)
    return execute_local(ds if ds is not None else dataset(),q['query'])

def triples(ds=None):
    ds=ds if ds is not None else dataset()
    rows=[]
    for s,p,o,g in ds.quads():
        if str(g).endswith('/ontology'): continue
        rows.append({'s':str(s),'p':str(p),'o':str(o),'kind':'literal' if isinstance(o,Literal) else 'uri',
                     'datatype':str(o.datatype) if isinstance(o,Literal) and o.datatype else None,'graph':str(g)})
    return sorted(rows,key=lambda t:(t['s'],t['p'],t['o'],t['graph']))

def series(run,channel):
    db=sqlite3.connect(f'file:{DB_FILE}?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        rows=[dict(row) for row in db.execute('SELECT sample_id,event_time,t_seconds,value,unit,quality FROM samples WHERE run_id=? AND channel_id=? ORDER BY t_seconds LIMIT 2000',(run,channel))]
    finally: db.close()
    return {'run':run,'channel':channel,'points':rows,'sample_count':len(rows),'source':'SQLite parameterized SELECT; original synthetic samples','downsampled':False}

def bootstrap(include_results=False):
    ds=dataset()
    registry=json.loads((RAW/'registry.json').read_text())
    findings={id:query_id(id) for id in ['05-expired','06-unknown','07-impact']}
    result={'app':'Signal Atlas','version':'1.0.0','synthetic':True,'snapshot_at':'2026-09-14T00:00:00Z',
        'notice':'Synthetic ground-test teaching data. No real company data, physics model or flight-readiness determination.',
        'counts':{'samples':14424,'triples':len(ds),'observations':24,'sensors':len(registry['sensors']),
                  'sources':7,'graphs':sum(1 for g in ds.graphs() if len(g))},
        'sensors':registry['sensors'],'channels':registry['channels'],
        'runs':json.loads((RAW/'tests.json').read_text())['runs'],
        'sources':json.loads((GENERATED/'sources.json').read_text()),
        'summaries':json.loads((GENERATED/'summaries.json').read_text()),
        'queries':catalog(),'findings':findings,'validation':validate_graph(ds),'triples':triples()}
    if include_results:
        result['saved_results']={q['id']:query_id(q['id']) for q in catalog()}
        result['saved_series']={r['id']+'|'+c['id']:series(r['id'],c['id']) for r in result['runs'] for c in result['channels']}
        result['raw_sources']={s['filename']:(RAW/s['filename']).read_text()[:16000] for s in result['sources']}
        result['scenarios']={s:scenario(s) for s in ['calibration','unit']}
        result['dataset_trig']=GRAPH_FILE.read_text()
    return result

def scenario(name):
    # Load an isolated copy; never mutate cached baseline or source files.
    ds=load_dataset()
    if name=='calibration':
        g=ds.graph(EX['graph/hypothesis'])
        cert=EX['HYPOTHETICAL-CAL-P-101']
        for p,o in [(RDF.type,EX.Calibration),(EX.sensor,EX['P-101']),(EX.status,Literal('approved')),
                    (EX.validFrom,dt('2026-09-10T00:00:00Z')),(EX.validTo,dt('2026-10-01T00:00:00Z')),
                    (RDFS.label,Literal('Hypothetical replacement evidence, not an actual certificate'))]: g.add((cert,p,o))
        result=query_id('05-expired',ds)
        return {'scenario':name,'hypothetical':True,'baseline_count':3,'scenario_count':len(result['rows']),
                'result':result,'message':'A covering replacement certificate removes expired-evidence matches in this isolated copy. This is NOT permission to backdate a real certificate. Missing P-103 evidence remains unknown.'}
    if name=='unit':
        ds.graph(EX['graph/hypothesis']).add((EX['CH-AUX-401'],EX.unit,UNIT.V))
        report=validate_graph(ds)
        return {'scenario':name,'hypothetical':True,'baseline_count':1,'scenario_count':len(report['violations']),
                'validation':report,'message':'One declared unit repairs the structural contract in this copy only. No source fixture was overwritten, and passing shapes is not a test acceptance decision.'}
    raise ValueError('Unknown scenario')
