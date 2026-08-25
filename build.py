# Собирает демо в один файл: шрифты и картинки уходят внутрь html.
# Запуск: python build.py

import base64, io, re, pathlib

BASE = pathlib.Path(__file__).parent
OUT = BASE / 'demo-single-file.html'
MIME = {'.woff2': 'font/woff2', '.webp': 'image/webp'}

cache = {}

def to_data_uri(rel):
    if rel not in cache:
        path = BASE / rel
        cache[rel] = 'data:%s;base64,%s' % (MIME[path.suffix], base64.b64encode(path.read_bytes()).decode())
    return cache[rel]

html = io.open(BASE / 'index.html', encoding='utf-8').read()
html = re.sub(r'(?:img|font)/[\w.-]+\.(?:webp|woff2)', lambda m: to_data_uri(m.group(0)), html)

io.open(OUT, 'w', encoding='utf-8', newline='\n').write(html)
print('готово:', OUT.name, round(len(html.encode('utf-8')) / 1024), 'КБ,', len(cache), 'файла внутри')
