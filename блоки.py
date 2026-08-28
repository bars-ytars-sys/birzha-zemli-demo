# -*- coding: utf-8 -*-
"""Блоки нововведений для карточки объекта и новых страниц."""
import html, io, json, pathlib

BASE = pathlib.Path(__file__).parent
EXTRA = json.load(io.open(BASE / 'данные-доп.json', encoding='utf-8'))

I = {
 'road': '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 21 8 3M20 21 16 3M12 5v3M12 11v3M12 17v3"/></svg>',
 'water': '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3s6 6.2 6 10a6 6 0 0 1-12 0c0-3.8 6-10 6-10Z"/></svg>',
 'chart': '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h16M7 16V9M12 16V5M17 16v-4"/></svg>',
 'down': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>',
 'up': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
 'shield': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 5 6v6c0 4.4 3 7.6 7 9 4-1.4 7-4.6 7-9V6Z"/><path d="m9 12 2 2 4-4"/></svg>',
 'bell': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 9a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6M13.7 20a2 2 0 0 1-3.4 0"/></svg>',
 'send': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21 3-9 18-2.5-7.5L2 11Z"/></svg>',
 'book': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2Z"/><path d="M8 7h7M8 11h7"/></svg>',
}


def mln(v):
    s = ('%.1f' % v).replace('.0', '').replace('.', ',')
    return s + ' млн ₽'


def money(v):
    return format(int(v), ',d').replace(',', ' ') + ' ₽'


def hours(h):
    ch = int(h)
    m = int(round((h - ch) * 60))
    return '%d ч%s' % (ch, ' %d мин' % m if m else '')


# ─────────────────────────────── карточка объекта

def market_line(o):
    """Цена относительно средней по региону."""
    m = o.get('market')
    if not m or not m['diff']:
        return ''
    low = m['diff'] < 0
    return ('<p class="market %s">%s<span>на %d%% %s средней по региону, '
            'сотка в %s стоит около %s</span></p>'
            % ('low' if low else 'high', I['down'] if low else I['up'], abs(m['diff']),
               'ниже' if low else 'выше', html.escape(o['region'].replace(' область', 'ской области')
                                                      if False else o['region']), money(m['mid'])))


def history_line(o):
    h = o.get('history') or []
    if not h:
        return ''
    x = h[0]
    return ('<p class="hist">%s Было %s, снижено %d дней назад</p>'
            % (I['down'], money(x['was']), x['days']))


def facts_block(o):
    """Дорога, вода, район. То, чего нет на универсальных досках."""
    r, w, d = o.get('road'), o.get('water'), o.get('district_stat')
    items = []
    if r:
        items.append((I['road'], 'Дорога',
                      'Москва %s, Петербург %s. До асфальта %d км'
                      % (hours(r['msk']), hours(r['spb']), r['asphalt_km'])))
    if w:
        zone = ('Береговая полоса 20 м общего пользования, водоохранная зона %d м: '
                'капитальное строительство ограничено' % w['zone']) if w['zone'] else 'Ограничений по воде нет'
        items.append((I['water'], 'Вода',
                      'До воды %d м, %s. %s' % (w['dist'], w['kind'], zone)))
    if d:
        items.append((I['chart'], 'Район',
                      '%d действующих баз в радиусе 30 км, средняя загрузка %d%%'
                      % (d['bases'], d['load'])))
    if not items:
        return ''
    li = ''.join('<li><span class="i">%s</span><div><b>%s</b><p>%s</p></div></li>' % it for it in items)
    return ('<div class="dbox rv"><h2 class="dbox-h">Что важно для базы отдыха</h2>'
            '<ul class="facts">%s</ul></div>' % li)


def project_block(o):
    """Что здесь можно построить плюс калькулятор окупаемости."""
    p = o.get('project')
    if not p:
        return ''
    land = (o.get('price') or (o.get('auction') or {}).get('current') or 0) / 1e6
    return '''<div class="dbox rv project" id="calc"
     data-unit="%(unit).3f" data-land="%(land).3f" data-check="%(check)d" data-load="%(load)d">
  <div class="pj-top">
    <div>
      <h2 class="dbox-h">Что здесь можно построить</h2>
      <p class="dbox-sub">Подобрано по площади и рельефу участка. Проект «%(name)s» из каталога
        готовых решений, цифры считаются по данным реализованных объектов.</p>
    </div>
    <span class="pj-fmt">%(fmt)s</span>
  </div>

  <div class="pj-grid">
    <label class="pj-ctrl">
      <span class="pj-l">Модулей на участке <b id="cu">%(units)d</b></span>
      <input type="range" id="units" min="2" max="24" value="%(units)d" step="1">
    </label>
    <label class="pj-ctrl">
      <span class="pj-l">Средний чек за ночь <b id="cc">%(checkfmt)s</b></span>
      <input type="range" id="check" min="4000" max="18000" value="%(check)d" step="500">
    </label>
    <label class="pj-ctrl">
      <span class="pj-l">Загрузка за год <b id="cl">%(load)d%%</b></span>
      <input type="range" id="load" min="25" max="75" value="%(load)d" step="1">
    </label>
  </div>

  <div class="pj-out">
    <div class="pj-cell"><span>Вложения с землёй</span><b id="o-total">—</b></div>
    <div class="pj-cell"><span>Выручка в год</span><b id="o-year">—</b></div>
    <div class="pj-cell"><span>Прибыль в год</span><b id="o-profit">—</b></div>
    <div class="pj-cell hi"><span>Окупаемость</span><b id="o-pay">—</b></div>
  </div>
  <p class="pj-note">Расчёт ориентировочный: маржа принята 42%%, инфраструктура 34%% от стоимости модулей.
    Точная модель считается на консультации.</p>
  <div class="pj-act">
    <button class="btn btn-p" type="button">Рассчитать проект под этот участок</button>
    <button class="btn btn-s" type="button">Смотреть проект «%(name)s»</button>
  </div>
</div>''' % {'unit': p['build'] / max(p['units'], 1), 'land': land, 'check': p['check'],
             'load': p['load'], 'units': p['units'], 'name': html.escape(p['name']),
             'fmt': html.escape(p['format']), 'checkfmt': money(p['check'])}


def partners_block():
    cells = ''.join('<li><b>%s</b><p>%s</p><span>%s</span></li>'
                    % (html.escape(p['name']), html.escape(p['what']), html.escape(p['from']))
                    for p in EXTRA['partners'])
    return ('<div class="dbox rv"><h2 class="dbox-h">Подрядчики под этот проект</h2>'
            '<p class="dbox-sub">Проверенные партнёры площадки, цены ориентировочные.</p>'
            '<ul class="partners">%s</ul></div>' % cells)


def article_block(o):
    """Статья базы знаний под ограничения конкретного участка."""
    tags = set(o.get('tags', [])) | {o.get('purpose', ''), o.get('category', '')}
    if o.get('water') and o['water']['zone']:
        pick = 'a2'
    elif 'Сельхоз' in (o.get('category', '') + o.get('purpose', '')):
        pick = 'a1'
    elif o['type'] == 'business':
        pick = 'a5'
    elif 'Грант' in tags:
        pick = 'a3'
    elif 'Подъезд круглый год' in tags:
        pick = 'a6'
    else:
        pick = 'a4'
    a = [x for x in EXTRA['articles'] if x['id'] == pick][0]
    return ('<a class="know rv" href="#"><span class="i">%s</span>'
            '<div><b>%s</b><p>%s</p></div><span class="min">%d мин</span></a>'
            % (I['book'], html.escape(a['title']), html.escape(a['lead']), a['min']))


def seller_block(o):
    s = o.get('seller') or {}
    ver = ('<span class="ver">%s Личность подтверждена</span>' % I['shield']) if s.get('verified') else ''
    return ('<div class="seller">'
            '<p class="av" aria-hidden="true">%s</p>'
            '<div><p class="sn">%s</p><p class="sr">%s, сделок на площадке %d</p>'
            '<p class="sr">Отвечает в среднем за %d мин</p>%s</div></div>'
            % (html.escape(s.get('name', 'А')[0]), html.escape(s.get('name', 'Александр')),
               html.escape(s.get('kind', 'Собственник')), s.get('deals', 0), s.get('answer', 30), ver))


def club_line(o):
    if not o.get('club'):
        return ''
    return ('<p class="club">%s Объект открыт для клуба на неделю раньше публикации</p>' % I['bell'])
