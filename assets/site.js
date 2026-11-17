// Small progressive enhancements for phones. The site works fully without this.
(function () {
  var small = window.matchMedia('(max-width: 959px)');

  // On phones, start the guide / topic / contents list collapsed so the page begins with its content.
  if (small.matches) {
    document.querySelectorAll('.toc details[open]').forEach(function (d) { d.removeAttribute('open'); });
  }

  // The download bar slides up once you've scrolled past the hero, and steps aside
  // whenever an App Store badge is already on screen.
  var bar = document.querySelector('.getbar');
  if (!bar) return;
  var badges = Array.prototype.slice.call(document.querySelectorAll('main .badge'));
  function update() {
    var h = window.innerHeight;
    var badgeOnScreen = badges.some(function (b) { var r = b.getBoundingClientRect(); return r.bottom > 0 && r.top < h; });
    bar.classList.toggle('show', window.scrollY > h * 0.6 && !badgeOnScreen);
  }
  window.addEventListener('scroll', update, { passive: true });   // two rect reads: cheap enough to run on every scroll
  window.addEventListener('resize', update);
  update();
})();
