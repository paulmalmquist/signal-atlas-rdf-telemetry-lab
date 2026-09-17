"""Local browser smoke test; requires Playwright and a Chromium installation."""
from pathlib import Path
import json, os, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.app import app
client=TestClient(app)
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'; OUT.mkdir(exist_ok=True)
errors=[]; checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1080},device_scale_factor=1)
    page.on('pageerror',lambda err: errors.append(str(err)))
    # This build environment blocks Chromium loopback navigation by policy.
    # Exercise the exact UI assets through an in-process FastAPI transport instead.
    # No browser policy is changed. This is not a deployment/network test.
    def transport(url,options):
        response=client.request(options.get('method','GET'),url,headers=options.get('headers',{}),content=options.get('body'))
        return {'status':response.status_code,'body':response.text}
    page.expose_function('labTestTransport',transport)
    page.set_content('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="app"></div></body></html>')
    page.add_style_tag(content=(ROOT/'frontend'/'src'/'style.css').read_text())
    page.evaluate("""() => { window.fetch=async (url,options={})=>{const r=await window.labTestTransport(url,options);return {ok:r.status>=200&&r.status<300,status:r.status,json:async()=>JSON.parse(r.body),text:async()=>r.body};}; }""")
    page.add_script_tag(content=(ROOT/'frontend'/'src'/'app.js').read_text())
    page.get_by_role('heading',name='From signals to evidence.').wait_for()
    page.screenshot(path=str(OUT/'overview-desktop.png'),full_page=True)
    checks.append('Overview loads real backend counts and investigation links')
    page.get_by_role('button',name='Start the investigation',exact=True).click()
    page.get_by_text('3 rows',exact=True).wait_for(timeout=15000)
    page.screenshot(path=str(OUT/'sparql-desktop.png'),full_page=True)
    checks.append('Investigation runs actual SPARQL and returns three results')
    page.locator('#query-editor').fill('SELECT ?s WHERE { ?s a <http://www.w3.org/ns/sosa/Sensor> } ORDER BY ?s')
    page.get_by_role('button',name='Run query',exact=True).click()
    page.get_by_text('6 rows',exact=True).wait_for(timeout=15000)
    checks.append('Edited free-form SPARQL returns six sensors')
    page.get_by_role('button',name='Telemetry',exact=True).click()
    page.locator('#run-select').select_option('T-103')
    page.locator('#channel-select').select_option('CH-P-103')
    page.get_by_role('heading',name='Calibration evidence unknown',exact=True).wait_for()
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT/'telemetry-desktop.png'),full_page=True)
    checks.append('Telemetry selection updates values, historical context and evidence state')
    page.get_by_role('button',name='Graph explorer',exact=True).click()
    page.locator('#entity-search').fill('manifold-b')
    page.locator('#search-results').get_by_role('button',name='manifold-b',exact=True).click()
    page.get_by_role('heading',name='manifold-b',exact=True).wait_for()
    page.screenshot(path=str(OUT/'graph-desktop.png'),full_page=True)
    checks.append('Entity search and graph recenter follow actual RDF relationships')
    page.get_by_role('button',name='Evidence & quality',exact=True).click()
    page.get_by_role('button',name='Simulate covering evidence',exact=True).click()
    page.get_by_text('3 → 0',exact=True).wait_for()
    page.get_by_role('button',name='Simulate unit repair',exact=True).click()
    page.get_by_text('1 → 0',exact=True).wait_for()
    page.screenshot(path=str(OUT/'quality-desktop.png'),full_page=True)
    checks.append('Both what-if actions recompute isolated graphs')
    page.get_by_role('button',name='Learning path',exact=False).first.click()
    page.locator('.lesson-card').first.locator('summary').click()
    page.get_by_role('button',name='Predicate',exact=True).click()
    page.get_by_text('Correct.',exact=False).first.wait_for()
    page.locator('.lesson-card').first.get_by_role('button',name='Mark read',exact=True).click()
    checks.append('Knowledge checks and local learning progress work')
    page.get_by_role('button',name='Source catalog',exact=True).click()
    page.get_by_role('button',name='View source fixture',exact=True).first.click()
    page.get_by_role('dialog').wait_for()
    page.get_by_role('button',name='Close',exact=True).click()
    checks.append('Source fixture inspector opens and closes')
    # Phone viewport: assert document does not overflow horizontally on any page.
    page.set_viewport_size({'width':390,'height':844})
    for nav in ['Mission overview','Graph explorer','Telemetry','SPARQL workbench','Evidence & quality','Learning path','Source catalog']:
        page.get_by_role('button',name=nav,exact=False).first.click()
        page.wait_for_timeout(150)
        overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
        assert not overflow, f'Horizontal document overflow: {nav}'
    page.get_by_role('button',name='Mission overview',exact=True).click()
    page.screenshot(path=str(OUT/'overview-mobile.png'),full_page=True)
    checks.append('All seven pages fit 390px mobile width without document overflow')
    browser.close()
assert not errors,errors
(OUT/'browser-report.json').write_text(json.dumps({'transport':'Real FastAPI TestClient via browser binding; Chromium loopback navigation is blocked in the build environment. No network deployment test claimed.','checks':checks,'page_errors':errors},indent=2)+'\n')
print(json.dumps({'passed':len(checks),'page_errors':errors},indent=2))
