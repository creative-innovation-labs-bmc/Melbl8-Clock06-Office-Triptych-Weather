from pathlib import Path
import base64
import gzip
import re

PAYLOAD = Path('build/index.html.gz.b64')
html = gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip())).decode('utf-8')

typed_width_marker = "const widest=Math.max(...p.lines.map(l=>Math.ceil(l.typed.getBoundingClientRect().width+18)))"
if 'id="fit-stack-v4"' in html and typed_width_marker in html and 'MAX_SIZE=116,MIN_SIZE=42' in html:
    Path('index.html').write_text(html, encoding='utf-8')
    print('fit-stack-v4 already present')
    raise SystemExit(0)

# Keep the tight stack inline so it cannot be lost to stylesheet caching.
html = re.sub(
    r'tight-spacing\.css\?v=[^"\']+',
    'tight-spacing.css?v=20260806-fit4',
    html,
    count=1,
)
html = html.replace('id="fit-stack-v3"', 'id="fit-stack-v4"', 1)
if 'id="fit-stack-v4"' not in html:
    inline_layout = '''<style id="fit-stack-v4">
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
    html = html.replace('</head>', inline_layout + '</head>', 1)

# Long translations may need to go slightly below the old 50px floor.
html = html.replace('MAX_SIZE=116,MIN_SIZE=50', 'MAX_SIZE=116,MIN_SIZE=42', 1)

# Measure the actual rendered text spans, not the full-width flex line containers.
old_width_marker = "const widest=Math.max(...p.lines.map(l=>Math.ceil(l.root.scrollWidth)))"
if old_width_marker in html:
    html = html.replace(old_width_marker, typed_width_marker, 1)
elif typed_width_marker not in html:
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
    const widest=Math.max(...p.lines.map(l=>Math.ceil(l.typed.getBoundingClientRect().width+18)));
    if(widest<=PANEL_TEXT_W)lo=mid;else hi=mid;
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

# The old v3 threshold was based on a full-width container. Use the true panel width now.
html = html.replace('if(widest<=PANEL_TEXT_W-12)lo=mid;else hi=mid', 'if(widest<=PANEL_TEXT_W)lo=mid;else hi=mid', 1)

required = [
    'id="fit-stack-v4"',
    'tight-spacing.css?v=20260806-fit4',
    typed_width_marker,
    'MAX_SIZE=116,MIN_SIZE=42',
    'gap: 4px !important',
]
for marker in required:
    if marker not in html:
        raise SystemExit(f'Missing required marker: {marker}')

Path('index.html').write_text(html, encoding='utf-8')
PAYLOAD.write_text(
    base64.b64encode(gzip.compress(html.encode('utf-8'), compresslevel=9, mtime=0)).decode('ascii') + '\n',
    encoding='utf-8',
)
print('Applied fit-stack-v4 to production source and payload')
