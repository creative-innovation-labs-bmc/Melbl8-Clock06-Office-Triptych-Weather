from pathlib import Path
import base64
import gzip
import re

payload_path = Path('build/index.html.gz.b64')
html = gzip.decompress(base64.b64decode(payload_path.read_text().strip())).decode('utf-8')

old_constants = "const SIDE_MS=30000,CENTRE_MS=60000,RIGHT_OFFSET=15000,WEATHER_REFRESH=600000;"
new_constants = "const SIDE_MS=30000,CENTRE_MS=60000,LEFT_OFFSET=5000,RIGHT_OFFSET=20000,WEATHER_REFRESH=600000;"
if old_constants not in html:
    raise SystemExit('Expected timing constants were not found')
html = html.replace(old_constants, new_constants, 1)

old_panels = "const panels={left:panel('left',SIDE_MS,0),centre:panel('centre',CENTRE_MS,0),right:panel('right',SIDE_MS,RIGHT_OFFSET)};"
new_panels = "const panels={left:panel('left',SIDE_MS,LEFT_OFFSET),centre:panel('centre',CENTRE_MS,0),right:panel('right',SIDE_MS,RIGHT_OFFSET)};"
if old_panels not in html:
    raise SystemExit('Expected panel timing setup was not found')
html = html.replace(old_panels, new_panels, 1)

relation_patch = r'''function localCity(o){const names={'hong-kong':'香港',shanghai:'上海',beijing:'北京',jakarta:'Jakarta',manila:'Maynila',singapore:'Singapore',bangkok:'กรุงเทพฯ','ho-chi-minh-city':'Thành phố Hồ Chí Minh','kuala-lumpur':'Kuala Lumpur',macau:'澳門',auckland:'Auckland',wellington:'Wellington',sydney:'Sydney',brisbane:'Brisbane'};return names[o.id]||o.city}
function localDuration(minutes,lang){const n=Math.abs(minutes),h=Math.floor(n/60),m=n%60;if(lang==='zh-Hant')return(h?h+'小時':'')+(m?m+'分鐘':'');if(lang==='zh-Hans')return(h?h+'小时':'')+(m?m+'分钟':'');if(lang==='id')return(h?h+' jam':'')+(m?(h?' ':'')+m+' menit':'');if(lang==='fil')return(h?h+' oras':'')+(m?(h?' at ':'')+m+' minuto':'');if(lang==='th')return(h?h+' ชั่วโมง':'')+(m?(h?' ':'')+m+' นาที':'');if(lang==='vi')return(h?h+' giờ':'')+(m?(h?' ':'')+m+' phút':'');if(lang==='ms')return(h?h+' jam':'')+(m?(h?' ':'')+m+' minit':'');if(!h)return m+' '+(m===1?'minute':'minutes');if(!m)return h+' '+(h===1?'hour':'hours');return h+' '+(h===1?'hour':'hours')+' '+m+' minutes'}
function relationLine(p,o,date){const diff=offsetMinutes(date,o.tz)-offsetMinutes(date,mel.tz),city=localCity(o),duration=localDuration(diff,o.lang),v=((slot(p,date)%3)+3)%3;if(diff===0){if(o.lang==='zh-Hant')return city+'與墨爾本時間相同。';if(o.lang==='zh-Hans')return city+'与墨尔本时间相同。';if(o.lang==='id')return'Waktu di '+city+' dan Melbourne sama.';if(o.lang==='fil')return'Magkapareho ang oras sa '+city+' at Melbourne.';if(o.lang==='th')return'เวลาใน'+city+'และเมลเบิร์นตรงกัน';if(o.lang==='vi')return city+' và Melbourne cùng giờ.';if(o.lang==='ms')return'Waktu di '+city+' dan Melbourne adalah sama.';return[city+' and Melbourne share the same time.',city+' and Melbourne keep the same beat.','The clocks match in '+city+' and Melbourne.'][v]}if(diff>0){if(o.lang==='zh-Hant')return city+'比墨爾本快'+duration+'。';if(o.lang==='zh-Hans')return city+'比墨尔本快'+duration+'。';if(o.lang==='id')return city+' '+duration+' lebih cepat dari Melbourne.';if(o.lang==='fil')return city+' ay nauuna ng '+duration+' sa Melbourne.';if(o.lang==='th')return city+'เร็วกว่าเมลเบิร์น '+duration;if(o.lang==='vi')return city+' sớm hơn Melbourne '+duration+'.';if(o.lang==='ms')return city+' mendahului Melbourne sebanyak '+duration+'.';return city+' is '+duration+' ahead of Melbourne.'}if(o.lang==='zh-Hant')return city+'比墨爾本慢'+duration+'。';if(o.lang==='zh-Hans')return city+'比墨尔本慢'+duration+'。';if(o.lang==='id')return city+' '+duration+' lebih lambat dari Melbourne.';if(o.lang==='fil')return city+' ay nahuhuli ng '+duration+' sa Melbourne.';if(o.lang==='th')return city+'ช้ากว่าเมลเบิร์น '+duration;if(o.lang==='vi')return city+' chậm hơn Melbourne '+duration+'.';if(o.lang==='ms')return city+' ketinggalan '+duration+' berbanding Melbourne.';return city+' is '+duration+' behind Melbourne.'}
function weatherLabel'''

html, count = re.subn(
    r"function relationLine\(p,o,date\)\{.*?\}\nfunction weatherLabel",
    relation_patch,
    html,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Relative-time function patch failed')

melbourne_patch = r'''function fullWeekday(shortName){return{Mon:'Monday',Tue:'Tuesday',Wed:'Wednesday',Thu:'Thursday',Fri:'Friday',Sat:'Saturday',Sun:'Sunday'}[shortName]||shortName}
function melbourneThird(o,pt){const w=weather.get(o.id),part=dayPart(pt.h),day=fullWeekday(pt.weekday),options=[];if(w){const condition=weatherLabel(w.code).toLowerCase(),adjective=weatherAdjective(w.code),temperature=Math.round(w.temperature);options.push('A '+temperatureWord(w.temperature)+', '+adjective+' '+part+'.');options.push(temperature+'° and '+condition+' outside.');options.push(day+' '+part+', with '+adjective+' skies.')}options.push(day+' '+part+' in Melbourne.');options.push('The '+part+' is moving along.');return options[pt.m%options.length]}
function message'''

html, count = re.subn(
    r"function melbourneThird\(o,pt\)\{.*?\}\nfunction message",
    melbourne_patch,
    html,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('Melbourne observation patch failed')

checks = [
    'LEFT_OFFSET=5000',
    'RIGHT_OFFSET=20000',
    'Magkapareho ang oras sa ',
    'Waktu di ',
    'เวลาใน',
    ' cùng giờ.',
    'fullWeekday',
    "condition+' outside.'",
]
for check in checks:
    if check not in html:
        raise SystemExit(f'Missing expected patch marker: {check}')
if 'On Melbourne time today.' in html:
    raise SystemExit('Old Melbourne-centric same-time copy remains')

events = []
for second in range(120):
    if second % 60 == 0:
        events.append((second, 'centre'))
    if (second - 5) % 30 == 0:
        events.append((second, 'left'))
    if (second - 20) % 30 == 0:
        events.append((second, 'right'))
event_seconds = [second for second, _ in events]
if len(event_seconds) != len(set(event_seconds)):
    raise SystemExit(f'Transition overlap detected: {events}')
if min(b - a for a, b in zip(event_seconds, event_seconds[1:])) < 5:
    raise SystemExit(f'Transitions are too close: {events}')

Path('index.html').write_text(html, encoding='utf-8')
compressed = gzip.compress(html.encode('utf-8'), compresslevel=9, mtime=0)
payload_path.write_text(base64.b64encode(compressed).decode('ascii') + '\n', encoding='utf-8')
print('Patched production payload. Events:', events)
