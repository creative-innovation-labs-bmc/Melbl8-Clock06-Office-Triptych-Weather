from pathlib import Path
import base64
import gzip
import re

PAYLOAD = Path('build/index.html.gz.b64')
html = gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip())).decode('utf-8')

old_link = '<link rel="stylesheet" href="./tight-spacing.css?v=20260806-tight1">'
new_layout = '''<link rel="stylesheet" href="./tight-spacing.css?v=20260806-fit3">
<style id="fit-stack-v3">
.message {
  top: 132px !important;
  bottom: 64px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-content: normal !important;
  grid-template-rows: none !important;
  gap: 4px !important;
  row-gap: 4px !important;
  overflow: visible !important;
}
.message > .line {
  flex: 0 0 auto !important;
  line-height: 1.08 !important;
  overflow: visible !important;
  padding-bottom: .04em !important;
}
</style>'''

if old_link not in html:
    raise SystemExit('Expected tight-spacing link was not found')
html = html.replace(old_link, new_layout, 1)

pattern = re.compile(
    r"function measure\(p,lines\)\{.*?\}\nfunction size\(p,lines\)\{",
    re.DOTALL,
)
replacement = '''function measure(p,lines){
  const snapshots=p.lines.map(l=>({text:l.typed.textContent,cursorHidden:l.cursor.hidden,fontSize:l.root.style.fontSize}));
  const previousVisibility=p.msg.style.visibility;
  p.msg.style.visibility='hidden';
  p.lines.forEach((l,index)=>{l.typed.textContent=lines[index]||' ';l.cursor.hidden=true});
  let lo=MIN_SIZE,hi=MAX_SIZE;
  for(let k=0;k<18;k++){
    const mid=(lo+hi)/2;
    p.lines.forEach(l=>{l.root.style.fontSize=mid+'px'});
    const widest=Math.max(...p.lines.map(l=>Math.ceil(l.root.scrollWidth)));
    if(widest<=PANEL_TEXT_W-12)lo=mid;else hi=mid;
  }
  const fitted=Math.floor(lo*100)/100;
  p.lines.forEach((l,index)=>{l.typed.textContent=snapshots[index].text;l.cursor.hidden=snapshots[index].cursorHidden;l.root.style.fontSize=snapshots[index].fontSize});
  p.msg.style.visibility=previousVisibility;
  return fitted;
}
function size(p,lines){'''
html, count = pattern.subn(replacement, html, count=1)
if count != 1:
    raise SystemExit(f'Expected one measure function replacement, found {count}')

html = html.replace(
    '<span class="typed">Keeping pace with Melbourne.</span>',
    '<span class="typed">與墨爾本時間相同。</span>',
    1,
)
html = html.replace(
    '<span class="typed">Following Melbourne by three hours.</span>',
    '<span class="typed">Jakarta tiga jam lebih lambat dari Melbourne.</span>',
    1,
)

required = [
    'id="fit-stack-v3"',
    'tight-spacing.css?v=20260806-fit3',
    'const widest=Math.max(...p.lines.map(l=>Math.ceil(l.root.scrollWidth)))',
    'padding-bottom: .04em !important',
]
for marker in required:
    if marker not in html:
        raise SystemExit(f'Missing required marker: {marker}')

Path('index.html').write_text(html, encoding='utf-8')
PAYLOAD.write_text(
    base64.b64encode(gzip.compress(html.encode('utf-8'), compresslevel=9, mtime=0)).decode('ascii') + '\n',
    encoding='utf-8',
)
print('Applied fit-stack-v3 to production source and payload')
