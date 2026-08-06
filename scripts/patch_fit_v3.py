from pathlib import Path
import base64
import gzip
import re

PAYLOAD = Path('build/index.html.gz.b64')
html = gzip.decompress(base64.b64decode(PAYLOAD.read_text().strip())).decode('utf-8')

scroll_width_marker = "const widest=Math.max(...p.lines.map(l=>Math.ceil(l.typed.scrollWidth+18)))"
font_boot_marker = "async function bootClock()"
if 'id="fit-stack-v5"' in html and scroll_width_marker in html and font_boot_marker in html:
    Path('index.html').write_text(html, encoding='utf-8')
    print('fit-stack-v5 already present')
    raise SystemExit(0)

# Keep the tight centred stack inline so mobile and production use the same layout.
html = re.sub(
    r'tight-spacing\.css\?v=[^"\']+',
    'tight-spacing.css?v=20260806-fit5',
    html,
    count=1,
)
html = re.sub(r'id="fit-stack-v[0-9]+"', 'id="fit-stack-v5"', html, count=1)
if 'id="fit-stack-v5"' not in html:
    inline_layout = '''<style id="fit-stack-v5">
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

html = html.replace('MAX_SIZE=116,MIN_SIZE=50', 'MAX_SIZE=116,MIN_SIZE=42', 1)

# getBoundingClientRect() includes the mobile stage transform. scrollWidth is native,
# transform-independent layout width, so mobile and 3840x804 produce identical fits.
bounding_marker = "const widest=Math.max(...p.lines.map(l=>Math.ceil(l.typed.getBoundingClientRect().width+18)))"
root_marker = "const widest=Math.max(...p.lines.map(l=>Math.ceil(l.root.scrollWidth)))"
if bounding_marker in html:
    html = html.replace(bounding_marker, scroll_width_marker, 1)
elif root_marker in html:
    html = html.replace(root_marker, scroll_width_marker, 1)
elif scroll_width_marker not in html:
    raise SystemExit('Expected a known widest-line marker')

# Wait for the self-hosted fonts before the first dynamic fit. Safari otherwise measures
# a fallback face and swaps to the wider PT Serif after sizing has completed.
old_startup = "scale();update(now());fetchWeather().then(()=>{refreshMelbourneWeatherLine();update(now())});requestAnimationFrame(tick);"
new_startup = '''let clockStarted=false;
function refitRenderedPanels(){
  if(!clockStarted)return;
  for(const p of Object.values(panels)){
    if(Array.isArray(p.rendered)&&p.rendered.length===3)size(p,p.rendered);
  }
}
async function bootClock(){
  scale();
  if(document.fonts){
    try{
      await Promise.allSettled([
        document.fonts.load('700 116px "PT Serif Local"'),
        document.fonts.load('600 25px "Open Sans Local"')
      ]);
      await Promise.race([
        document.fonts.ready,
        new Promise(resolve=>setTimeout(resolve,3000))
      ]);
    }catch(error){
      console.warn('Font preload unavailable',error);
    }
  }
  clockStarted=true;
  update(now());
  fetchWeather().then(()=>{
    refreshMelbourneWeatherLine();
    update(now());
    refitRenderedPanels();
  });
  requestAnimationFrame(tick);
}
if(document.fonts&&document.fonts.addEventListener){
  document.fonts.addEventListener('loadingdone',()=>requestAnimationFrame(refitRenderedPanels));
}
bootClock();'''
if old_startup in html:
    html = html.replace(old_startup, new_startup, 1)
elif font_boot_marker not in html:
    raise SystemExit('Expected startup block was not found')

required = [
    'id="fit-stack-v5"',
    'tight-spacing.css?v=20260806-fit5',
    scroll_width_marker,
    font_boot_marker,
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
print('Applied fit-stack-v5 mobile-safe production patch')
