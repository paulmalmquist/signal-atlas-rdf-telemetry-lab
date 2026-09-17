"""Generate deterministic source fixtures. No external connections or real hardware data."""
from __future__ import annotations
import csv, hashlib, json, math, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
SEED = 42
SNAPSHOT = '2026-09-14T00:00:00Z'

def write_json(name: str, value: object) -> None:
    (RAW / name).write_text(json.dumps(value, indent=2) + '\n')

def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    components = [
        {'id':'rig-01','label':'Aster ground-test rig','kind':'TestRig','parent':None,'revision':'A'},
        {'id':'fluid-loop','label':'Fluid loop','kind':'Assembly','parent':'rig-01','revision':'A'},
        {'id':'manifold-a','label':'Manifold A','kind':'Component','parent':'fluid-loop','revision':'C'},
        {'id':'manifold-b','label':'Manifold B','kind':'Component','parent':'fluid-loop','revision':'B'},
        {'id':'fixture','label':'Structural fixture','kind':'Component','parent':'rig-01','revision':'A'},
        {'id':'daq','label':'Acquisition enclosure','kind':'Component','parent':'rig-01','revision':'D'},
    ]
    sensors = [
        {'id':'P-101','label':'Primary pressure sensor','property':'Pressure','unit':'KiloPA','unit_label':'kPa','base':103.0,'amplitude':1.6,'component':'manifold-a'},
        {'id':'P-102','label':'Reference pressure sensor','property':'Pressure','unit':'KiloPA','unit_label':'kPa','base':102.5,'amplitude':1.2,'component':'manifold-b'},
        {'id':'P-103','label':'Auxiliary pressure sensor','property':'Pressure','unit':'KiloPA','unit_label':'kPa','base':101.8,'amplitude':1.0,'component':'manifold-a'},
        {'id':'T-201','label':'Loop temperature sensor','property':'Temperature','unit':'DEG_C','unit_label':'°C','base':23.0,'amplitude':0.9,'component':'manifold-a'},
        {'id':'V-301','label':'Fixture vibration sensor','property':'Acceleration','unit':'M-PER-SEC2','unit_label':'m/s²','base':0.15,'amplitude':0.035,'component':'fixture'},
        {'id':'AUX-401','label':'Supply voltage sensor','property':'Voltage','unit':'V','unit_label':'V','base':5.0,'amplitude':0.025,'component':'daq'},
    ]
    # Channel metadata has one intentional omission. Raw sample units remain explicit.
    channels = [{'id':'CH-'+s['id'],'sensor':s['id'],'label':s['label'],
                 'property':s['property'],'unit': None if s['id']=='AUX-401' else s['unit'],
                 'sample_rate_hz':10,'raw_tag':'DAQ/'+s['id'].replace('-','_')} for s in sensors]
    deployments=[]
    for s in sensors:
        deployments.append({'id':'DEP-'+s['id']+'-A','sensor':s['id'],'component':s['component'],
                            'valid_from':'2026-09-01T00:00:00Z',
                            'valid_to':'2026-09-12T00:00:00Z' if s['id']=='P-101' else '2026-10-01T00:00:00Z'})
    deployments.append({'id':'DEP-P-101-B','sensor':'P-101','component':'manifold-b',
                        'valid_from':'2026-09-12T00:00:00Z','valid_to':'2026-10-01T00:00:00Z'})
    certs=[]
    for s in sensors:
        if s['id']=='P-103': continue  # Unknown, not proven uncalibrated.
        certs.append({'id':'CAL-'+s['id'],'sensor':s['id'],'valid_from':'2026-09-01T00:00:00Z',
                      'valid_to':'2026-09-10T00:00:00Z' if s['id']=='P-101' else '2026-10-01T00:00:00Z',
                      'status':'approved','revision':'1'})
    runs=[]
    for i,day in enumerate([9,11,12,13]):
        start=datetime(2026,9,day,12,0,0,tzinfo=timezone.utc)
        runs.append({'id':f'T-{101+i}','label':['Baseline hold','Repeat hold','Relocated sensor','Follow-up hold'][i],
                     'start':start.isoformat().replace('+00:00','Z'),
                     'end':(start+timedelta(seconds=60)).isoformat().replace('+00:00','Z'),
                     'configuration':'CFG-A','phase':'hold','rig':'rig-01'})
    reqs=[{'id':'REQ-P','label':'Pressure evidence completeness','component':'fluid-loop','property':'Pressure','revision':'A'},
          {'id':'REQ-T','label':'Temperature evidence completeness','component':'fluid-loop','property':'Temperature','revision':'B'},
          {'id':'REQ-V','label':'Fixture evidence completeness','component':'fixture','property':'Acceleration','revision':'A'}]
    reports=[{'id':'RPT-'+r['id'],'run':r['id'],'label':'Evidence package '+r['id'],
              'requirements':['REQ-P','REQ-T','REQ-V'],'status':'draft','revision':'1'} for r in runs]
    issues=[{'id':'NCR-017','component':'manifold-a','label':'Synthetic inspection follow-up','state':'open','revision':'1'}]
    aliases=[{'system':'DAQ','source_id':c['raw_tag'],'canonical_sensor':c['sensor'],'mapping_status':'approved','mapping_version':'1'} for c in channels]
    write_json('plm.json', {'source':'Mock PLM','snapshot_at':SNAPSHOT,'components':components})
    write_json('registry.json', {'source':'Mock instrument registry','snapshot_at':SNAPSHOT,
                               'sensors':[{k:v for k,v in s.items() if k not in ('base','amplitude')} for s in sensors],
                               'channels':channels,'deployments':deployments,'aliases':aliases})
    write_json('calibration.json', {'source':'Mock calibration registry','snapshot_at':SNAPSHOT,'certificates':certs})
    write_json('tests.json', {'source':'Mock test execution','snapshot_at':SNAPSHOT,'runs':runs})
    write_json('qms.json', {'source':'Mock QMS','snapshot_at':SNAPSHOT,'issues':issues})
    write_json('requirements.json', {'source':'Mock requirements and reports','snapshot_at':SNAPSHOT,'requirements':reqs,'reports':reports})
    rng=random.Random(SEED)
    with (RAW/'telemetry.csv').open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=['sample_id','run_id','channel_id','event_time','t_seconds','value','unit','quality'])
        out.writeheader()
        for ri,run in enumerate(runs):
            start=datetime.fromisoformat(run['start'].replace('Z','+00:00'))
            for si,s in enumerate(sensors):
                for k in range(601):
                    t=k/10
                    value=s['base']+s['amplitude']*(math.sin(t/5+si)+0.1*rng.gauss(0,1))
                    # Visible pattern, deliberately not a physical model or operational limit.
                    if s['id']=='P-101' and ri==1 and 27<=t<=35:
                        value += 6.0 * math.sin((t-27)/8*math.pi)**2
                    quality='suspect' if s['id']=='P-103' and k%200==0 else 'good'
                    out.writerow({'sample_id':f"{run['id']}:{s['id']}:{k}",'run_id':run['id'],
                        'channel_id':'CH-'+s['id'],'event_time':(start+timedelta(seconds=t)).isoformat().replace('+00:00','Z'),
                        't_seconds':t,'value':round(value,5),'unit':s['unit'],'quality':quality})
    manifest={'synthetic':True,'seed':SEED,'snapshot_at':SNAPSHOT,'sample_rate_hz':10,
              'notice':'Entirely invented ground-test data. Not a physics simulation, acceptance criterion, or flight decision tool.',
              'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.iterdir()) if p.is_file() and p.name!='manifest.json'}}
    write_json('manifest.json',manifest)
    print('Generated 7 deterministic source fixtures and manifest; 14,424 samples.')

if __name__=='__main__': main()
