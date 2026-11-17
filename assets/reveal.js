// The hero's fog reveal: a 25-minute session, played in about fifteen seconds.
// The painting clears from the centre outward (a noise-edged mask that grows with
// progress), holds unveiled for a moment, then the fog rolls back in and it begins again.
(function () {
  var stage = document.getElementById('reveal');
  var timer = document.getElementById('timer');
  if (!stage || !timer) return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var REVEAL = 15000, HOLD = 4500, RETURN = 1600, CYCLE = REVEAL + HOLD + RETURN;
  var SESSION = 25 * 60;
  var start = null, raf = 0, visible = true;

  function ease(t) { return Math.pow(t, 1.6); }                    // a touch quicker than the app (revealEase 2.0), so the short demo opens sooner
  function fmt(s) { s = Math.max(0, Math.ceil(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }

  function paint(progress) {
    var r = stage.getBoundingClientRect();
    var diag = Math.hypot(r.width, r.height);
    stage.style.setProperty('--mask', (0.12 + ease(progress) * 4.4) * diag + 'px');
    stage.style.setProperty('--mist', (0.55 * (1 - progress)).toFixed(3));
    stage.classList.toggle('clear', progress >= 1);
  }

  function frame(now) {
    if (start === null) start = now;
    var t = (now - start) % CYCLE, p;
    if (t < REVEAL) p = t / REVEAL;
    else if (t < REVEAL + HOLD) p = 1;
    else p = 1 - (t - REVEAL - HOLD) / RETURN;          // fog drifts back in
    var counting = t < REVEAL;
    paint(Math.max(0, Math.min(1, p)));
    timer.textContent = counting ? fmt(SESSION * (1 - t / REVEAL)) : (t < REVEAL + HOLD ? '0:00' : '25:00');
    timer.classList.toggle('done', !counting && t < REVEAL + HOLD);
    raf = visible ? requestAnimationFrame(frame) : 0;
  }

  function still() { cancelAnimationFrame(raf); raf = 0; paint(1); timer.textContent = '0:00'; timer.classList.add('done'); }
  function run() { if (reduce.matches) return still(); if (!raf && visible) raf = requestAnimationFrame(frame); }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) run(); }).observe(stage);
  }
  document.addEventListener('visibilitychange', function () { visible = !document.hidden; if (visible) run(); });
  if (reduce.addEventListener) reduce.addEventListener('change', function () { start = null; reduce.matches ? still() : run(); });
  run();
})();
