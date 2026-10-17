"""Documentation-only checks. Run from any directory with the pinned Python environment."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
def slug(s):
    s=re.sub(r'<[^>]+>','',s)
    s=re.sub(r'[^\w\- ]','',s.lower())
    return s.replace(' ','-')
def anchors(path):
    text=re.sub(r'```.*?```','',(path).read_text(),flags=re.S)
    counts={}; out=set()
    for h in re.findall(r'^#{1,6}\s+(.+?)\s*#*$',text,re.M):
        key=slug(h); n=counts.get(key,0);counts[key]=n+1
        out.add(key+(f'-{n}' if n else ''))
    out.update(re.findall(r'\bid="([^"]+)"',text))
    return out
checks=[]
for doc in [ROOT/'README.md',OUT/'FINAL_README_SHOWCASE_REPORT.md']:
    source=doc.read_text()
    assert source.count('```')%2==0, 'Unclosed fenced block'
    targets=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',source)+re.findall(r'(?:src|href)="([^"]+)"',source)
    for raw in targets:
        target=raw.strip('<>'); url=urlsplit(target)
        if url.scheme in ['http','https','mailto']: continue
        dest=(doc.parent/unquote(url.path)).resolve() if url.path else doc
        assert dest.is_relative_to(ROOT),target
        assert dest.exists(),target
        cursor=ROOT
        for part in dest.relative_to(ROOT).parts:
            assert part in [p.name for p in cursor.iterdir()],target
            cursor=cursor/part
        if url.fragment and dest.suffix=='.md': assert unquote(url.fragment) in anchors(dest),target
        checks.append({'document':str(doc.relative_to(ROOT)),'target':target,'status':'PASS'})
    for code in re.findall(r'```bash\n(.*?)```',source,re.S):
        subprocess.run(['bash','-n'],input=code,text=True,check=True)
manifest=json.loads((OUT/'charts/sources.json').read_text())
for path,digest in manifest['sources_sha256'].items(): assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
for filename,digest in manifest['figures'].items():
    path=OUT/'charts'/filename
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,filename
    tree=ET.parse(path)
    assert tree.getroot().attrib.get('viewBox'),filename
    for node in tree.iter():
        assert node.tag.split('}')[-1] not in ['script','foreignObject','image'],filename
        assert not any(k.lower().startswith('on') for k in node.attrib),filename
        for k,v in node.attrib.items():
            if k.endswith('href'): assert v.startswith('#'),filename
protected=json.loads((ROOT/'reports/v7-protected-artifacts.json').read_text())['sha256']
for path,digest in protected.items(): assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
# All pre-existing runtime, test, data, model and historical report files must match V7 publication.
changed=subprocess.check_output(['git','diff','82d458889f894c1e7ce74f8791ce2a7711971761','--name-only'],cwd=ROOT,text=True).splitlines()
assert all(p=='README.md' or p.startswith('docs/') for p in changed),changed
readme=(ROOT/'README.md').read_text()
for name in ['Advaith Ganesh','Abdul Malik','Ishaant Verma']: assert name in readme
for marker in ['84.69%','90%','91.67%','Sandbox · Synthetic Data','self-reported contribution allocation']:
    assert marker in readme,marker
result={'status':'PASS','scope':'Exact-case local links, Markdown fragments, shell syntax, safe self-contained SVG, chart source/output hashes, ten protected artifacts and documentation-only diff.',
 'link_count':len(checks),'links':checks,'svg_count':len(manifest['figures']),'protected_artifact_count':len(protected),
 'limitations':'Remote-link uptime and full accessibility conformance are not established by this script. GitHub rendering is checked separately in the actual browser.'}
(OUT/'showcase-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"PASS: {len(checks)} links/fragments, {len(manifest['figures'])} SVGs, 10 protected artifacts; documentation-only diff.")
