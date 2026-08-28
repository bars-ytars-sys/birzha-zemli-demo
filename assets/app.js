(function () {
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* тема */
  try { var st = localStorage.getItem('bz-theme'); if (st) root.setAttribute('data-theme', st); } catch (e) {}
  var tgl = $('#theme');
  if (tgl) tgl.addEventListener('click', function () {
    var cur = root.getAttribute('data-theme');
    if (!cur) cur = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('bz-theme', next); } catch (e) {}
  });

  /* шапка и мобильное меню */
  var hdr = $('#hdr'), hero = $('.hero'), burger = $('#burger'), mnu = $('#mnu');
  function onScroll() {
    if (!hdr) return;
    var open = mnu && mnu.classList.contains('open');
    hdr.classList.toggle('solid', !hero || window.scrollY > hero.offsetHeight - 80 || open);
  }
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });
  if (burger && mnu) {
    burger.addEventListener('click', function () {
      var open = mnu.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      onScroll();
    });
    mnu.addEventListener('click', function (e) {
      if (e.target.closest('a')) { mnu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); onScroll(); }
    });
  }

  /* поиск в герое */
  var srch = $('#srch');
  if (srch) srch.addEventListener('submit', function (e) { e.preventDefault(); });

  /* фильтры на телефоне */
  var filters = $('#filters'), veil = $('#veil'), fOpen = $('#f-open'), fClose = $('#f-close');
  function closeF() { if (filters) filters.classList.remove('open'); if (veil) veil.classList.remove('open'); }
  if (fOpen) fOpen.addEventListener('click', function () { filters.classList.add('open'); veil.classList.add('open'); });
  if (fClose) fClose.addEventListener('click', closeF);
  if (veil) veil.addEventListener('click', closeF);
  addEventListener('keydown', function (e) { if (e.key === 'Escape') closeF(); });

  /* избранное */
  $$('.fav').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
    });
  });

  /* ——— каталог: табы, чипы, сортировка ——— */
  var grid = $('#grid');
  function cards() { return $$('#grid > .card'); }
  var state = { type: 'all', chips: [], sort: 'rec' };

  function apply() {
    if (!grid) return;
    var list = cards(), shown = 0;
    list.forEach(function (c) {
      var okType = state.type === 'all' || c.dataset.type === state.type || c.dataset.deal === state.type;
      var okChips = state.chips.every(function (t) { return (c.dataset.tags || '').indexOf(t) >= 0; });
      var ok = okType && okChips;
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    });
    var byNum = function (a, b, k, dir) { return dir * ((+a.dataset[k] || 0) - (+b.dataset[k] || 0)); };
    var vis = list.filter(function (c) { return c.style.display !== 'none'; });
    var cmp = {
      rec: function (a, b) { return (+b.dataset.rank || 0) - (+a.dataset.rank || 0); },
      new: function (a, b) { return byNum(a, b, 'days', 1); },
      cheap: function (a, b) { return byNum(a, b, 'price', 1); },
      exp: function (a, b) { return byNum(a, b, 'price', -1); },
      views: function (a, b) { return byNum(a, b, 'views', -1); }
    }[state.sort];
    if (cmp) vis.sort(cmp).forEach(function (c) { grid.appendChild(c); });
    var cnt = $('#found');
    if (cnt) cnt.textContent = 'найдено ' + shown;
    var empty = $('#empty');
    if (empty) empty.style.display = shown ? 'none' : 'block';
  }

  $$('.tab').forEach(function (t) {
    t.addEventListener('click', function () {
      $$('.tab').forEach(function (x) { x.setAttribute('aria-selected', 'false'); });
      t.setAttribute('aria-selected', 'true');
      state.type = t.dataset.type || 'all';
      apply();
      if (history.replaceState) history.replaceState(null, '', state.type === 'all' ? location.pathname : '#' + state.type);
    });
  });
  $$('.chip').forEach(function (c) {
    c.addEventListener('click', function () {
      var on = c.getAttribute('aria-pressed') === 'true';
      c.setAttribute('aria-pressed', on ? 'false' : 'true');
      var tag = c.dataset.tag || c.textContent.trim();
      state.chips = on ? state.chips.filter(function (x) { return x !== tag; }) : state.chips.concat(tag);
      apply();
    });
  });
  var sortSel = $('#sort');
  if (sortSel) sortSel.addEventListener('change', function () { state.sort = sortSel.value; apply(); });
  var reset = $('#reset');
  if (reset) reset.addEventListener('click', function () {
    state.chips = []; state.type = 'all'; state.sort = 'rec';
    $$('.chip').forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    $$('.tab').forEach(function (x, i) { x.setAttribute('aria-selected', i === 0 ? 'true' : 'false'); });
    if (sortSel) sortSel.value = 'rec';
    apply();
  });
  if (grid && location.hash) {
    var h = location.hash.slice(1);
    var tab = $$('.tab').filter(function (t) { return t.dataset.type === h; })[0];
    if (tab) tab.click();
  }

  /* галерея объявления */
  var galMain = $('#gal-main');
  $$('.gal .strip button').forEach(function (b) {
    b.addEventListener('click', function () {
      $$('.gal .strip button').forEach(function (x) { x.setAttribute('aria-current', 'false'); });
      b.setAttribute('aria-current', 'true');
      if (!galMain) return;
      if (b.dataset.full) { galMain.src = b.dataset.full; var im = b.querySelector('img'); if (im) galMain.alt = im.alt; }
      if (b.dataset.pos) galMain.style.objectPosition = b.dataset.pos;
    });
  });

  /* показ телефона */
  $$('[data-phone]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var out = $('#' + btn.dataset.phone);
      if (out) { out.textContent = '+7 900 214-88-02'; out.classList.add('show'); }
      btn.textContent = 'Телефон открыт, засчитан показ';
      btn.disabled = true;
      btn.style.opacity = '.6';
    });
  });

  /* формы */
  $$('form[data-validate]').forEach(function (form) {
    var done = $('.done', form), btn = form.querySelector('[type="submit"]');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      $$('.fg[data-rule]', form).forEach(function (grp) {
        var fld = grp.querySelector('.field'), v = (fld.value || '').trim(), good;
        if (grp.dataset.rule === 'phone') good = (v.match(/\d/g) || []).length >= 10;
        else if (grp.dataset.rule === 'email') good = /.+@.+\..+/.test(v);
        else good = v.length > 4;
        grp.classList.toggle('bad', !good);
        if (!good && ok) { fld.focus(); ok = false; }
      });
      if (!ok) return;
      btn.disabled = true; btn.textContent = 'Отправляем...';
      setTimeout(function () {
        $$('.fg, .note', form).forEach(function (n) { n.style.display = 'none'; });
        btn.style.display = 'none';
        if (done) done.classList.add('show');
      }, 700);
    });
    $$('.fg[data-rule] .field', form).forEach(function (f) {
      f.addEventListener('input', function () { f.closest('.fg').classList.remove('bad'); });
    });
  });

  /* спарклайны */
  $$('.spark').forEach(function (s) {
    var v = (s.getAttribute('data-spark') || '').split(',').map(Number);
    if (v.length < 2) return;
    var w = 76, h = 22, pad = 3, max = Math.max.apply(null, v), min = Math.min.apply(null, v), span = (max - min) || 1;
    var pts = v.map(function (n, i) {
      var x = pad + i * (w - pad * 2) / (v.length - 1);
      var y = h - pad - (n - min) / span * (h - pad * 2);
      return x.toFixed(1) + ',' + y.toFixed(1);
    });
    var last = pts[pts.length - 1].split(',');
    s.innerHTML = '<polyline points="' + pts.join(' ') + '" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="2.4" fill="currentColor"/>';
  });

  /* появление и счётчики */
  var rio = new IntersectionObserver(function (es) {
    es.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      $$('.bar, .track', en.target).forEach(function (b) { b.classList.add('grow'); });
      rio.unobserve(en.target);
    });
  }, { threshold: .12 });
  $$('.rv').forEach(function (el) { rio.observe(el); });
  setTimeout(function () {   /* страховка: контент не должен остаться невидимым */
    $$('.rv').forEach(function (el) { el.classList.add('in'); });
    $$('.bar, .track').forEach(function (b) { b.classList.add('grow'); });
  }, 900);

  function run(el) {
    var t = parseInt(el.getAttribute('data-count'), 10) || 0;
    if (reduce) { el.textContent = t.toLocaleString('ru-RU'); return; }
    var d = 1100, s = performance.now();
    requestAnimationFrame(function step(now) {
      var p = Math.min(1, (now - s) / d), e = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(t * e).toLocaleString('ru-RU');
      if (p < 1) requestAnimationFrame(step);
    });
  }
  var cio = new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { run(en.target); cio.unobserve(en.target); } });
  }, { threshold: .5 });
  $$('[data-count]').forEach(function (el) { cio.observe(el); });
})();

/* калькулятор окупаемости в карточке объекта */
(function () {
  var box = document.getElementById('calc');
  if (!box) return;
  var unit = parseFloat(box.dataset.unit) || 3,
      land = parseFloat(box.dataset.land) || 0,
      elU = document.getElementById('units'),
      elC = document.getElementById('check'),
      elL = document.getElementById('load');

  function mln(v) {
    return (v >= 100 ? Math.round(v) : Math.round(v * 10) / 10).toLocaleString('ru-RU') + ' млн ₽';
  }
  function years(v) {
    var y = Math.floor(v), m = Math.round((v - y) * 12);
    if (m === 12) { y += 1; m = 0; }
    var sy = y + ' ' + (y % 10 === 1 && y % 100 !== 11 ? 'год' : (y % 10 >= 2 && y % 10 <= 4 && (y % 100 < 10 || y % 100 >= 20) ? 'года' : 'лет'));
    return m ? sy + ' ' + m + ' мес' : sy;
  }
  function calc() {
    var u = +elU.value, c = +elC.value, l = +elL.value;
    var build = u * unit, total = build + land;
    var year = u * c * 365 * l / 100 / 1e6;
    var profit = year * 0.42;
    document.getElementById('cu').textContent = u;
    document.getElementById('cc').textContent = c.toLocaleString('ru-RU') + ' ₽';
    document.getElementById('cl').textContent = l + '%';
    document.getElementById('o-total').textContent = mln(total);
    document.getElementById('o-year').textContent = mln(year);
    document.getElementById('o-profit').textContent = mln(profit);
    document.getElementById('o-pay').textContent = profit > 0 ? years(total / profit) : '—';
  }
  [elU, elC, elL].forEach(function (el) { el.addEventListener('input', calc); });
  calc();
})();

/* сохранение поиска */
(function(){
  var b=document.getElementById('save-search'),s=document.getElementById('saved');
  if(!b||!s)return;
  b.addEventListener('click',function(){
    s.hidden=false;b.disabled=true;b.style.opacity='.55';
    b.textContent='Поиск сохранён';
    s.scrollIntoView({block:'nearest',behavior:'smooth'});
  });
})();
