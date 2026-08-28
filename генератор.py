# -*- coding: utf-8 -*-
"""Собирает страницы демо из данных: главная, каталог, объявления, проверка земли."""

import io, json, pathlib, re, html
from блоки import (market_line, history_line, facts_block, project_block,
                   partners_block, article_block, seller_block, club_line)
from страницы import requests_page, cabinet_page, roadmap_page

BASE = pathlib.Path(__file__).parent
DATA = json.load(io.open(BASE / 'данные.json', encoding='utf-8'))
T = lambda n: io.open(BASE / 'шаблоны' / (n + '.html'), encoding='utf-8').read()

TYPE_NAME = {'uchastok': 'Участок', 'business': 'Готовый бизнес', 'stroy': 'Строится'}
SVG = {
 'eye': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
 'tel': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.4 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2Z"/></svg>',
 'clock': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 'heart': '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1a5.5 5.5 0 1 0-7.8 7.8l8.8 8.8 8.8-8.8a5.5 5.5 0 0 0 0-7.8Z"/></svg>',
 'gavel': '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m14 4 6 6-3 3-6-6zM11 7 4 14l3 3 7-7M3 21h10"/></svg>',
 'check': '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/></svg>',
}

def money(v):
    return format(v, ',d').replace(',', ' ') + ' ₽'

def area_text(sot):
    if sot >= 100:
        ga = sot / 100
        ga = ('%.1f' % ga).replace('.0', '').replace('.', ',')
        return '%d соток · %s га' % (sot, ga)
    return '%d соток' % sot

def img_paths(o, base):
    n = o['img']
    small = '%simg/%s.webp' % (base, n)
    big = '%simg/%s%s.webp' % (base, n, '-big' if n.startswith('gen/') else '')
    return small, big

def rank(o):
    r = o.get('check', 0) * 9 + min(o.get('views', 0), 900) // 30
    if o.get('priority'): r += 40
    return r

def spark(o):
    seed = sum(ord(c) for c in o['id'])
    base = max(4, o.get('views', 60) // 24)
    return ','.join(str(base + (seed * (i + 3) % 11) + i * 2) for i in range(7))

def card(o, base=''):
    small, _ = img_paths(o, base)
    flag = ''
    if o.get('priority'):
        flag = '<span class="badge gold">Приоритет</span>'
    elif o['deal'] == 'auction':
        flag = '<span class="badge">%s Аукцион</span>' % SVG['gavel']
    elif o['type'] == 'stroy':
        flag = '<span class="badge">Строится</span>'
    elif o['type'] == 'business':
        flag = '<span class="badge">Готовый бизнес</span>'
    elif o.get('check', 0) >= 5:
        flag = '<span class="badge">Проверено</span>'

    if o['deal'] == 'auction':
        a = o['auction']
        price = ('<p class="price">%s <span>ставок %d, шаг %s</span></p>'
                 % (money(a['current']), a['bids'], money(a['step'])))
    elif o['price']:
        per = o['price'] // o['area'] if o['area'] else 0
        extra = o.get('revenue') or (o.get('ready') if o['type'] == 'stroy' else None) or ('%s ₽ за сотку' % format(per, ',d').replace(',', ' '))
        price = '<p class="price">%s <span>%s</span></p>' % (money(o['price']), html.escape(extra))
    else:
        price = '<p class="price">Цена по запросу <span>%s</span></p>' % html.escape(o.get('revenue') or 'уточняется у продавца')

    tags = ''.join('<li>%s</li>' % html.escape(t) for t in o['tags'][:2])
    tags += '<li class="ok">Проверка %d из 5</li>' % o.get('check', 0)

    return '''<article class="card rv" data-type="%(type)s" data-deal="%(deal)s" data-tags="%(tagstr)s" data-price="%(price_num)d" data-views="%(views)d" data-days="%(days)d" data-rank="%(rank)d">
  <a class="ph" href="%(base)sobject/%(id)s.html">
    <img src="%(small)s" width="560" height="385" alt="%(alt)s" loading="lazy">
    %(flag)s
    <button class="fav" type="button" aria-label="В избранное" aria-pressed="false">%(heart)s</button>
  </a>
  <div class="body">
    %(price)s
    <h3 class="ttl"><a href="%(base)sobject/%(id)s.html">%(title)s</a></h3>
    <p class="meta">%(area)s · %(region)s, %(district)s</p>
    <ul class="tags">%(tags)s</ul>
    <div class="stats">
      <span class="s">%(eye)s<b data-count="%(views)d">0</b></span>
      <span class="s">%(tel)s<b>%(phones)d</b></span>
      <svg class="spark" width="76" height="22" viewBox="0 0 76 22" data-spark="%(spark)s" role="img" aria-label="Просмотры за 7 дней"></svg>
    </div>
  </div>
</article>''' % {
        'type': o['type'], 'deal': o['deal'], 'tagstr': html.escape(' '.join(o['tags'])),
        'price_num': o['price'] or (o['auction']['current'] if o['deal'] == 'auction' else 0),
        'views': o['views'], 'days': o['days'], 'rank': rank(o), 'base': base, 'id': o['id'],
        'small': small, 'alt': html.escape(o['title']), 'flag': flag, 'heart': SVG['heart'],
        'price': price, 'title': html.escape(o['title']), 'area': area_text(o['area']),
        'region': html.escape(o['region']), 'district': html.escape(o['district'].replace(' район', '')),
        'tags': tags, 'eye': SVG['eye'], 'tel': SVG['tel'], 'phones': o['phones'], 'spark': spark(o)}


def page(title, desc, content, base='', nav_active=''):
    head = T('head')
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % html.escape(title), head, count=1, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(">)', r'\g<1>%s\g<2>' % html.escape(desc), head, count=1)
    head = head.replace('href="assets/', 'href="%sassets/' % base).replace('src="assets/', 'src="%sassets/' % base)
    header = T('header')
    header = header.replace('href="#catalog"', 'href="%scatalog.html"' % base)
    header = header.replace('href="#rank"', 'href="%srequests.html"' % base)
    header = header.replace('href="#detail"', 'href="%scabinet.html"' % base)
    header = header.replace('href="#cabinet"', 'href="%scheck.html"' % base)
    header = header.replace('href="#place"', 'href="%sindex.html#place"' % base)
    header = header.replace('href="#top"', 'href="%sindex.html"' % base)
    header = header.replace('>Каталог<', '>Объекты<').replace('>Ранжирование<', '>Заявки покупателей<')
    header = header.replace('>Объявление<', '>Кабинет<').replace('>Кабинет продавца<', '>Проверка земли<')
    footer = T('footer')
    for a, b in [('href="#catalog"', 'href="%scatalog.html"' % base), ('href="#rank"', 'href="%srequests.html"' % base),
                 ('href="#detail"', 'href="%scheck.html"' % base), ('href="#cabinet"', 'href="%scabinet.html"' % base),
                 ('href="#place"', 'href="%sroadmap.html"' % base)]:
        footer = footer.replace(a, b)
    parts = ['<!doctype html>', '<html lang="ru">', '<head>', head + '</head>', '<body>', header,
             '<main id="top">', content, '</main>', footer,
             '<script src="' + base + 'assets/app.js" defer></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


FILTERS = '''<div class="veil" id="veil"></div>
<div class="layout">
  <aside class="filters" id="filters" aria-label="Фильтры">
    <div class="f-top"><h3>Фильтры</h3>
      <button class="f-close" id="f-close" type="button" aria-label="Закрыть фильтры"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
    </div>
    <div class="fg"><label for="f-reg">Регион</label>
      <select class="field" id="f-reg"><option>Вся Россия</option>%(regions)s</select></div>
    <div class="fg"><label for="f-use">Назначение</label>
      <select class="field" id="f-use"><option>Любое</option><option>Рекреация</option><option>Туристическое обслуживание</option><option>ИЖС</option><option>Сельхоз, СХ-3</option></select></div>
    <div class="fg"><label>Цена, ₽</label><div class="two"><input class="field" inputmode="numeric" placeholder="от" aria-label="Цена от"><input class="field" inputmode="numeric" placeholder="до" aria-label="Цена до"></div></div>
    <div class="fg"><label>Площадь, соток</label><div class="two"><input class="field" inputmode="numeric" placeholder="от" aria-label="Площадь от"><input class="field" inputmode="numeric" placeholder="до" aria-label="Площадь до"></div></div>
    <div class="fg">
      <label class="chk"><input type="checkbox"><span>Только проверенные</span></label>
      <label class="chk"><input type="checkbox"><span>С электричеством</span></label>
      <label class="chk"><input type="checkbox"><span>Круглогодичный подъезд</span></label>
      <label class="chk"><input type="checkbox"><span>Грантовый потенциал</span></label>
    </div>
    <div class="f-act">
      <button class="btn btn-p btn-w" type="button">Показать объекты</button>
      <button class="link-btn" id="reset" type="button">Сбросить фильтры</button>
    </div>
  </aside>'''


def catalog_page():
    regions = ''.join('<option>%s</option>' % r for r in sorted({o['region'] for o in DATA}))
    tabs = [('all', 'Все объекты'), ('uchastok', 'Участки'), ('business', 'Готовый бизнес'),
            ('auction', 'Аукционы'), ('stroy', 'Строящиеся')]
    tabs_html = ''.join('<button class="tab" role="tab" data-type="%s" aria-selected="%s">%s</button>'
                        % (t, 'true' if i == 0 else 'false', n) for i, (t, n) in enumerate(tabs))
    chips = ['У воды', 'Электричество', 'Лес', 'Подъезд круглый год', 'Готовый бизнес', 'Аукцион']
    chips_html = ''.join('<button class="chip" type="button" data-tag="%s" aria-pressed="false">%s</button>' % (c, c) for c in chips)
    cards = '\n'.join(card(o, '') for o in sorted(DATA, key=rank, reverse=True))
    content = '''<section class="zone" aria-labelledby="cat-h">
  <div class="wrap">
    <p class="kick">Каталог</p>
    <h1 class="h2" id="cat-h">Объекты на площадке</h1>
    <p class="sub">%d объявления в шести регионах. Счётчик просмотров и показов телефона работает на каждой карточке, порядок выдачи считается по трём правилам.</p>
    <div class="tabs" role="tablist" aria-label="Категории" style="margin-top:24px">%s</div>
    <div class="chips">%s</div>
    %s
      <div>
        <div class="rhead">
          <h2 style="font-size:20px">Найденные объекты<span class="cnt" id="found">найдено %d</span></h2>
          <div class="rtools">
            <button class="btn btn-s f-open" id="f-open" type="button"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M7 12h10M10 18h4"/></svg> Фильтры</button>
            <select class="sel" id="sort" aria-label="Сортировка">
              <option value="rec">Сначала рекомендуемые</option><option value="new">Сначала новые</option>
              <option value="cheap">Дешевле</option><option value="exp">Дороже</option><option value="views">Больше просмотров</option>
            </select>
            <button class="btn btn-s" id="save-search" type="button"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 9a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6M13.7 20a2 2 0 0 1-3.4 0"/></svg> Сохранить поиск</button>
          </div>
        </div>
        <div class="grid" id="grid">%s</div>
        <div class="saved" id="saved" role="status" hidden>
          <b>Поиск сохранён</b>
          <p>Новые объекты по условиям «у воды, Тверская область, до 6 млн» будут приходить в телеграм
            сразу после публикации. Отписаться можно одной командой в боте.</p>
        </div>
        <p id="empty" style="display:none;padding:32px 0;color:var(--soft)">По этим условиям ничего не нашлось. Сбросьте фильтры или выберите другую категорию.</p>
      </div>
  </div>
  </div>
</section>''' % (len(DATA), tabs_html, chips_html, FILTERS % {'regions': regions}, len(DATA), cards)
    return page('Каталог участков и готового бизнеса, Биржа-Земли',
                'Участки под базы отдыха и глэмпинги, готовый бизнес, аукционы и строящиеся объекты по всей России.',
                content)


def object_page(o):
    small, big = img_paths(o, '../')
    views_line = ('<div>%s<span><b data-count="%d">0</b> просмотров всего</span></div>'
                  '<div>%s<span>телефон открывали <b data-count="%d">0</b> раз</span></div>'
                  '<div>%s<span>опубликовано %d дн. назад</span></div>'
                  % (SVG['eye'], o['views'], SVG['tel'], o['phones'], SVG['clock'], o['days']))

    if o['deal'] == 'auction':
        a = o['auction']
        price_block = ('<p class="pp">текущая ставка</p><p class="pr">%s</p>'
                       '<dl class="specs" style="grid-template-columns:1fr;margin-top:14px">'
                       '<div><dt>Стартовая цена</dt><dd>%s</dd></div>'
                       '<div><dt>Шаг</dt><dd>%s</dd></div>'
                       '<div><dt>Ставок</dt><dd>%d</dd></div>'
                       '<div><dt>До конца торгов</dt><dd>%s</dd></div></dl>'
                       % (money(a['current']), money(a['start']), money(a['step']), a['bids'], a['ends']))
        actions = ('<button class="btn btn-p btn-w" data-phone="phone-out" type="button">Сделать ставку</button>'
                   '<p class="phone" id="phone-out" aria-live="polite"></p>'
                   '<button class="btn btn-s btn-w" type="button">Запросить документы</button>')
    else:
        per = o['price'] // o['area'] if (o['price'] and o['area']) else 0
        price_block = ('<p class="pr">%s</p><p class="pp">%s</p>'
                       % (money(o['price']) if o['price'] else 'Цена по запросу',
                          (format(per, ',d').replace(',', ' ') + ' ₽ за сотку') if per else 'уточняется у продавца'))
        actions = ('<button class="btn btn-p btn-w" data-phone="phone-out" type="button">Показать телефон</button>'
                   '<p class="phone" id="phone-out" aria-live="polite"></p>'
                   '<button class="btn btn-s btn-w" type="button">Запросить документы</button>')

    specs = [('Площадь', area_text(o['area'])), ('Категория', o['category']), ('Назначение', o['purpose']),
             ('Кадастр', o['cadastre']), ('Коммуникации', o['utilities']), ('Проверка документов', '%d из 5 пунктов' % o.get('check', 0))]
    if o.get('revenue'): specs.append(('Выручка', o['revenue']))
    if o.get('ready'): specs.append(('Стадия', o['ready']))
    specs_html = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (html.escape(k), html.escape(v)) for k, v in specs)

    views = [('50% 50%', 'Общий вид'), ('12% 50%', 'Левая часть'), ('88% 50%', 'Правая часть'), ('50% 12%', 'Дальний план')]
    strip = ''.join('<button type="button" data-pos="%s" aria-current="%s" aria-label="%s"><img src="%s" width="280" height="187" alt="%s" loading="lazy" style="object-position:%s"></button>'
                    % (pos, 'true' if i == 0 else 'false', name, small, html.escape(name + ', ' + o['title']), pos)
                    for i, (pos, name) in enumerate(views))

    similar = [x for x in DATA if x['id'] != o['id'] and x['type'] == o['type']][:3]
    similar_html = '\n'.join(card(x, '../') for x in similar)

    content = '''<section class="zone">
  <div class="wrap">
    <p class="kick"><a href="../catalog.html">Каталог</a> · %(typename)s</p>
    <h1 class="h2" style="max-width:20ch">%(title)s</h1>
    <p class="sub">%(region)s, %(district)s, %(place)s</p>

    <div class="detail" style="margin-top:32px">
      <div>
        <figure class="gal rv">
          <div class="main"><img src="%(big)s" width="1200" height="800" alt="%(alt)s" id="gal-main">
            <span class="badge">%(eye)s <b data-count="%(views)d">0</b> просмотров</span>
          </div>
          <div class="strip">%(strip)s</div>
        </figure>
        <div class="dbox rv">
          <h2 style="font-size:20px;font-weight:700">Характеристики</h2>
          <dl class="specs">%(specs)s</dl>
          <p style="margin-top:18px;color:var(--soft);font-size:15px">%(desc)s</p>
        </div>
        %(facts)s
        %(project)s
        %(article)s
        %(partners)s
      </div>
      <aside class="aside rv">
        %(price_block)s
        %(market)s
        %(history)s
        %(actions)s
        <div class="cnts">%(views_line)s</div>
        %(seller)s
        %(club)s
      </aside>
    </div>
  </div>
</section>

<section class="zone alt">
  <div class="wrap">
    <div class="head rv"><h2 class="h2" style="font-size:26px">Похожие объекты</h2></div>
    <div class="grid">%(similar)s</div>
    <div class="more-row"><a class="btn btn-s" href="../catalog.html">Смотреть весь каталог</a></div>
  </div>
</section>''' % {
        'typename': TYPE_NAME[o['type']] if o['deal'] != 'auction' else 'Аукцион',
        'title': html.escape(o['title']), 'region': html.escape(o['region']),
        'district': html.escape(o['district']), 'place': html.escape(o['place']),
        'big': big, 'alt': html.escape(o['title']), 'eye': SVG['eye'], 'views': o['views'],
        'strip': strip, 'specs': specs_html, 'desc': html.escape(o['desc']),
        'price_block': price_block, 'actions': actions, 'views_line': views_line, 'similar': similar_html,
        'market': market_line(o), 'history': history_line(o), 'seller': seller_block(o), 'club': club_line(o),
        'facts': facts_block(o), 'project': project_block(o), 'article': article_block(o),
        'partners': partners_block()}

    return page(o['title'] + ', Биржа-Земли', o['desc'][:150], content, base='../')


def check_page():
    content = '''<section class="zone">
  <div class="wrap form-zone">
    <div class="rv">
      <p class="kick">Проверка земли</p>
      <h1 class="h2">Узнайте риски до сделки</h1>
      <p class="sub">Проверяем участок по документам и открытым реестрам, отчёт сохраняется в кабинете. Пять пунктов: собственник, кадастр, категория и назначение, обременения, границы на местности.</p>
      <div class="rank" style="grid-template-columns:1fr 1fr 1fr;margin-top:28px">
        <div class="rule"><p class="n">1</p><h3>1 до 3 дней</h3><p>Срок подготовки отчёта после оплаты.</p></div>
        <div class="rule"><p class="n">2</p><h3>Веб-отчёт</h3><p>Остаётся в кабинете, можно скачать и отправить.</p></div>
        <div class="rule"><p class="n">3</p><h3>3 000 ₽</h3><p>Фиксированная стоимость одной проверки.</p></div>
      </div>
      <ol class="steps">
        <li><span class="n">1</span><div><h3>Собственник и история</h3><p>Кто владеет участком, как и когда получил право, есть ли судебные споры.</p></div></li>
        <li><span class="n">2</span><div><h3>Категория и назначение</h3><p>Можно ли строить то, ради чего покупаете, и что придётся менять.</p></div></li>
        <li><span class="n">3</span><div><h3>Обременения и границы</h3><p>Залоги, аренда, охранные зоны, совпадение границ с фактическими на местности.</p></div></li>
      </ol>
    </div>

    <form class="rv" data-validate novalidate>
      <div class="fg" data-rule="text">
        <label for="kad">Кадастровый номер</label>
        <input class="field" id="kad" name="kad" inputmode="numeric" placeholder="69:27:3150644:8909" autocomplete="off">
        <p class="hint">Если номера нет под рукой, напишите адрес участка.</p>
        <p class="err">Заполните это поле</p>
      </div>
      <div class="fg" data-rule="text">
        <label for="reg">Регион</label>
        <input class="field" id="reg" name="reg" placeholder="Тверская область" autocomplete="off">
        <p class="err">Укажите регион</p>
      </div>
      <div class="fg" data-rule="text">
        <label for="goal">Цель покупки</label>
        <input class="field" id="goal" name="goal" placeholder="Глэмпинг на 6 куполов" autocomplete="off">
        <p class="hint">От цели зависит, какие ограничения важны.</p>
        <p class="err">Опишите цель в двух словах</p>
      </div>
      <div class="fg" data-rule="phone">
        <label for="tel">Телефон</label>
        <input class="field" id="tel" name="tel" type="tel" inputmode="tel" placeholder="+7 900 000-00-00" autocomplete="tel">
        <p class="err">Нужен телефон, чтобы сообщить результат</p>
      </div>
      <button class="btn btn-p btn-w" type="submit">Заказать проверку за 3 000 ₽</button>
      <p class="note">Оплата после согласования, отчёт в течение трёх рабочих дней</p>
      <p class="done" role="status">%s<span>Заявка принята. Проверим документы и пришлём отчёт в кабинет.</span></p>
    </form>
  </div>
</section>''' % SVG['check']
    return page('Проверка земли перед сделкой, Биржа-Земли',
                'Проверка участка по документам и реестрам за 3 000 ₽, отчёт за один до трёх дней.', content)


def index_page():
    main = T('главная')
    show = sorted(DATA, key=rank, reverse=True)[:6]
    cards = '\n'.join(card(o, '') for o in show)
    main = re.sub(r'<div class="grid">.*?</div>\s*<div class="more-row">',
                  '<div class="grid" id="grid">%s</div>\n        <div class="more-row">' % cards,
                  main, count=1, flags=re.S)
    main = main.replace('<button class="btn btn-s" type="button">Показать ещё 54 объекта</button>',
                        '<a class="btn btn-s" href="catalog.html">Показать все %d объекта</a>' % len(DATA))
    main = main.replace('найдено 60', 'найдено %d' % len(DATA))
    main = main.replace('<button class="btn btn-p btn-w" type="button">Показать 60 объектов</button>',
                        '<a class="btn btn-p btn-w" href="catalog.html">Показать %d объекта</a>' % len(DATA))
    main = main.replace('<form class="rv" id="place-form" novalidate>', '<form class="rv" data-validate novalidate>')
    main = main.replace('<div class="fg" id="fg-kad">', '<div class="fg" data-rule="text">')
    main = main.replace('<div class="fg" id="fg-tel">', '<div class="fg" data-rule="phone">')
    main = main.replace('<button class="btn btn-p btn-w" id="show-phone" type="button">', '<button class="btn btn-p btn-w" data-phone="phone-out" type="button">')
    main = main.replace('<p class="phone" id="phone-out"', '<p class="phone" id="phone-out"')
    main = main.replace('<select class="sel" aria-label="Сортировка">', '<select class="sel" id="sort" aria-label="Сортировка">')
    main = main.replace('<button class="reset"', '<button class="link-btn" id="reset"')
    for old, new in [('<button class="tab" role="tab" aria-selected="true">Все объекты</button>', '<button class="tab" role="tab" data-type="all" aria-selected="true">Все объекты</button>'),
                     ('<button class="tab" role="tab" aria-selected="false">Участки</button>', '<button class="tab" role="tab" data-type="uchastok" aria-selected="false">Участки</button>'),
                     ('<button class="tab" role="tab" aria-selected="false">Готовый бизнес</button>', '<button class="tab" role="tab" data-type="business" aria-selected="false">Готовый бизнес</button>'),
                     ('<button class="tab" role="tab" aria-selected="false">Строящиеся</button>', '<button class="tab" role="tab" data-type="stroy" aria-selected="false">Строящиеся</button>'),
                     ('<button class="tab" role="tab" aria-selected="false">Заявки покупателей</button>', '<button class="tab" role="tab" data-type="auction" aria-selected="false">Аукционы</button>')]:
        main = main.replace(old, new)
    return page('Биржа-Земли: участки под базы отдыха и глэмпинги',
                'Площадка земли для туристического бизнеса. Участки у воды и леса с проверенными документами, счётчик просмотров и показов телефона на каждом объекте.',
                main)


if __name__ == '__main__':
    (BASE / 'object').mkdir(exist_ok=True)
    io.open(BASE / 'index.html', 'w', encoding='utf-8', newline='\n').write(index_page())
    io.open(BASE / 'catalog.html', 'w', encoding='utf-8', newline='\n').write(catalog_page())
    io.open(BASE / 'check.html', 'w', encoding='utf-8', newline='\n').write(check_page())
    io.open(BASE / 'requests.html', 'w', encoding='utf-8', newline='\n').write(
        page('Заявки покупателей, Биржа-Земли',
             'Покупатели публикуют запросы на землю под базы отдыха, продавцы предлагают участки.',
             requests_page()))
    io.open(BASE / 'cabinet.html', 'w', encoding='utf-8', newline='\n').write(
        page('Кабинет продавца, Биржа-Земли',
             'Просмотры, показы телефона, воронка и сроки размещения по каждому объявлению.',
             cabinet_page()))
    io.open(BASE / 'roadmap.html', 'w', encoding='utf-8', newline='\n').write(
        page('Что интегрируем в площадку, Биржа-Земли',
             'Карта нововведений: собрано в демо и следующие этапы.',
             roadmap_page()))
    for o in DATA:
        io.open(BASE / 'object' / (o['id'] + '.html'), 'w', encoding='utf-8', newline='\n').write(object_page(o))
    print('готово: index, catalog, check, requests, cabinet, roadmap и %d страниц объявлений' % len(DATA))
