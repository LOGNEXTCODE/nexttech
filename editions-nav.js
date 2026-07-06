/*
 * editions-nav.js — Navegación entre ediciones en el FOOTER de NextTech.
 * Repuebla la columna «Ediciones» del footer desde /editions.json, con enlaces
 * a TODAS las ediciones publicadas y marcando la edición actual (leída del
 * <meta name="edicion">). Auto-actualizable: al publicar una edición nueva basta
 * con regenerar el manifiesto; ninguna edición ya publicada reescribe su HTML.
 * Si el manifiesto no carga o no encuentra la columna, se deja el footer estático.
 */
(function () {
  var meta = document.querySelector('meta[name="edicion"]');
  var current = meta ? (meta.getAttribute('content') || '').trim() : '';

  function findList() {
    // La clave i18n del título varía entre ediciones: guion (01) o guion bajo (02).
    var title = document.querySelector('[data-i18n="footer_col_editions"], [data-i18n="footer-col-editions"]');
    if (!title || !title.parentElement) return null;
    return title.parentElement.querySelector('.footer-links-list');
  }

  function pad2(n) { return ('0' + n).slice(-2); }

  fetch('/editions.json', { cache: 'no-cache' })
    .then(function (r) { return r.json(); })
    .then(function (eds) {
      if (!Array.isArray(eds) || !eds.length) return;
      var ul = findList();
      if (!ul) return;
      eds.sort(function (a, b) { return String(a.n).localeCompare(String(b.n)); });
      injectStyle();

      var html = '';
      eds.forEach(function (e) {
        var isCur = String(e.n) === current;
        var label = e.label ? ' — ' + e.label : '';
        html += '<li><a href="' + e.url + '"' + (isCur ? ' class="ed-foot-cur" aria-current="page"' : '') + '>#' + e.n + label + '</a>'
              + (isCur ? '<span class="ed-foot-here">estás aquí</span>' : '') + '</li>';
      });
      // Teaser de las 2 próximas ediciones aún no publicadas.
      var maxN = parseInt(eds[eds.length - 1].n, 10);
      for (var d = 1; d <= 2; d++) {
        html += '<li><span class="ed-foot-soon">→ #' + pad2(maxN + d) + ' — próximamente</span></li>';
      }
      ul.innerHTML = html;
    })
    .catch(function () { /* sin manifiesto: se deja el footer estático */ });

  function injectStyle() {
    if (document.getElementById('ed-foot-style')) return;
    var st = document.createElement('style');
    st.id = 'ed-foot-style';
    st.textContent =
      ".ed-foot-cur{color:var(--red)!important;font-weight:700;}" +
      ".ed-foot-here{margin-left:8px;font-size:9px;letter-spacing:1px;font-family:'JetBrains Mono',monospace;opacity:0.5;text-transform:uppercase;}" +
      ".ed-foot-soon{opacity:0.28;font-size:13px;font-family:'JetBrains Mono',monospace;letter-spacing:0.5px;color:var(--grey);}";
    document.head.appendChild(st);
  }
})();
