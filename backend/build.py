"""Map local source contracts to RDF and a separate indexed SQLite sample store."""
from __future__ import annotations
import csv, hashlib, json, sqlite3
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from rdflib import Dataset, Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from backend.seed import ROOT, RAW, SNAPSHOT
EX=Namespace('https://example.org/signal-atlas/')
SOSA=Namespace('http://www.w3.org/ns/sosa/')
PROV=Namespace('http://www.w3.org/ns/prov#')
UNIT=Namespace('http://qudt.org/vocab/unit/')
TIME=Namespace('http://www.w3.org/2006/time#')
GENERATED=ROOT/'data'/'generated'
GRAPH_FILE=GENERATED/'dataset.trig'
DB_FILE=GENERATED/'telemetry.sqlite'

def read(name): return json.loads((RAW/name).read_text())
def dt(s): return Literal(s,datatype=XSD.dateTime)
def u(s): return EX[s]
def add(g,s,p,o): g.add((u(s) if isinstance(s,str) and not isinstance(s,URIRef) else s,p,o))
def label(g,id,text): add(g,id,RDFS.label,Literal(text))
def typed(g,id,kind,text=None):
    add(g,id,RDF.type,kind)
    if text: label(g,id,text)
def load_dataset(path=GRAPH_FILE):
    ds=Dataset(default_union=True)
    ds.parse(str(path),format='trig')
    return ds

def build():
    GENERATED.mkdir(parents=True,exist_ok=True)
    ds=Dataset(default_union=True)
    for prefix,ns in [('ex',EX),('sosa',SOSA),('prov',PROV),('unit',UNIT),('time',TIME)]: ds.bind(prefix,ns)
    ds.graph(u('graph/ontology')).parse(str(ROOT/'ontology'/'model.ttl'),format='turtle')
    catalog=ds.graph(u('graph/catalog'))
    meta=[]
    sources=[('plm','plm.json'),('registry','registry.json'),('calibration','calibration.json'),
             ('tests','tests.json'),('qms','qms.json'),('requirements','requirements.json'),('telemetry','telemetry.csv')]
    for source,filename in sources:
        gid=u('graph/'+source)
        g=ds.graph(gid)
        source_id=u('source/'+filename)
        add(catalog,gid,PROV.wasDerivedFrom,source_id)
        add(catalog,gid,PROV.generatedAtTime,dt(SNAPSHOT))
        add(catalog,gid,EX.mappingVersion,Literal('1.0.0'))
        add(catalog,gid,EX.synthetic,Literal(True))
        typed(catalog,source_id,PROV.Entity,filename)
        digest=hashlib.sha256((RAW/filename).read_bytes()).hexdigest()
        add(catalog,source_id,EX.sha256,Literal(digest))
        add(catalog,source_id,EX.relativePath,Literal('data/raw/'+filename))
        meta.append({'id':source,'filename':filename,'graph':str(gid),'sha256':digest,
                     'snapshot_at':SNAPSHOT,'mapping_version':'1.0.0','synthetic':True})
    plm=read('plm.json'); reg=read('registry.json'); cal=read('calibration.json'); tests=read('tests.json')
    qms=read('qms.json'); req=read('requirements.json')
    g=ds.graph(u('graph/plm'))
    for c in plm['components']:
        typed(g,c['id'],EX[c['kind']],c['label'])
        # Explicit types avoid pretending RDFS inference is enabled.
        add(g,c['id'],RDF.type,EX.Component)
        add(g,c['id'],EX.revision,Literal(c['revision']))
        if c['parent']: add(g,c['id'],EX.partOf,u(c['parent']))
    g=ds.graph(u('graph/registry'))
    for s in reg['sensors']:
        typed(g,s['id'],SOSA.Sensor,s['label'])
        add(g,s['id'],SOSA.observes,EX[s['property']])
        add(g,s['id'],EX.serialNumber,Literal('SYN-'+s['id']))
    for c in reg['channels']:
        typed(g,c['id'],EX.Channel,c['label']+' channel')
        add(g,c['id'],EX.sensor,u(c['sensor']))
        add(g,c['id'],EX.rawTag,Literal(c['raw_tag']))
        add(g,c['id'],EX.sampleRateHz,Literal(c['sample_rate_hz'],datatype=XSD.integer))
        if c['unit']: add(g,c['id'],EX.unit,UNIT[c['unit']])
    for d in reg['deployments']:
        typed(g,d['id'],EX.Deployment,d['id'])
        add(g,d['id'],EX.sensor,u(d['sensor']))
        add(g,d['id'],EX.component,u(d['component']))
        add(g,d['id'],EX.validFrom,dt(d['valid_from']))
        add(g,d['id'],EX.validTo,dt(d['valid_to']))
    for i,a in enumerate(reg['aliases']):
        aid=f'mapping/{i+1}'
        typed(g,aid,EX.IdentityMapping,a['source_id'])
        for k in ['system','source_id','mapping_status','mapping_version']: add(g,aid,EX[k],Literal(a[k]))
        add(g,aid,EX.canonicalSensor,u(a['canonical_sensor']))
    g=ds.graph(u('graph/calibration'))
    for c in cal['certificates']:
        typed(g,c['id'],EX.Calibration,c['id'])
        add(g,c['id'],EX.sensor,u(c['sensor']))
        add(g,c['id'],EX.validFrom,dt(c['valid_from']))
        add(g,c['id'],EX.validTo,dt(c['valid_to']))
        add(g,c['id'],EX.status,Literal(c['status']))
        add(g,c['id'],EX.revision,Literal(c['revision']))
    g=ds.graph(u('graph/tests'))
    for r in tests['runs']:
        typed(g,r['id'],EX.TestRun,r['label'])
        add(g,r['id'],EX.start,dt(r['start'])); add(g,r['id'],EX.end,dt(r['end']))
        add(g,r['id'],EX.rig,u(r['rig']))
        add(g,r['id'],EX.phase,Literal(r['phase'])); add(g,r['id'],EX.configuration,Literal(r['configuration']))
    g=ds.graph(u('graph/qms'))
    for i in qms['issues']:
        typed(g,i['id'],EX.Nonconformance,i['label'])
        add(g,i['id'],EX.component,u(i['component'])); add(g,i['id'],EX.state,Literal(i['state']))
    g=ds.graph(u('graph/requirements'))
    for r in req['requirements']:
        typed(g,r['id'],EX.Requirement,r['label'])
        add(g,r['id'],EX.component,u(r['component'])); add(g,r['id'],EX.property,EX[r['property']])
        add(g,r['id'],EX.revision,Literal(r['revision']))
    for r in req['reports']:
        typed(g,r['id'],EX.Report,r['label'])
        add(g,r['id'],EX.forRun,u(r['run'])); add(g,r['id'],EX.status,Literal(r['status']))
        for requirement in r['requirements']: add(g,r['id'],EX.addresses,u(requirement))
    buckets=defaultdict(list)
    # Rebuild through a temporary database to avoid partially visible sample tables.
    temp=GENERATED/'telemetry.next.sqlite'
    if temp.exists(): temp.unlink()
    db=sqlite3.connect(temp)
    db.execute('CREATE TABLE samples (sample_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, channel_id TEXT NOT NULL, event_time TEXT NOT NULL, t_seconds REAL NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL, quality TEXT NOT NULL)')
    with (RAW/'telemetry.csv').open() as f:
        rows=list(csv.DictReader(f))
    db.executemany('INSERT INTO samples VALUES (:sample_id,:run_id,:channel_id,:event_time,:t_seconds,:value,:unit,:quality)',rows)
    db.execute('CREATE INDEX samples_lookup ON samples(run_id,channel_id,t_seconds)')
    db.commit(); db.close(); temp.replace(DB_FILE)
    for r in rows: buckets[r['run_id'],r['channel_id']].append(r)
    runs={r['id']:r for r in tests['runs']}; channels={c['id']:c for c in reg['channels']}
    g=ds.graph(u('graph/telemetry'))
    summaries=[]
    for (rid,cid),series in sorted(buckets.items()):
        run=runs[rid]; channel=channels[cid]; sensor=channel['sensor']
        matched=[d for d in reg['deployments'] if d['sensor']==sensor and d['valid_from']<=run['start'] and d['valid_to']>run['end']]
        if len(matched)!=1: raise ValueError(f'Expected one deployment covering {rid}/{cid}, got {len(matched)}')
        dep=matched[0]
        good=[float(r['value']) for r in series if r['quality']=='good']
        if not good: raise ValueError(f'No good data for {rid}/{cid}')
        units={r['unit'] for r in series}
        if len(units)!=1: raise ValueError(f'Mixed raw units in {rid}/{cid}; conversion requires an explicit versioned rule')
        # No silent unit conversion or registry repair.
        if channel['unit'] and channel['unit']!=next(iter(units)): raise ValueError('Registry/raw unit conflict')
        oid=f'obs/{rid}/{cid}'; window=f'window/{rid}'
        mean=round(sum(good)/len(good),6)
        typed(g,oid,SOSA.Observation,f'{rid} · {sensor} window mean')
        add(g,oid,RDF.type,EX.WindowSummary)
        for pred,obj in [(EX.run,u(rid)),(EX.channel,u(cid)),(EX.deployment,u(dep['id'])),
                         (SOSA.madeBySensor,u(sensor)),(SOSA.hasFeatureOfInterest,u(dep['component'])),
                         (SOSA.observedProperty,EX[channel['property']]),(SOSA.usedProcedure,EX['mean-window-v1']),
                         (EX.unit,UNIT[next(iter(units))]),(SOSA.phenomenonTime,u(window)),
                         (PROV.wasDerivedFrom,u('source/telemetry.csv'))]: add(g,oid,pred,obj)
        add(g,oid,SOSA.hasSimpleResult,Literal(Decimal(str(mean)),datatype=XSD.decimal))
        add(g,oid,SOSA.resultTime,dt(SNAPSHOT))
        add(g,oid,EX.windowStart,dt(run['start'])); add(g,oid,EX.windowEnd,dt(run['end']))
        add(g,oid,EX.goodSamples,Literal(len(good),datatype=XSD.integer))
        add(g,oid,EX.totalSamples,Literal(len(series),datatype=XSD.integer))
        add(g,oid,EX.minimum,Literal(Decimal(str(min(good))),datatype=XSD.decimal))
        add(g,oid,EX.maximum,Literal(Decimal(str(max(good))),datatype=XSD.decimal))
        add(g,oid,EX.rawSelector,Literal(json.dumps({'run_id':rid,'channel_id':cid},sort_keys=True)))
        typed(g,window,TIME.Interval)
        for edge,key in [(TIME.hasBeginning,'start'),(TIME.hasEnd,'end')]:
            instant=u(window+'/'+key)
            add(g,window,edge,instant); add(g,instant,RDF.type,TIME.Instant); add(g,instant,TIME.inXSDDateTime,dt(run[key]))
        summaries.append({'id':str(u(oid)),'run':rid,'sensor':sensor,'channel':cid,'component':dep['component'],
                          'mean':mean,'min':min(good),'max':max(good),'good_samples':len(good),'total_samples':len(series),
                          'unit':next(iter(units)),'start':run['start'],'end':run['end']})
    ds.serialize(destination=str(GRAPH_FILE),format='trig')
    meta_by_graph={m['graph']:m for m in meta}
    for graph in ds.graphs():
        if str(graph.identifier) in meta_by_graph: meta_by_graph[str(graph.identifier)]['triples']=len(graph)
    (GENERATED/'sources.json').write_text(json.dumps(meta,indent=2)+'\n')
    (GENERATED/'summaries.json').write_text(json.dumps(summaries,indent=2)+'\n')
    print(f'Built {len(ds)} union triples / {len(list(ds.quads()))} quads; {len(rows)} samples; {len(summaries)} summaries.')
    return ds

if __name__=='__main__': build()
