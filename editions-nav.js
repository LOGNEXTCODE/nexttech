/*
 * editions-nav.js — Navegador de ediciones de NextTech
 * Lee /editions.json (manifiesto de ediciones publicadas) y pinta una barra
 * "‹ anterior · Ediciones ▾ · siguiente ›" justo debajo de la topbar.
 * La edición actual se detecta del <meta name="edicion" content="NN">.
 * Se auto-actualiza: al publicar una edición nueva basta con regenerar el
 * manifiesto; ninguna edición ya publicada necesita reescribir su HTML.
 */
(function () {
  var meta = document.querySelector('meta[name="edicion"]');
  if (!meta) return;
  var current = (meta.getAttribute('content') || '').trim();
  if (!current) return;

  fetch('/editions.json', { cache: 'no-cache' })
    .then(function (r) { return r.json(); })
    .then(function (eds) {
      if (!Array.isArray(eds) || !eds.length) return;
      eds.sort(function (a, b) { return String(a.n).localeCompare(String(b.n)); });

      var idx = -1;
      for (var i = 0; i < eds.length; i++) {
        if (String(eds[i].n) === current) { idx = i; break; }
      }
      if (idx < 0) return;
      var prev = eds[idx - 1] || null;
      var next = eds[idx + 1] || null;

      injectStyle();

      var nav = document.createElement('nav');
      nav.id = 'ed-nav';
      nav.setAttribute('aria-label', 'Navegación entre ediciones de NextTech');

      // ‹ anterior
      if (prev) {
        nav.appendChild(link(prev.url, '‹ #' + prev.n, ''));
      } else {
        nav.appendChild(span('‹', 'ed-dim'));
      }

      // Ediciones ▾ (desplegable con todas)
      var det = document.createElement('details');
      var sum = document.createElement('summary');
      sum.textContent = 'Ediciones ▾';
      det.appendChild(sum);
      var menu = document.createElement('div');
      menu.className = 'ed-menu';
      eds.forEach(function (e) {
        var a = link(e.url, '#' + e.n, String(e.n) === current ? 'ed-cur' : '');
        if (String(e.n) === current) { a.textContent = '#' + e.n + '  • actual'; }
        menu.appendChild(a);
      });
      det.appendChild(menu);
      nav.appendChild(det);

      // siguiente ›
      if (next) {
        nav.appendChild(link(next.url, '#' + next.n + ' ›', ''));
      } else {
        nav.appendChild(span('›', 'ed-dim'));
      }

      var topbar = document.querySelector('.topbar');
      if (topbar && topbar.parentNode) {
        topbar.parentNode.insertBefore(nav, topbar.nextSibling);
      } else {
        document.body.insertBefore(nav, document.body.firstChild);
      }
    })
    .catch(function () { /* sin manifiesto: no se pinta nada, sin romper la página */ });

  function link(href, text, cls) {
    var a = document.createElement('a');
    a.href = href; a.textContent = text; if (cls) a.className = cls;
    return a;
  }
  function span(text, cls) {
    var s = document.createElement('span');
    s.textContent = text; if (cls) s.className = cls;
    return s;
  }
  function injectStyle() {
    if (document.getElementById('ed-nav-style')) return;
    var st = document.createElement('style');
    st.id = 'ed-nav-style';
    st.textContent =
      "#ed-nav{display:flex;align-items:center;justify-content:center;gap:20px;padding:8px 16px;" +
      "font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:1px;" +
      "background:rgba(0,0,20,0.9);border-bottom:1px solid rgba(250,60,15,0.15);}" +
      "#ed-nav a{color:rgba(255,255,255,0.55);text-decoration:none;transition:color .2s ease;}" +
      "#ed-nav a:hover{color:var(--red,#FA3C0F);}" +
      "#ed-nav .ed-cur{color:var(--red,#FA3C0F);font-weight:700;}" +
      "#ed-nav .ed-dim{color:rgba(255,255,255,0.22);}" +
      "#ed-nav details{position:relative;}" +
      "#ed-nav summary{cursor:pointer;color:rgba(255,255,255,0.55);list-style:none;user-select:none;}" +
      "#ed-nav summary::-webkit-details-marker{display:none;}" +
      "#ed-nav details[open]>summary{color:var(--red,#FA3C0F);}" +
      "#ed-nav .ed-menu{position:absolute;left:50%;transform:translateX(-50%);top:24px;" +
      "background:rgba(0,0,20,0.98);border:1px solid rgba(255,255,255,0.1);padding:6px 0;" +
      "min-width:150px;box-shadow:0 8px 28px rgba(0,0,0,0.45);z-index:200;}" +
      "#ed-nav .ed-menu a{display:block;padding:7px 18px;white-space:nowrap;}" +
      "#ed-nav .ed-menu a:hover{background:rgba(255,255,255,0.06);}" +
      "body.light #ed-nav{background:rgba(255,255,255,0.94);border-bottom:1px solid rgba(0,0,41,0.1);}" +
      "body.light #ed-nav a,body.light #ed-nav summary{color:rgba(0,0,41,0.55);}" +
      "body.light #ed-nav .ed-cur,body.light #ed-nav details[open]>summary,body.light #ed-nav a:hover{color:#C82D00;}" +
      "body.light #ed-nav .ed-dim{color:rgba(0,0,41,0.25);}" +
      "body.light #ed-nav .ed-menu{background:#fff;border-color:rgba(0,0,41,0.12);box-shadow:0 8px 28px rgba(0,0,41,0.12);}" +
      "body.light #ed-nav .ed-menu a:hover{background:rgba(0,0,41,0.05);}";
    document.head.appendChild(st);
  }
})();
