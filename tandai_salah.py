import datetime, json
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
st = json.load(open('data/status_lokal.json', encoding='utf-8'))
n = 0
for l in open('data/salah_channel.txt', encoding='utf-8'):
    u = l.split(' | ')[0].strip()
    if u.startswith('http'):
        st[u] = {'ok': False, 'height': 0, 'reason': 'SALAH_CHANNEL (cek user)', 'drm': False, 'ms': 0, 'checked': now, 'fails': 99}
        n += 1
json.dump(st, open('data/status_lokal.json', 'w', encoding='utf-8'))
print('ditandai salah channel:', n)
