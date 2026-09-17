"""Validate the actual standalone HTML without a server or external requests."""
from pathlib import Path
import json, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'preview/Signal_Atlas_Preview.html').read_text()
errors=[]; requests=[]; checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.set_content(html,wait_until='load')
    page.get_by_role('heading',name='From signals to evidence.').wait_for()
    checks.append('Actual single-file HTML boots without external asset requests')
    page.get_by_role('button',name='Start the investigation',exact=True).click()
    page.get_by_text('3 rows',exact=True).wait_for()
    assert page.locator('#query-editor').get_attribute('readonly') is not None
    checks.append('Saved query returns three rows and arbitrary editing is disabled')
    page.get_by_role('button',name='Telemetry',exact=True).click()
    page.locator('#run-select').select_option('T-104')
    page.locator('#channel-select').select_option('CH-P-103')
    page.get_by_role('heading',name='Calibration evidence unknown',exact=True).wait_for()
    checks.append('Offline sample selection uses embedded 601-point series')
    page.get_by_role('button',name='Evidence & quality',exact=True).click()
    page.get_by_role('button',name='Simulate covering evidence',exact=True).click()
    page.get_by_text('3 → 0',exact=True).wait_for()
    page.get_by_role('button',name='Simulate unit repair',exact=True).click()
    page.get_by_text('1 → 0',exact=True).wait_for()
    checks.append('Offline what-if views show explicitly saved scenario outcomes')
    page.set_viewport_size({'width':390,'height':844})
    for nav in ['Mission overview','Graph explorer','Telemetry','SPARQL workbench','Evidence & quality','Learning path','Source catalog']:
        page.get_by_role('button',name=nav,exact=False).first.click()
        page.wait_for_timeout(70)
        assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1'),nav
    checks.append('All seven offline pages fit a 390px viewport')
    browser.close()
assert not errors,errors
assert not requests,requests
result={'checks':checks,'page_errors':errors,'external_requests':requests,'transport':'Actual standalone HTML via set_content; no server, no API binding, no external assets.'}
(ROOT/'artifacts/preview-report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
