// Progressive enhancements. Every page works without this file:
// navigation, the language list and the menu are plain links inside <details>.
(function () {
  var root = document.documentElement;
  var small = window.matchMedia('(max-width: 959px)');
  var systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} }
  };

  // ── Appearance: Automatic (follow the system), By day, By night ──
  var toggle = document.querySelector('.theme-toggle');
  var segButtons = document.querySelectorAll('[data-theme-set]');
  var themeMeta = document.querySelector('meta[name="theme-color"]');

  function chosen() { var t = root.getAttribute('data-theme'); return t === 'light' || t === 'dark' ? t : 'auto'; }
  function effective() { var c = chosen(); return c === 'auto' ? (systemDark.matches ? 'dark' : 'light') : c; }
  function reflect() {
    var eff = effective();
    if (toggle) {
      toggle.setAttribute('aria-label', eff === 'dark' ? toggle.dataset.toLight : toggle.dataset.toDark);
      toggle.setAttribute('aria-pressed', eff === 'dark' ? 'true' : 'false');
    }
    segButtons.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.themeSet === chosen() ? 'true' : 'false'); });
    if (themeMeta) themeMeta.setAttribute('content', eff === 'dark' ? '#161310' : '#F5F2EC');
  }
  function setTheme(t) {
    if (t === 'light' || t === 'dark') { root.setAttribute('data-theme', t); store.set('easel-theme', t); }
    else { root.removeAttribute('data-theme'); store.set('easel-theme', null); }
    reflect();
  }
  if (toggle) toggle.addEventListener('click', function () { setTheme(effective() === 'dark' ? 'light' : 'dark'); });
  segButtons.forEach(function (b) { b.addEventListener('click', function () { setTheme(b.dataset.themeSet); }); });
  if (systemDark.addEventListener) systemDark.addEventListener('change', reflect);
  reflect();

  // ── Popovers: one open at a time; close on outside tap or Escape ──
  var pops = document.querySelectorAll('details.pop');
  pops.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (d.open) pops.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
  document.addEventListener('click', function (ev) {
    pops.forEach(function (d) { if (d.open && !d.contains(ev.target)) d.open = false; });
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape') return;
    pops.forEach(function (d) { if (d.open) { d.open = false; d.querySelector('summary').focus(); } });
  });

  // ── Language: remember an explicit choice; offer the visitor's own language once ──
  var data = document.getElementById('i18n');
  var here = data ? data.dataset.lang : 'en';
  document.querySelectorAll('a[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () { store.set('easel-lang', a.dataset.lang); });
  });
  if (data && !store.get('easel-lang') && !store.get('easel-suggest-dismissed')) {
    var map = JSON.parse(data.textContent);
    var want = null;
    (navigator.languages || [navigator.language || '']).some(function (raw) {
      var t = String(raw).toLowerCase();
      var code = t.indexOf('zh') === 0 ? ((/hant|tw|hk|mo/).test(t) ? null : 'zh-Hans')
        : t.indexOf('pt') === 0 ? 'pt-BR'
        : t.split('-')[0];
      if (code && map[code]) { want = code; return true; }
      return false;
    });
    if (want && want !== here) {
      var s = map[want];
      var bar = document.createElement('div');
      bar.className = 'suggest';
      bar.setAttribute('lang', s.hl);
      bar.innerHTML = '<div class="wrap"><p></p><button type="button"></button></div>';
      var p = bar.querySelector('p');
      p.textContent = s.text + ' ';
      var link = document.createElement('a');
      link.href = data.dataset.root + s.path;
      link.textContent = s.link;
      link.addEventListener('click', function () { store.set('easel-lang', want); });
      p.appendChild(link);
      var x = bar.querySelector('button');
      x.textContent = '×';
      x.setAttribute('aria-label', s.dismiss);
      x.addEventListener('click', function () { store.set('easel-suggest-dismissed', '1'); bar.remove(); });
      var header = document.querySelector('.top');
      header.parentNode.insertBefore(bar, header);
    }
  }

  // ── Header hairline once the page scrolls ──
  var top = document.querySelector('.top');
  function onScrollHeader() { if (top) top.classList.toggle('scrolled', window.scrollY > 4); }

  // ── On phones, start contents lists collapsed so each page opens on its content ──
  if (small.matches) {
    document.querySelectorAll('.toc details[open]').forEach(function (d) { d.removeAttribute('open'); });
  }

  // ── Download bar: after the hero, and only while no App Store badge is on screen ──
  var getbar = document.querySelector('.getbar');
  var badges = Array.prototype.slice.call(document.querySelectorAll('main .badge'));
  function onScrollBar() {
    if (!getbar) return;
    var h = window.innerHeight;
    var badgeOnScreen = badges.some(function (b) { var r = b.getBoundingClientRect(); return r.bottom > 0 && r.top < h; });
    getbar.classList.toggle('show', window.scrollY > h * 0.6 && !badgeOnScreen);
  }
  function onScroll() { onScrollHeader(); onScrollBar(); }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();
})();
