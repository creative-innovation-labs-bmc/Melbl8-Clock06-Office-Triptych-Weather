from pathlib import Path
import base64, gzip
p=Path('build/index.html.gz.b64')
html=gzip.decompress(base64.b64decode(p.read_text().strip())).decode('utf-8')
repls={
  'tight-spacing.css?v=20260806-tight1':'tight-spacing.css?v=20260806-qc4',
  '<span class="typed">Keeping pace with Melbourne.</span>':'<span class="typed">與墨爾本時間相同。</span>',
  '<span class="typed">Following Melbourne by three hours.</span>':'<span class="typed">Jakarta tiga jam lebih lambat dari Melbourne.</span>',
}
for old,new in repls.items():
    if old not in html:
        raise SystemExit(f'missing expected text: {old}')
    html=html.replace(old,new,1)
for marker in ['tight-spacing.css?v=20260806-qc4','與墨爾本時間相同。','Jakarta tiga jam lebih lambat dari Melbourne.']:
    if marker not in html: raise SystemExit(f'missing marker {marker}')
Path('index.html').write_text(html,encoding='utf-8')
p.write_text(base64.b64encode(gzip.compress(html.encode(),compresslevel=9,mtime=0)).decode()+'\n',encoding='utf-8')
print('fallback and cache version patched')
