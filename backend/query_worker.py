"""Disposable query process. Local lab containment, not a public multi-tenant sandbox."""
import json, sys
from backend.build import load_dataset
from backend.query import execute_local

def main():
    try:
        payload=json.loads(sys.stdin.read(22000))
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CPU,(4,4))
            resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
        except ImportError:
            pass  # Windows: parent enforces wall-clock timeout; no RLIMIT claims.
        ds=load_dataset()
        import socket
        def deny(*args,**kwargs): raise PermissionError('Network access disabled in SPARQL worker.')
        socket.socket=deny
        socket.create_connection=deny
        data=execute_local(ds,payload['query'])
    except Exception as e:
        data={'error':str(e)[:500]}
    sys.stdout.write(json.dumps(data))

if __name__=='__main__': main()
