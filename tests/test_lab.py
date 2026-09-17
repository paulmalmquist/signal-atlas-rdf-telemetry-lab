from __future__ import annotations
import hashlib, json, sqlite3, statistics, subprocess, sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD
from backend.build import ROOT, RAW, DB_FILE, GRAPH_FILE, EX, UNIT, SOSA, dt, build, load_dataset
from backend.service import catalog, query_id, bootstrap, dataset, scenario, series
from backend.query import execute_local, run_isolated, prepare
from backend.validation import validate_graph
from backend.app import app

@pytest.fixture(scope='session',autouse=True)
def baseline():
    build(); dataset.cache_clear()

@pytest.fixture
def client():
    with TestClient(app) as c: yield c

@pytest.mark.parametrize('qid,expected',[
 ('01-sensors',6),('02-deployments',7),('03-bom',4),('04-observations',24),
 ('05-expired',3),('06-unknown',4),('07-impact',3),('08-provenance',4),
 ('09-construct',15),('10-contract',True),('11-comparable',5),('12-sources',9)])
def test_all_lesson_answers(qid,expected):
    result=query_id(qid)
    assert result.get('boolean',len(result.get('rows',[])))==expected

def test_manifest_hashes():
    manifest=json.loads((RAW/'manifest.json').read_text())
    for file,digest in manifest['files'].items():
        assert hashlib.sha256((RAW/file).read_bytes()).hexdigest()==digest

def test_samples_are_separate_from_graph():
    with sqlite3.connect(DB_FILE) as db:
        assert db.execute('SELECT COUNT(*) FROM samples').fetchone()[0]==14424
    ds=load_dataset()
    assert len(set(ds.subjects(RDF.type,SOSA.Observation)))==24
    assert not any('sample_id' in str(x) for x in ds.all_nodes())

def test_mean_excludes_suspect_samples():
    points=series('T-101','CH-P-103')['points']
    good=[p['value'] for p in points if p['quality']=='good']
    ds=dataset(); obs=EX['obs/T-101/CH-P-103']
    assert len(points)==601 and len(good)==597
    assert float(ds.value(obs,SOSA.hasSimpleResult))==pytest.approx(statistics.mean(good),abs=1e-6)

def test_historical_installation_is_not_current_installation():
    ds=dataset()
    assert ds.value(EX['obs/T-102/CH-P-101'],SOSA.hasFeatureOfInterest)==EX['manifold-a']
    assert ds.value(EX['obs/T-103/CH-P-101'],SOSA.hasFeatureOfInterest)==EX['manifold-b']

def test_missing_vs_expired_are_separate():
    expired={r['sensor']['value'] for r in query_id('05-expired')['rows']}
    unknown={r['sensor']['value'] for r in query_id('06-unknown')['rows']}
    assert expired=={str(EX['P-101'])} and unknown=={str(EX['P-103'])}
    assert not (expired & unknown)

def test_hypothetical_certificate_suppresses_old_expiry_without_mutation():
    before=hashlib.sha256(GRAPH_FILE.read_bytes()).hexdigest()
    assert scenario('calibration')['scenario_count']==0
    assert len(query_id('05-expired')['rows'])==3
    assert hashlib.sha256(GRAPH_FILE.read_bytes()).hexdigest()==before

def test_unit_repair_is_scoped():
    report=validate_graph(dataset())
    assert not report['conforms']
    assert len(report['violations'])==1
    assert report['violations'][0]['focus']==str(EX['CH-AUX-401'])
    assert scenario('unit')['validation']['conforms']
    assert not validate_graph(dataset())['conforms']

def test_calibration_expiring_during_window_is_detected():
    ds=load_dataset(); g=ds.graph(EX['graph/calibration'])
    g.set((EX['CAL-P-102'],EX.validTo,dt('2026-09-09T12:00:30Z')))
    found=query_id('05-expired',ds)['rows']
    assert any(r['run']['value']==str(EX['T-101']) and r['sensor']['value']==str(EX['P-102']) for r in found)

def test_expiry_equal_to_last_sample_is_outside_half_open_interval():
    ds=load_dataset(); g=ds.graph(EX['graph/calibration'])
    g.set((EX['CAL-P-102'],EX.validTo,dt('2026-09-09T12:01:00Z')))
    found=query_id('05-expired',ds)['rows']
    assert any(r['run']['value']==str(EX['T-101']) and r['sensor']['value']==str(EX['P-102']) for r in found)

def test_calibration_start_is_inclusive():
    ds=load_dataset(); g=ds.graph(EX['graph/calibration'])
    g.set((EX['CAL-P-101'],EX.validFrom,dt('2026-09-09T12:00:00Z')))
    assert not any(r['run']['value']==str(EX['T-101']) for r in query_id('05-expired',ds)['rows'])

def test_unapproved_replacement_does_not_suppress_alert():
    ds=load_dataset(); g=ds.graph(EX['graph/calibration']); cert=EX['unapproved']
    for p,o in [(RDF.type,EX.Calibration),(EX.sensor,EX['P-101']),(EX.status,Literal('draft')),
                (EX.validFrom,dt('2026-09-01T00:00:00Z')),(EX.validTo,dt('2026-10-01T00:00:00Z'))]: g.add((cert,p,o))
    assert len(query_id('05-expired',ds)['rows'])==3

@pytest.mark.parametrize('query',[
 'SELECT * WHERE { SERVICE <http://127.0.0.1:1/> { ?s ?p ?o } }',
 'SELECT * WHERE { SERVICE SILENT <https://example.org/> { ?s ?p ?o } }',
 'SELECT * FROM <file:///etc/passwd> WHERE { ?s ?p ?o }',
 'SELECT * FROM NAMED <https://example.org/> WHERE { GRAPH ?g { ?s ?p ?o } }',
 'INSERT DATA { <urn:a> <urn:b> <urn:c> }',
 'DELETE WHERE { ?s ?p ?o }',
 'LOAD <https://example.org/>',
 'DESCRIBE <urn:a>',
])
def test_query_policy_rejects_fetch_and_writes(query):
    with pytest.raises(ValueError): prepare(query)

def test_service_word_in_literal_is_not_a_false_positive():
    result=execute_local(dataset(),'SELECT ("SERVICE FROM INSERT" AS ?note) WHERE {}')
    assert result['rows'][0]['note']['value']=='SERVICE FROM INSERT'

def test_actual_worker_returns_real_bindings():
    result=run_isolated(catalog()[0]['query'])
    assert result['kind']=='SELECT' and len(result['rows'])==6
    assert result['rows'][0]['sensor']['type']=='uri'

def test_result_cap_is_reported():
    result=execute_local(dataset(),'SELECT ?s ?p ?o WHERE { ?s ?p ?o }')
    assert len(result['rows'])==250 and result['truncated']

def test_oversized_query_is_rejected():
    with pytest.raises(ValueError): run_isolated('a'*20001)

def test_worker_wallclock_limit():
    with pytest.raises(TimeoutError): run_isolated('SELECT * WHERE { ?s ?p ?o }',timeout=0.001)

def test_health_and_static_assets(client):
    assert client.get('/api/health').json()['mode']=='synthetic-local'
    assert client.get('/').status_code==200
    assert 'no-referrer'==client.get('/').headers['Referrer-Policy']
    assert client.get('/assets/app.js').status_code==200

def test_api_query_and_standard_result_format(client):
    r=client.post('/api/query',json={'query':catalog()[0]['query']})
    assert r.status_code==200 and len(r.json()['rows'])==6
    r=client.post('/sparql',content='ASK { ?s ?p ?o }',headers={'Content-Type':'application/sparql-query'})
    assert r.status_code==200 and r.json()['boolean'] is True
    assert r.headers['content-type'].startswith('application/sparql-results+json')

def test_construct_protocol_returns_turtle(client):
    r=client.get('/sparql',params={'query':catalog()[8]['query']})
    assert r.status_code==200 and r.headers['content-type'].startswith('text/turtle')

def test_sql_injection_does_not_expand_scope(client):
    r=client.get('/api/series',params={'run':"T-101' OR 1=1 --",'channel':'CH-P-101'})
    assert r.status_code==404

def test_source_allowlist(client):
    assert client.get('/api/source/requirements.json').status_code==200
    assert client.get('/api/source/secrets.json').status_code==404

def test_cross_origin_and_unknown_host_rejected(client):
    assert client.post('/api/query',headers={'Origin':'https://untrusted.invalid'},json={'query':'ASK {}'}).status_code==403
    assert client.get('/api/health',headers={'Host':'untrusted.invalid'}).status_code==400

def test_api_syntax_error_is_actionable(client):
    r=client.post('/api/query',json={'query':'SELECT broken'})
    assert r.status_code==400 and 'syntax' in r.json()['detail'].lower()
