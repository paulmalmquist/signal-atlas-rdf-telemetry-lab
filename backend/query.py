"""Read-only SPARQL execution with parsed policy checks and a process boundary."""
from __future__ import annotations
import json, os, subprocess, sys, time
from itertools import islice
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parserutils import CompValue
import rdflib.plugins.sparql as sparql
from backend.build import ROOT, GRAPH_FILE
MAX_QUERY=20_000
MAX_ROWS=250
sparql.SPARQL_LOAD_GRAPHS=False

def walk(value):
    if isinstance(value,CompValue):
        yield value
        for v in value.values(): yield from walk(v)
    elif isinstance(value,(list,tuple)):
        for v in value: yield from walk(v)
    elif isinstance(value,dict):
        for v in value.values(): yield from walk(v)

def prepare(text):
    if not isinstance(text,str) or not text.strip(): raise ValueError('Enter a SPARQL query.')
    if len(text.encode('utf-8'))>MAX_QUERY: raise ValueError('Query exceeds the 20 KB limit.')
    try: parsed=translateQuery(parseQuery(text))
    except Exception as e: raise ValueError('SPARQL syntax error: '+str(e)[:350]) from e
    if parsed.algebra.name not in {'SelectQuery','AskQuery','ConstructQuery'}:
        raise ValueError('Only SELECT, ASK and CONSTRUCT are allowed. Updates and DESCRIBE are disabled.')
    for node in walk(parsed.algebra):
        if node.name=='ServiceGraphPattern': raise ValueError('SERVICE federation is disabled: local data only.')
        if 'datasetClause' in node and node['datasetClause']:
            raise ValueError('FROM and FROM NAMED are disabled: use GRAPH over the local dataset.')
    return parsed

def term(value):
    if value is None: return None
    if isinstance(value,URIRef): return {'type':'uri','value':str(value)}
    if isinstance(value,BNode): return {'type':'bnode','value':str(value)}
    out={'type':'literal','value':str(value)}
    if isinstance(value,Literal):
        if value.datatype: out['datatype']=str(value.datatype)
        if value.language: out['xml:lang']=value.language
    return out

def execute_local(ds,text):
    start=time.perf_counter(); result=ds.query(prepare(text))
    if result.type=='ASK':
        out={'kind':'ASK','boolean':bool(result.askAnswer),'standard':{'head':{},'boolean':bool(result.askAnswer)},'truncated':False}
    elif result.type=='CONSTRUCT':
        # CONSTRUCT materializes in RDFLib; worker resource limits bound this phase.
        triples=sorted(list(result.graph),key=lambda x:tuple(map(str,x)))
        if len(triples)>MAX_ROWS:
            from rdflib import Graph
            graph=Graph()
            for triple in triples[:MAX_ROWS]: graph.add(triple)
        else: graph=result.graph
        out={'kind':'CONSTRUCT','columns':['subject','predicate','object'],
             'rows':[{k:term(v) for k,v in zip(['subject','predicate','object'],triple)} for triple in triples[:MAX_ROWS]],
             'turtle':graph.serialize(format='turtle'),'truncated':len(triples)>MAX_ROWS}
    else:
        cols=[str(v) for v in result.vars]
        rows=list(islice(result,MAX_ROWS+1))
        bindings=[{k:term(v) for k,v in zip(cols,row) if v is not None} for row in rows[:MAX_ROWS]]
        out={'kind':'SELECT','columns':cols,'rows':bindings,'truncated':len(rows)>MAX_ROWS,
             'standard':{'head':{'vars':cols},'results':{'bindings':bindings}}}
    out['elapsed_ms']=round((time.perf_counter()-start)*1000,2)
    out['engine']='RDFLib 7.5.0 / SPARQL 1.1 / explicit union default graph'
    return out

def run_isolated(text,timeout=6.0):
    if len(text.encode('utf-8'))>MAX_QUERY: raise ValueError('Query exceeds the 20 KB limit.')
    try:
        result=subprocess.run([sys.executable,'-m','backend.query_worker'],cwd=ROOT,
            input=json.dumps({'query':text}),text=True,capture_output=True,timeout=timeout,
            env={**os.environ,'PYTHONHASHSEED':'0'})
    except subprocess.TimeoutExpired as e: raise TimeoutError('Query stopped at the six-second wall-clock limit.') from e
    if result.returncode!=0:
        raise ValueError('Query worker stopped, possibly at a resource limit. Simplify the query.')
    try: data=json.loads(result.stdout)
    except json.JSONDecodeError as e: raise ValueError('Query worker returned an invalid response.') from e
    if 'error' in data: raise ValueError(data['error'])
    return data
