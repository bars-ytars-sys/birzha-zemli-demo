# -*- coding: utf-8 -*-
"""Новые страницы демо: заявки покупателей, кабинет продавца, карта нововведений."""
import html
from блоки import EXTRA, I, money


def requests_page():
    cards = []
    for r in EXTRA['requests']:
        hot = '<span class="badge gold">Срочно</span>' if r['hot'] else ''
        cards.append('''<article class="req rv">
  <div class="req-h">
    <div><p class="req-who">%(who)s · %(region)s</p><h3>%(what)s</h3></div>%(hot)s
  </div>
  <ul class="req-p">
    <li><span>Площадь</span><b>%(area)s</b></li>
    <li><span>Бюджет</span><b>%(budget)s</b></li>
    <li><span>Вода</span><b>%(water)s</b></li>
    <li><span>Сроки</span><b>%(term)s</b></li>
  </ul>
  <div class="req-f">
    <span class="req-a">%(answers)d предложения от продавцов · опубликовано %(days)d дн. назад</span>
    <button class="btn btn-p" type="button">Предложить участок</button>
  </div>
</article>''' % {'who': html.escape(r['who']), 'region': html.escape(r['region']),
                 'what': html.escape(r['what']), 'hot': hot, 'area': html.escape(r['area']),
                 'budget': html.escape(r['budget']), 'water': html.escape(r['water']),
                 'term': html.escape(r['term']), 'answers': r['answers'], 'days': r['days']})

    return '''<section class="zone">
  <div class="wrap">
    <p class="kick">Спрос</p>
    <h1 class="h2">Заявки покупателей</h1>
    <p class="sub">Покупатель публикует запрос за минуту и без документов, продавцы предлагают
      подходящие участки. Раздел наполняет площадку до того, как появятся объявления,
      и показывает продавцу живой спрос в его районе.</p>

    <div class="req-bar rv">
      <div><b>%(count)d</b><span>активных заявок</span></div>
      <div><b>%(answers)d</b><span>предложений от продавцов</span></div>
      <div><b>2 дня</b><span>средний срок до первого отклика</span></div>
      <a class="btn btn-p" href="#new-req">Оставить заявку</a>
    </div>

    <div class="reqs">%(cards)s</div>
  </div>
</section>

<section class="zone alt" id="new-req">
  <div class="wrap form-zone">
    <div class="rv">
      <p class="kick">Ищете участок</p>
      <h2 class="h2">Опишите, что нужно</h2>
      <p class="sub">Заявка публикуется сразу, документы и кадастровый номер не нужны.
        Продавцы и агентства увидят её в своём кабинете и предложат варианты.</p>
      <ol class="steps">
        <li><span class="n">1</span><div><h3>Публикуем за минуту</h3><p>Регион, формат проекта, бюджет.</p></div></li>
        <li><span class="n">2</span><div><h3>Собираем предложения</h3><p>Продавцы отвечают своими объектами, вы сравниваете в одном месте.</p></div></li>
        <li><span class="n">3</span><div><h3>Проверяем выбранный участок</h3><p>Перед сделкой запускается проверка по пяти пунктам.</p></div></li>
      </ol>
    </div>
    <form class="rv" data-validate novalidate>
      <div class="fg" data-rule="text">
        <label for="q-what">Что ищете</label>
        <input class="field" id="q-what" placeholder="Глэмпинг на 8 куполов у воды">
        <p class="err">Опишите в двух словах</p>
      </div>
      <div class="fg">
        <label for="q-reg">Регион</label>
        <select class="field" id="q-reg"><option>Тверская область</option><option>Новгородская область</option>
          <option>Республика Карелия</option><option>Ленинградская область</option><option>Любой</option></select>
      </div>
      <div class="fg">
        <label>Бюджет, ₽</label>
        <div class="two"><input class="field" inputmode="numeric" placeholder="от" aria-label="Бюджет от">
          <input class="field" inputmode="numeric" placeholder="до" aria-label="Бюджет до"></div>
      </div>
      <div class="fg" data-rule="phone">
        <label for="q-tel">Телефон</label>
        <input class="field" id="q-tel" type="tel" inputmode="tel" placeholder="+7 900 000-00-00">
        <p class="err">Нужен телефон для откликов</p>
      </div>
      <button class="btn btn-p btn-w" type="submit">Опубликовать заявку</button>
      <p class="note">Заявка видна продавцам, ваш телефон открывается только после вашего согласия</p>
      <p class="done" role="status">%(check)s<span>Заявка опубликована. Первые предложения обычно приходят в течение двух дней.</span></p>
    </form>
  </div>
</section>''' % {'count': len(EXTRA['requests']),
                 'answers': sum(r['answers'] for r in EXTRA['requests']),
                 'cards': '\n'.join(cards),
                 'check': I['send']}


FUNNEL = [('Показы в каталоге', 4180, 100), ('Открытия карточки', 347, 8), ('Показы телефона', 89, 26)]


def cabinet_page():
    rows = [
        ('Участок 0,8 га у озера под глэмпинг', 347, 89, '+112', 'Приоритет до 14 сентября', 7),
        ('Массив 2,4 га под базу отдыха', 128, 24, '+40', 'Обычное размещение', 0),
        ('Участок ИЖС 12 соток рядом с рекой', 87, 11, '+19', 'Обычное размещение', 0),
    ]
    tr = ''.join('<tr><td>%s<span class="td-sub">%s</span></td><td class="num"><b data-count="%d">0</b></td>'
                 '<td class="num"><b data-count="%d">0</b></td><td class="num up">%s</td></tr>'
                 % (html.escape(t), html.escape(plan), v, p, d) for t, v, p, d, plan, _ in rows)

    funnel = ''.join('<li><div class="fu-bar" style="--w:%d%%"><i></i></div>'
                     '<div class="fu-t"><b data-count="%d">0</b><span>%s</span></div>'
                     '<span class="fu-c">%s</span></li>'
                     % (max(13, int(v / FUNNEL[0][1] * 100)), v, name,
                        'из показов %d%%' % pct if i else 'все показы')
                     for i, (name, v, pct) in enumerate(FUNNEL))

    bars = [('Март', 210, 17), ('Апрель', 340, 27), ('Май', 520, 42), ('Июнь', 610, 49),
            ('Июль', 880, 71), ('Август', 1240, 100)]
    chart = ''.join('<div class="bar%s" style="--h:%d%%;--i:%d"><i><em>%d</em></i><span>%s</span></div>'
                    % (' cur' if i == len(bars) - 1 else '', h, i, v, m)
                    for i, (m, v, h) in enumerate(bars))

    return '''<section class="zone">
  <div class="wrap">
    <p class="kick">Кабинет продавца</p>
    <h1 class="h2">Что происходит с объявлениями</h1>
    <p class="sub">Просмотры и показы телефона по каждому объекту, воронка от показа в каталоге
      до звонка и напоминания о сроках размещения. Данные копятся со дня установки счётчика.</p>

    <div class="notice rv">
      <span class="i">%(bell)s</span>
      <div>
        <b>Приоритетное размещение заканчивается через 7 дней</b>
        <p>За месяц объявление «Участок 0,8 га у озера» получило 347 просмотров и 89 показов телефона.
          После окончания приоритета объявление опустится с 1 на 9 место в выдаче по запросу
          «участок у воды в Тверской области».</p>
        <div class="notice-act">
          <button class="btn btn-p" type="button">Продлить за 2 400 ₽</button>
          <button class="btn btn-s" type="button">Включить автопродление</button>
        </div>
      </div>
    </div>

    <div class="cab rv" style="margin-top:24px">
      <div class="tbl-scroll">
        <table>
          <caption class="sr">Статистика объявлений</caption>
          <thead><tr><th scope="col">Объявление</th><th scope="col" class="num">Просмотры</th>
            <th scope="col" class="num">Показы телефона</th><th scope="col" class="num">За 30 дней</th></tr></thead>
          <tbody>%(rows)s</tbody>
        </table>
      </div>
      <div class="report">
        <div>
          <p class="chart-cap">Просмотры по месяцам</p>
          <div class="chart">%(chart)s</div>
        </div>
        <div class="kpi">
          <p class="k" data-count="1240">0</p><p class="kl">просмотров за август</p>
          <p class="k2" data-count="312">0</p><p class="kl">показов телефона за август</p>
        </div>
      </div>
    </div>

    <div class="two-col rv">
      <div class="dbox">
        <h2 class="dbox-h">Воронка по объявлению</h2>
        <p class="dbox-sub">Видно, где теряется покупатель: слабое фото в каталоге или цена в карточке.</p>
        <ul class="funnel">%(funnel)s</ul>
      </div>
      <div class="dbox">
        <h2 class="dbox-h">Уведомления</h2>
        <p class="dbox-sub">Приходят в телеграм, а не на почту.</p>
        <ul class="notif">
          <li><span class="i">%(send)s</span><div><b>Телефон открыли 3 раза за сутки</b><p>Участок 0,8 га у озера · сегодня 14:20</p></div></li>
          <li><span class="i">%(send)s</span><div><b>Новая заявка покупателя в вашем районе</b><p>Глэмпинг на 8 куполов, до 6 млн · вчера</p></div></li>
          <li><span class="i">%(bell)s</span><div><b>Размещение заканчивается через 7 дней</b><p>Сводка результатов и продление в один клик · вчера</p></div></li>
          <li><span class="i">%(send)s</span><div><b>Объявление опустилось на 4 позиции</b><p>Конкурент включил приоритет · 3 дня назад</p></div></li>
        </ul>
      </div>
    </div>
  </div>
</section>''' % {'rows': tr, 'chart': chart, 'funnel': funnel, 'bell': I['bell'], 'send': I['send']}


def roadmap_page():
    groups = []
    for g in EXTRA['roadmap']:
        items = ''
        for name, what, link in g['items']:
            a = ('<a class="rm-go" href="%s">Посмотреть</a>' % link) if link else '<span class="rm-soon">в плане</span>'
            items += ('<li><div><b>%s</b><p>%s</p></div>%s</li>'
                      % (html.escape(name), html.escape(what), a))
        groups.append('<div class="rm rv"><h2 class="rm-h">%s<span class="%s">%s</span></h2><ul>%s</ul></div>'
                      % (html.escape(g['group']), 'rm-tag done' if g['done'] else 'rm-tag',
                         'собрано в демо' if g['done'] else 'следующие этапы', items))

    return '''<section class="zone">
  <div class="wrap">
    <p class="kick">Карта работ</p>
    <h1 class="h2">Что интегрируем в площадку</h1>
    <p class="sub">Список того, что уже собрано в этом демо и что идёт дальше. Каждый пункт
      можно посмотреть в работе, ссылка ведёт на живой экран, а не на картинку.</p>
    <div class="rms">%s</div>
  </div>
</section>''' % '\n'.join(groups)
