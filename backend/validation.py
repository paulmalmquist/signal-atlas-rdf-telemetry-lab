"""A deliberately small, explicit SHACL Core subset, not a general SHACL engine.
Supported: NodeShape, targetClass, direct-IRI property paths, min/maxCount,
datatype, nodeKind=IRI, message. Unsupported shape constructs fail closed.
"""
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF
from backend.build import ROOT
SH=Namespace('http://www.w3.org/ns/shacl#')
SUPPORTED={SH.targetClass,SH.property,SH.path,SH.minCount,SH.maxCount,SH.datatype,SH.nodeKind,SH.message}

def validate_graph(data):
    shapes=Graph().parse(str(ROOT/'ontology'/'shapes.ttl'),format='turtle')
    for s,p,o in shapes:
        if str(p).startswith(str(SH)) and p not in SUPPORTED:
            raise ValueError(f'Unsupported SHACL feature: {p}. Use an approved full SHACL engine.')
    report=Graph(); report.bind('sh',SH); root=BNode(); report.add((root,RDF.type,SH.ValidationReport))
    findings=[]; checks=0; focus_count=set()
    def fail(focus,path,shape,component,message):
        rid=BNode()
        for p,o in [(RDF.type,SH.ValidationResult),(SH.focusNode,focus),(SH.resultPath,path),
                    (SH.sourceShape,shape),(SH.sourceConstraintComponent,component),
                    (SH.resultSeverity,SH.Violation),(SH.resultMessage,Literal(message))]: report.add((rid,p,o))
        report.add((root,SH.result,rid))
        findings.append({'focus':str(focus),'path':str(path),'severity':'Violation',
                         'constraint':str(component).split('#')[-1],'message':message})
    for node_shape in shapes.subjects(RDF.type,SH.NodeShape):
        for target in shapes.objects(node_shape,SH.targetClass):
            for focus in sorted(set(data.subjects(RDF.type,target)),key=str):
                focus_count.add(str(focus))
                for ps in shapes.objects(node_shape,SH.property):
                    path=shapes.value(ps,SH.path)
                    if not isinstance(path,URIRef): raise ValueError('Only direct-IRI SHACL paths supported')
                    vals=list(data.objects(focus,path)); message=str(shapes.value(ps,SH.message) or f'Invalid {path}')
                    for pred,component in [(SH.minCount,SH.MinCountConstraintComponent),(SH.maxCount,SH.MaxCountConstraintComponent)]:
                        count=shapes.value(ps,pred)
                        if count is None: continue
                        checks+=1
                        if (pred==SH.minCount and len(vals)<int(count)) or (pred==SH.maxCount and len(vals)>int(count)):
                            fail(focus,path,ps,component,message)
                    datatype=shapes.value(ps,SH.datatype)
                    if datatype is not None:
                        checks+=len(vals)
                        for v in vals:
                            if not isinstance(v,Literal) or v.datatype!=datatype or v.ill_typed is True:
                                fail(focus,path,ps,SH.DatatypeConstraintComponent,message)
                    kind=shapes.value(ps,SH.nodeKind)
                    if kind is not None:
                        if kind!=SH.IRI: raise ValueError('Only sh:nodeKind sh:IRI supported')
                        checks+=len(vals)
                        for v in vals:
                            if not isinstance(v,URIRef): fail(focus,path,ps,SH.NodeKindConstraintComponent,message)
    report.add((root,SH.conforms,Literal(not findings)))
    return {'conforms':not findings,'violations':findings,'checks':checks,'focus_nodes':len(focus_count),
            'engine':'Signal Atlas bounded SHACL Core subset',
            'scope':'Structural contracts only. Does not establish calibration validity, truth, completeness, safety, or production readiness.',
            'report_turtle':report.serialize(format='turtle')}
