"""Loopback-first teaching API and same-origin static UI."""
from contextlib import asynccontextmanager
import json
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from backend.build import ROOT, RAW, GRAPH_FILE, DB_FILE, build
from backend.query import run_isolated, MAX_QUERY
from backend import service

@asynccontextmanager
async def lifespan(app):
    if not GRAPH_FILE.exists() or not DB_FILE.exists(): build()
    yield

app=FastAPI(title='Signal Atlas — RDF Telemetry Lab',version='1.0.0',lifespan=lifespan,
            description='Synthetic-only, read-only local teaching application. Not a production query service.')
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])

@app.middleware('http')
async def headers(request:Request,call_next):
    # Browser CSRF barrier. No CORS and no network data-fetch capability.
    origin=request.headers.get('origin')
    if request.method=='POST' and origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):
        return JSONResponse({'detail':'Cross-origin requests are disabled.'},status_code=403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    return response

@app.get('/api/health')
def health(): return {'status':'ok','mode':'synthetic-local','version':'1.0.0','graph_ready':GRAPH_FILE.exists()}
@app.get('/api/bootstrap')
def bootstrap(): return service.bootstrap()

class QueryBody(BaseModel):
    query:str=Field(min_length=1,max_length=MAX_QUERY)

@app.post('/api/query')
def query(body:QueryBody):
    try: return run_isolated(body.query)
    except TimeoutError as e: raise HTTPException(408,str(e)) from e
    except ValueError as e: raise HTTPException(400,str(e)) from e

@app.api_route('/sparql',methods=['GET','POST'])
async def sparql_endpoint(request:Request,query:str|None=None):
    """Small SPARQL protocol subset: GET query or POST application/sparql-query.
    SELECT/ASK use standard SPARQL JSON; CONSTRUCT uses Turtle; 250-result cap.
    Dataset-selection parameters, updates and federation are intentionally absent.
    """
    if request.method=='POST':
        if request.headers.get('content-type','').split(';')[0]!='application/sparql-query':
            raise HTTPException(415,'POST requires application/sparql-query.')
        raw=await request.body()
        if len(raw)>MAX_QUERY: raise HTTPException(413,'Query exceeds 20 KB.')
        try: query=raw.decode('utf-8')
        except UnicodeDecodeError as e: raise HTTPException(400,'Query must be UTF-8.') from e
    if not query: raise HTTPException(400,'query is required')
    try: result=await run_in_threadpool(run_isolated,query)
    except TimeoutError as e: raise HTTPException(408,str(e)) from e
    except ValueError as e: raise HTTPException(400,str(e)) from e
    extra={'X-Result-Truncated':str(result['truncated']).lower()}
    if result['kind']=='CONSTRUCT': return Response(result['turtle'],media_type='text/turtle',headers=extra)
    return JSONResponse(result['standard'],media_type='application/sparql-results+json',headers=extra)

@app.get('/api/series')
def samples(run:str=Query(max_length=40),channel:str=Query(max_length=40)):
    result=service.series(run,channel)
    if not result['points']: raise HTTPException(404,'No series for that run/channel.')
    return result

@app.get('/api/validation')
def validation(): return service.validate_graph(service.dataset())
@app.get('/api/scenario/{name}')
def scenario(name:str):
    try: return service.scenario(name)
    except ValueError as e: raise HTTPException(404,str(e)) from e
@app.get('/api/source/{filename}')
def source(filename:str):
    allowed={s['filename'] for s in service.bootstrap()['sources']}
    if filename not in allowed: raise HTTPException(404,'Unknown source')
    return {'filename':filename,'text':(RAW/filename).read_text()[:16000],'truncated':(RAW/filename).stat().st_size>16000}
@app.get('/api/export/dataset')
def export(): return FileResponse(GRAPH_FILE,media_type='application/trig',filename='signal-atlas.trig')
@app.get('/')
def index(): return FileResponse(ROOT/'frontend'/'index.html')
app.mount('/assets',StaticFiles(directory=ROOT/'frontend'/'src'),name='assets')
