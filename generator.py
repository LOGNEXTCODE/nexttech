"""
generator.py — NextTech
Usa Claude API para seleccionar noticias y redactar el contenido de cada sección.
Rellena web_template.html con los datos generados — no genera HTML desde cero.
"""

import os
import json
import re
import anthropic
import requests
from typing import List, Dict, Set, Optional

from pubdate import publication_date, mes_label

# ─── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
EDITION_NUMBER    = os.environ.get("EDITION_NUMBER", "01")

FORBIDDEN_WORDS = [
    "disruptivo", "disrupción", "ecosistema", "sinergia",
    "innovador", "innovación", "paradigma", "disruptive"
]

_MONTHS_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def _next_month_label(year: int, month: int, delta: int) -> str:
    idx = (month - 1 + delta) % 12
    y   = year + (month - 1 + delta) // 12
    return f"{_MONTHS_ES[idx]} {y}"


# ─── IMÁGENES UNSPLASH (IDs verificados HTTP 200, CDN directo sin API key) ──────
#
# Cada keyword tiene VARIAS fotos, no una sola: con un único ID por tema la misma
# imagen salía edición tras edición (la de "ai" se repitió en #02/#03/#05 y la de
# "privacy" en los Consejos de #03/#04/#05). `_pick_photo_id` rota por número de
# edición y descarta las ya usadas en ediciones anteriores y en la propia
# ejecución, así que dos secciones nunca comparten foto ni dentro de una edición
# ni entre ediciones mientras queden candidatas del tema.
_UNSPLASH_PHOTOS = {
    "cybersecurity": ["1550751827-4bd374c3f58b", "1614064548237-096f735f344f",
                      "1590065707046-4fde65275b2e", "1584433144859-1fc3ab64a957"],
    "data-breach":   ["1618060932014-4deda4932554", "1640158615573-cd28feb1bf4e",
                      "1529078155058-5d716f45d604", "1614064642578-7faacdc6336e"],
    "hacker":        ["1614064641938-3bbee52942c7", "1666615435088-4865bf5ed3fd",
                      "1562813733-b31f71025d54"],
    "network":       ["1558494949-ef010cbdcc31", "1544197150-b99a580bb7a8",
                      "1624965439943-09e0238644e2", "1484557052118-f32bd25b45b5"],
    "server":        ["1591808216268-ce0b82787efe", "1680992046626-418f7e910589",
                      "1629837093109-11325d6e7afd", "1506399558188-acca6f8cbf41"],
    "cloud":         ["1451187580459-43490279c0fa", "1667984390538-3dea7a3fe33d",
                      "1690627931320-16ac56eb2588", "1667984390535-6d03cff0b11a"],
    "code":          ["1517694712202-14dd9538aa97", "1608742213509-815b97c30b36",
                      "1461749280684-dccba630e2f6", "1542831371-29b0f74f9713"],
    "ai":            ["1676299081847-824916de030a", "1674027444485-cec3da58eef4",
                      "1620712943543-bcc4688e7485", "1677442135703-1787eea5ce01"],
    "robot":         ["1485827404703-89b55fcc595e", "1737644467636-6b0053476bb2",
                      "1527430253228-e93688616381"],
    "phishing":      ["1526374965328-7f61d4dc18c5", "1596526131083-e8c633c948d2",
                      "1557200134-90327ee9fafa", "1584438784894-089d6a62b8fa"],
    "privacy":       ["1610337673044-720471f83677", "1512149673953-1e251807ec7c",
                      "1654588831193-0285dab84d5a", "1580847097346-72d80f164702"],
    "energy":        ["1473341304170-971dccb5ac1e", "1508791290064-c27cc1ef7a9a",
                      "1466611653911-95081537e5b7", "1548337138-e87d889cc369"],
    "business":      ["1573497019236-17f8177b81e8", "1497215728101-856f4ea42174",
                      "1606857521015-7f9fcf423740", "1549637642-90187f64f420"],
    "mobile":        ["1512941937669-90a1b58e7e9c", "1592890288564-76628a30a657",
                      "1511707171634-5f897ff02aa9", "1598327105666-5b89351aff97"],
    "spain":         ["1539037116277-4db20889f2d4", "1543783207-ec64e4d95325",
                      "1570698473651-b2de99bae12f", "1574556462575-eb106a5865a0"],
    "technology":    ["1518770660439-4636190af475", "1644088379091-d574269d422f",
                      "1700427296131-0cc4c4610fc6", "1689443111130-6e9c7dfd8f9e"],
}


# Cache de comprobaciones HTTP por ejecución (una petición por foto como máximo)
_UNSPLASH_ALIVE: Dict[str, bool] = {}

# Fotos ya colocadas en ESTA ejecución (evita que dos secciones repitan imagen)
_USED_THIS_RUN: Set[str] = set()

# Fotos usadas en ediciones anteriores del repo (cache perezosa por ejecución)
_USED_PAST_EDITIONS: Optional[Set[str]] = None


def _photo_alive(photo_id: str) -> bool:
    """
    True si la foto sigue viva en el CDN de Unsplash (HTTP 200).
    Unsplash retira fotos sin avisar: en la #03 y la #04 el ID de "network"
    murió y la edición salió con la imagen de cabecera rota.
    Ante un error de red (sin conexión, timeout) se asume viva para no
    bloquear la generación.
    """
    if photo_id not in _UNSPLASH_ALIVE:
        try:
            r = requests.head(
                f"https://images.unsplash.com/photo-{photo_id}",
                params={"auto": "format", "fit": "crop", "w": 32, "h": 32, "q": 10},
                timeout=10,
            )
            _UNSPLASH_ALIVE[photo_id] = r.status_code == 200
        except requests.RequestException:
            _UNSPLASH_ALIVE[photo_id] = True
    return _UNSPLASH_ALIVE[photo_id]


def _past_edition_photo_ids(current_edition: str) -> Set[str]:
    """
    IDs de Unsplash ya usados en las ediciones del repo, excluyendo la que se está
    generando (si se regenera la misma edición, sus propias fotos no deben contar
    como "ya usadas"). Se cachea: basta con leer los HTML una vez por ejecución.
    """
    global _USED_PAST_EDITIONS
    if _USED_PAST_EDITIONS is None:
        used: Set[str] = set()
        root = os.path.dirname(os.path.abspath(__file__))
        try:
            carpetas = sorted(d for d in os.listdir(root) if re.fullmatch(r"\d{2}", d))
        except OSError:
            carpetas = []
        for carpeta in carpetas:
            if carpeta == current_edition:
                continue
            try:
                with open(os.path.join(root, carpeta, "index.html"), encoding="utf-8") as f:
                    used.update(re.findall(
                        r"images\.unsplash\.com/photo-([0-9a-f]+-[0-9a-f]+)", f.read()
                    ))
            except OSError:
                continue
        _USED_PAST_EDITIONS = used
    return _USED_PAST_EDITIONS


def _pick_photo_id(keyword: str, edition: str) -> str:
    """
    Elige una foto del tema `keyword` que no se haya usado antes.

    Prioridad: (1) del tema, nunca usada y viva; (2) del tema, no usada en esta
    edición y viva; (3) neutra de "technology" sin usar; (4) cualquiera del tema
    que siga viva. La fidelidad al tema manda sobre la variedad: antes repetir una
    foto acorde que colocar un molino de viento en una noticia de ransomware.
    """
    key = keyword.lower().split(",")[0].replace(" ", "-").strip()
    pool = _UNSPLASH_PHOTOS.get(key) or _UNSPLASH_PHOTOS["technology"]

    # Rotación por número de edición: cada mes arranca en un punto distinto del pool
    offset = (int(edition) - 1) if edition.isdigit() else 0
    rotado = [pool[(offset + i) % len(pool)] for i in range(len(pool))]

    usadas = _past_edition_photo_ids(edition)

    def _elegir(candidatas, evitar_pasadas: bool):
        for pid in candidatas:
            if pid in _USED_THIS_RUN:
                continue
            if evitar_pasadas and pid in usadas:
                continue
            if _photo_alive(pid):
                return pid
        return None

    photo_id = (
        _elegir(rotado, True)
        or _elegir(_UNSPLASH_PHOTOS["technology"], True)
        or _elegir(rotado, False)
        or next((pid for pid in rotado if _photo_alive(pid)), rotado[0])
    )

    if photo_id in usadas:
        print(f"  ⚠️ Sin fotos nuevas para '{key}': se repite {photo_id} de una edición anterior")
    _USED_THIS_RUN.add(photo_id)
    return photo_id


def _unsplash_url(keyword: str, w: int = 1200, h: int = 220, edition: str = "01") -> str:
    photo_id = _pick_photo_id(keyword, edition)
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&h={h}&q=80"


# ─── SELECCIÓN Y REDACCIÓN ─────────────────────────────────────────────────────

def select_and_draft(articles: List[Dict], warnings: List[str] = None) -> Dict:
    """
    Dos fases integradas en una llamada:
      Fase 1 — Razonamiento editorial: Claude justifica qué artículos elige y por qué.
      Fase 2 — Redacción: escribe el contenido con restricciones editoriales explícitas.
    Devuelve dict con todas las secciones + campo 'razonamiento'.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    articles_text = "\n\n".join([
        f"[{i+1}] FUENTE: {a['source']} | CATEGORÍA: {a['category']}\n"
        f"TÍTULO: {a['title']}\n"
        f"FECHA: {a['date']}\n"
        f"RESUMEN: {a['summary']}\n"
        f"URL: {a['url']}"
        for i, a in enumerate(articles[:40])
    ])

    # Mes de la edición = mes de PUBLICACIÓN (no de generación): la edición se
    # genera 14 días antes, en el mes anterior.
    mes_actual = mes_label(publication_date())

    aviso_scraping = ""
    if warnings:
        aviso_scraping = f"""
⚠️ AVISO EDITORIAL (no ignorar):
{chr(10).join(f'  - {w}' for w in warnings)}
Si la cobertura es insuficiente en alguna sección, indícalo con [COBERTURA LIMITADA ESTE MES]
en el campo 'texto' correspondiente. NUNCA inventes noticias ni URLs.
"""

    prompt = f"""Eres el editor jefe de NextTech, la publicación mensual de LOGNEXT sobre IA y ciberseguridad.

AUDIENCIA: El equipo IT de LOGNEXT en España (los "Nexters"). Nivel técnico medio-alto.
Contexto clave: LOGNEXT está en proceso de certificación ENS. Las noticias de ciberseguridad
en España tienen relevancia directa para ellos.
Tono: cercano, directo, con humor sutil. Nada corporativo ni frío. Como un compañero que sabe mucho.
{aviso_scraping}
══════════════════════════════════════════════════════
PASO 1 — SELECCIÓN RAZONADA (hazlo antes de escribir)
══════════════════════════════════════════════════════
Antes de redactar, decide qué artículos usar. Para cada sección indica en UNA línea
por qué es la mejor opción para los Nexters. Esto va en el campo "razonamiento" del JSON.

══════════════════════════════════════════════════════
PASO 2 — REDACCIÓN (con estas restricciones obligatorias)
══════════════════════════════════════════════════════
• consejo.texto: MÁXIMO 3 frases. Cuando hayas dado el consejo, para.
• esto_paso.texto: DEBE incluir al menos 1 dato numérico o porcentaje.
• Palabras PROHIBIDAS (reescribe si aparecen): {', '.join(FORBIDDEN_WORDS)}
• URLs: siempre de los artículos proporcionados. NUNCA inventadas.
• ESTO_PASO, CASO_REAL, CONSEJO, RETO e IA_DIA: campo "imagen" — elige UNA palabra exacta: cybersecurity, data-breach, hacker, network, server, cloud, code, ai, robot, phishing, privacy, energy, business, mobile, spain, technology
  Usa una palabra DISTINTA en cada sección: son cinco cabeceras visuales seguidas y repetir tema deja la edición con dos fotos parecidas.
• intro: 2-3 líneas. Cálida, directa. "Vuestra cita mensual", primer miércoles, recursos. Sin usar la palabra "newsletter". Mencionar edición #{EDITION_NUMBER}.
• radar: EXACTAMENTE 4 ítems, de fuentes distintas.
• enlaces: EXACTAMENTE 3 recursos (1 artículo, 1 vídeo, 1 quiz/herramienta).
• Para cada sección incluye el campo 'fuente' con el nombre del medio original
  y el mes/año. Ejemplo: 'Hispasec · Abril 2026', 'The Hacker News · Mayo 2026'.
  Para el reto, usa siempre: 'Departamento IT LOGNEXT · [mes] [año]'.

REGLA CRÍTICA — FUENTES SIN REPETIR: cada sección con enlace debe usar una
URL DISTINTA; nunca dos secciones (p. ej. caso_real y consejo) pueden
compartir el mismo artículo. Si el consejo deriva de la noticia del caso,
enlázalo a una guía oficial del tema (INCIBE/CCN-CERT) de los artículos
proporcionados, o déjalo sin URL (un consejo propio de IT no necesita
fuente externa).

REGLA CRÍTICA: El CONSEJO y el RETO deben tratar temas completamente
diferentes y no solaparse en ningún caso.
- El CONSEJO es una recomendación de seguridad técnica con una herramienta
  o práctica concreta (gestor de contraseñas, 2FA, revisar permisos, etc.).
- El RETO es una acción medible que el usuario puede completar esta semana
  (instalar algo, auditar algo, cambiar un hábito concreto).
- Nunca repitas la misma herramienta, concepto o acción en ambas secciones.
- Si el consejo habla de contraseñas, el reto debe hablar de otra cosa.
- Si el reto pide instalar algo, el consejo debe recomendar una práctica, no una app.

REGLA DE SENTIMIENTO:
- Noticias sobre incidentes de seguridad genéricos: SÍ incluir, tienen
  valor educativo aunque el evento sea negativo.
- Noticias positivas (buenas prácticas, parches publicados, logros,
  nuevas herramientas, estadísticas de mejora): SÍ incluir siempre.
- Noticias de bulos, rumores sin confirmar, o sensacionalismo sin
  fuente verificable: NO incluir, descartar.
- Noticias que dañen la imagen de empresas concretas sin valor
  educativo claro: NO incluir, descartar.
El objetivo es informar y educar, no alarmar ni señalar.

══════════════════════════════════════════════════════
SECCIONES A GENERAR
══════════════════════════════════════════════════════
1. ESTO_PASO: La noticia más impactante del mes en ciberseguridad/tecnología.
   3-4 líneas. Dato numérico obligatorio. URL de la noticia.

2. CASO_REAL: Un incidente real de seguridad narrado como episodio de serie.
   Qué pasó, cómo, consecuencias. Máx 5 líneas. URL.

3. CONSEJO: UN consejo práctico que cualquier empleado puede aplicar hoy.
   Concreto, útil, con toque de humor. Máx 3 frases.

4. RETO: Una acción concreta que los Nexters pueden completar este mes.
   Específica, medible, motivadora. Máx 2 frases. No es una recomendación — es un reto activo.

5. RADAR: 4 titulares relevantes de fuentes distintas. Breve y directo.
   Incluir org (nombre corto de la fuente) y fecha.

6. IA_DIA: Tendencia o incidente relevante sobre IA en ciberseguridad.
   3-4 líneas. Cómo afecta a equipos IT. URL del artículo fuente.

7. ENLACES: 3 recursos:
   - tipo "articulo": lectura recomendada
   - tipo "video": vídeo educativo o demostrativo (YouTube u otro)
   - tipo "quiz": herramienta interactiva, test o quiz de seguridad
   Cada uno con descripcion (1 línea de por qué merece la pena) y fuente.

8. INTRO: 2-3 líneas de apertura. Cálida, directa, que enganche. Sin usar "newsletter".

Responde ÚNICAMENTE con JSON válido con esta estructura exacta:
{{
  "razonamiento": {{
    "esto_paso": "Elegí [título] porque [motivo concreto para Nexters]",
    "caso_real": "Elegí [título] porque...",
    "radar": "Elegí estos 4 porque..."
  }},
  "intro": "...",
  "esto_paso": {{"titulo": "...", "texto": "...", "url": "...", "imagen": "ONE keyword from: cybersecurity, data-breach, hacker, network, server, cloud, code, ai, robot, phishing, privacy, energy, business, mobile, spain, technology", "fuente": "Nombre medio · Mes Año"}},
  "caso_real": {{"titulo": "...", "texto": "...", "url": "...", "imagen": "ONE keyword from: cybersecurity, data-breach, hacker, network, server, cloud, code, ai, robot, phishing, privacy, energy, business, mobile, spain, technology", "fuente": "Nombre medio · Mes Año"}},
  "consejo":   {{"titulo": "...", "texto": "...", "url": "...", "url_label": "Texto del enlace", "imagen": "ONE keyword from the same list", "fuente": "Nombre medio · Mes Año"}},
  "reto":      {{"titulo": "...", "texto": "...", "imagen": "ONE keyword from the same list", "fuente": "Departamento IT LOGNEXT · [mes] [año]"}},
  "ia_dia":    {{"titulo": "...", "texto": "...", "url": "...", "imagen": "ONE keyword from the same list", "fuente": "Nombre medio · Mes Año"}},
  "radar": [
    {{"titulo": "...", "org": "...", "url": "...", "fecha": "..."}},
    {{"titulo": "...", "org": "...", "url": "...", "fecha": "..."}},
    {{"titulo": "...", "org": "...", "url": "...", "fecha": "..."}},
    {{"titulo": "...", "org": "...", "url": "...", "fecha": "..."}}
  ],
  "enlaces": [
    {{"tipo": "articulo", "titulo": "...", "descripcion": "...", "url": "...", "fuente": "..."}},
    {{"tipo": "video",    "titulo": "...", "descripcion": "...", "url": "...", "fuente": "..."}},
    {{"tipo": "quiz",     "titulo": "...", "descripcion": "...", "url": "...", "fuente": "..."}}
  ]
}}

═══════════════════════════════════════════════
ARTÍCULOS DISPONIBLES — {mes_actual}
═══════════════════════════════════════════════
{articles_text}
"""

    print("  🤖 Llamando a Claude API (selección razonada + redacción)...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    content = json.loads(raw)

    if "razonamiento" in content:
        print("\n  📝 Razonamiento editorial:")
        for k, v in content["razonamiento"].items():
            print(f"     {k}: {v}")

    print("  ✅ Contenido generado correctamente")
    return content


def verify_content(content: Dict, edition: str) -> List[str]:
    """
    Verifica criterios editoriales antes del envío.
    Devuelve lista de issues; lista vacía = todo OK.
    """
    issues = []
    mes = mes_label(publication_date())

    subject = f"NextTech #{edition} — {mes}"
    if len(subject) > 45:
        issues.append(f"Subject demasiado largo: {len(subject)} chars (máx 45)")

    texto_esto = content.get("esto_paso", {}).get("texto", "")
    if not any(c.isdigit() for c in texto_esto):
        issues.append("esto_paso sin dato numérico — añadir cifra de impacto")

    for seccion in ["esto_paso", "caso_real", "ia_dia"]:
        url = content.get(seccion, {}).get("url", "")
        if not url.startswith("http"):
            issues.append(f"{seccion} sin URL válida (tiene: '{url}')")

    radar = content.get("radar", [])
    if len(radar) != 4:
        issues.append(f"Radar con {len(radar)} ítems — necesita exactamente 4")

    all_text = json.dumps(content, ensure_ascii=False).lower()
    found = [w for w in FORBIDDEN_WORDS if w in all_text]
    if found:
        issues.append(f"Palabras prohibidas encontradas: {', '.join(found)}")

    consejo_text = content.get("consejo", {}).get("texto", "")
    frases = [f for f in re.split(r'[.!?]', consejo_text) if f.strip()]
    if len(frases) > 3:
        issues.append(f"consejo.texto con {len(frases)} frases — máx 3")

    reto_text = content.get("reto", {}).get("texto", "")
    reto_frases = [f for f in re.split(r'[.!?]', reto_text) if f.strip()]
    if len(reto_frases) > 2:
        issues.append(f"reto.texto con {len(reto_frases)} frases — máx 2")

    enlaces = content.get("enlaces", [])
    if len(enlaces) != 3:
        issues.append(f"enlaces con {len(enlaces)} ítems — necesita exactamente 3")

    return issues


# ─── COMILLAS TIPOGRÁFICAS ─────────────────────────────────────────────────────
# Claude genera el contenido con comillas rectas (' y ") y las #02/#03/#04
# salieron con ellas hasta que alguien las parcheaba a mano. Aquí se normalizan
# ANTES de escribir el HTML: dobles "x" → “x” y simples 'x' → ‘x’ (curvas de
# apertura y cierre; decisión de Miguel del 1-sep-2026 tras probar y descartar
# las « » angulares en los entrecomillados de contenido).
# Los apóstrofos entre letras (l'IA, don't) no se tocan, ni las URLs.

_RE_DOBLES  = re.compile(r'"([^"\n]{1,200}?)"')
_RE_SIMPLES = re.compile(r"(?<![\w])'([^'\n]{1,200}?)'(?![\w])")


def _smart_quotes(text: str) -> str:
    text = _RE_DOBLES.sub('“\\1”', text)
    text = _RE_SIMPLES.sub('‘\\1’', text)
    return text


def _normalize_quotes(obj, key=None):
    """Aplica _smart_quotes a todos los strings del contenido, salvo URLs e IDs de imagen."""
    if isinstance(obj, str):
        return obj if key in ("url", "imagen") else _smart_quotes(obj)
    if isinstance(obj, dict):
        return {k: _normalize_quotes(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize_quotes(v, key) for v in obj]
    return obj


def _fuente_block(fuente: str) -> str:
    if not fuente:
        return ""
    return (
        "<div style=\"font-size:10px;font-family:'JetBrains Mono',monospace;"
        "opacity:0.4;letter-spacing:1px;margin-bottom:16px;"
        "display:flex;align-items:center;gap:6px;\">"
        "<span style=\"width:4px;height:4px;border-radius:50%;"
        "background:currentColor;display:inline-block;opacity:0.6;\"></span>"
        + fuente
        + "</div>"
    )


def _consejo_link_block(url: str, url_label: str) -> str:
    if not url or not url.startswith("http"):
        return ""
    label = url_label or "Saber más"
    return (
        f'<a href="{url}" target="_blank" class="card-link" '
        "style=\"color:var(--green)\" onclick=\"trackLink('consejo', this.href)\">"
        f"{label} <span class=\"arrow\">→</span></a>"
    )


def render_template(content: Dict, edition: str) -> str:
    """Lee web_template.html y sustituye todos los {{PLACEHOLDERS}} con el contenido generado."""
    content   = _normalize_quotes(content)  # comillas rectas → tipográficas antes de renderizar
    pub       = publication_date()
    mes_upper = mes_label(pub).upper()
    year      = pub.year
    month     = pub.month

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Imágenes Unsplash — las cinco secciones con cabecera visual SIEMPRE llevan foto.
    # El orden importa: `_pick_photo_id` va reservando IDs, así que la primera
    # sección elige del pool completo de su tema y las siguientes evitan repetir.
    _USED_THIS_RUN.clear()
    ia_img_url      = _unsplash_url(content.get("ia_dia",    {}).get("imagen", "ai"),            1200, 180, edition)
    esto_img_url    = _unsplash_url(content.get("esto_paso", {}).get("imagen", "cybersecurity"), 1200, 220, edition)
    caso_img_url    = _unsplash_url(content.get("caso_real", {}).get("imagen", "hacker"),         800, 160, edition)
    consejo_img_url = _unsplash_url(content.get("consejo",   {}).get("imagen", "code"),           800, 160, edition)
    reto_img_url    = _unsplash_url(content.get("reto",      {}).get("imagen", "code"),           800, 160, edition)

    # Radar (4 items fijos)
    radar = content.get("radar", [])
    for i in range(1, 5):
        item = radar[i - 1] if i - 1 < len(radar) else {}
        html = html.replace(f"{{{{RADAR_{i}_ORG}}}}", item.get("org", ""))
        html = html.replace(f"{{{{RADAR_{i}_TITULO}}}}", item.get("titulo", ""))
        html = html.replace(f"{{{{RADAR_{i}_URL}}}}", item.get("url", "#"))
        html = html.replace(f"{{{{RADAR_{i}_META}}}}", item.get("fecha", ""))

    # Recursos (3 items fijos: artículo, vídeo, quiz)
    enlaces = content.get("enlaces", [])
    for i in range(1, 4):
        e = enlaces[i - 1] if i - 1 < len(enlaces) else {}
        html = html.replace(f"{{{{RECURSOS_{i}_TITULO}}}}", e.get("titulo", ""))
        html = html.replace(f"{{{{RECURSOS_{i}_URL}}}}", e.get("url", "#"))
        html = html.replace(f"{{{{RECURSOS_{i}_DESC}}}}", e.get("descripcion", ""))
        html = html.replace(f"{{{{RECURSOS_{i}_FUENTE}}}}", e.get("fuente", ""))

    # Footer: lista de ediciones (pasadas publicadas + actual + 2 próximas)
    edition_int = int(edition)
    now_badge = (
        '<span style="display:inline-flex;align-items:center;gap:5px;margin-left:6px;'
        'background:rgba(250,60,15,0.15);border:1px solid rgba(250,60,15,0.4);'
        'padding:1px 7px;font-size:9px;letter-spacing:1.5px;color:var(--red);vertical-align:middle;">'
        '<span style="width:5px;height:5px;border-radius:50%;background:var(--red);'
        'display:inline-block;animation:pulse 1.5s ease-in-out infinite;"></span>NOW</span>'
    )
    # La columna NextGuide del footer es estática en web_template.html.
    # Cuando se publique una nueva guía, añadir el <li> correspondiente
    # directamente en web_template.html (y en todas las ediciones publicadas).
    footer_editions = ""
    # Ediciones pasadas ya publicadas (carpetas XX/ existentes) → enlaces reales
    base_dir = os.path.dirname(os.path.abspath(__file__))
    published_past = sorted(
        int(d) for d in os.listdir(base_dir)
        if re.fullmatch(r"\d{2}", d)
        and os.path.isdir(os.path.join(base_dir, d))
        and int(d) < edition_int
    )
    for ed_num in published_past:
        ed_str = f"{ed_num:02d}"
        ed_mes = _next_month_label(year, month, ed_num - edition_int)
        footer_editions += f'<li><a href="/{ed_str}/">#{ed_str} — {ed_mes}</a></li>\n'
    # Edición actual (NOW) + 2 próximas
    for delta in range(3):
        ed_num = edition_int + delta
        ed_str = f"{ed_num:02d}"
        ed_mes = _next_month_label(year, month, delta)
        if delta == 0:
            footer_editions += f'<li><a href="/{ed_str}/">#{ed_str} — {ed_mes}{now_badge}</a></li>\n'
        else:
            # Clase con override body.light (definida en web_template.html y en
            # editions-nav.js) — nunca color fijo inline, que no cambia de tema.
            footer_editions += (
                f'<li><span class="ed-foot-soon">→ #{ed_str} — próximamente</span></li>\n'
            )

    # Fuente blocks — se inyectan ANTES de que los placeholders de URL sean sustituidos,
    # usando los propios placeholders como anclajes de posición en el HTML.
    for anchor, block in [
        ('<a href="{{IA_URL}}"',      _fuente_block(content.get("ia_dia",    {}).get("fuente", ""))),
        ('<a href="{{NOTICIA_URL}}"', _fuente_block(content.get("esto_paso", {}).get("fuente", ""))),
        ('<a href="{{AMENAZA_URL}}"', _fuente_block(content.get("caso_real", {}).get("fuente", ""))),
    ]:
        if block:
            html = html.replace(anchor, block + "\n      " + anchor)

    consejo_additions = []
    consejo_fuente_html = _fuente_block(content.get("consejo", {}).get("fuente", ""))
    consejo_link_html   = _consejo_link_block(
        content.get("consejo", {}).get("url", ""),
        content.get("consejo", {}).get("url_label", "")
    )
    if consejo_fuente_html:
        consejo_additions.append(consejo_fuente_html)
    if consejo_link_html:
        consejo_additions.append(consejo_link_html)
    if consejo_additions:
        html = html.replace(
            "{{CONSEJO_TEXTO}}</div>",
            "{{CONSEJO_TEXTO}}</div>\n      " + "\n      ".join(consejo_additions)
        )

    reto_fuente_html = _fuente_block(content.get("reto", {}).get("fuente", ""))
    if reto_fuente_html:
        html = html.replace(
            "<span>¿Lo has hecho ya? ✓</span>\n      </div>\n    </div>",
            "<span>¿Lo has hecho ya? ✓</span>\n      </div>\n      "
            + reto_fuente_html + "\n    </div>"
        )

    # Sustituciones simples
    replacements = {
        "{{EDICION_NUM}}":     edition,
        "{{EDICION_MES}}":     mes_upper,
        "{{EDICION_AÑO}}":     str(year),
        "{{INTRO_TEXTO}}":     content.get("intro", ""),
        "{{IA_IMG_URL}}":      ia_img_url,
        "{{IA_TITULO}}":       content.get("ia_dia",    {}).get("titulo", ""),
        "{{IA_TEXTO}}":        content.get("ia_dia",    {}).get("texto",  ""),
        "{{IA_URL}}":          content.get("ia_dia",    {}).get("url",    "#"),
        "{{NOTICIA_IMG_URL}}": esto_img_url,
        "{{NOTICIA_TITULO}}":  content.get("esto_paso", {}).get("titulo", ""),
        "{{NOTICIA_TEXTO}}":   content.get("esto_paso", {}).get("texto",  ""),
        "{{NOTICIA_URL}}":     content.get("esto_paso", {}).get("url",    "#"),
        "{{AMENAZA_IMG_URL}}": caso_img_url,
        "{{AMENAZA_TITULO}}":  content.get("caso_real", {}).get("titulo", ""),
        "{{AMENAZA_TEXTO}}":   content.get("caso_real", {}).get("texto",  ""),
        "{{AMENAZA_URL}}":     content.get("caso_real", {}).get("url",    "#"),
        "{{CONSEJO_IMG_URL}}": consejo_img_url,
        "{{CONSEJO_TITULO}}":  content.get("consejo",   {}).get("titulo", ""),
        "{{CONSEJO_TEXTO}}":   content.get("consejo",   {}).get("texto",  ""),
        "{{RETO_IMG_URL}}":    reto_img_url,
        "{{RETO_TITULO}}":     content.get("reto",      {}).get("titulo", ""),
        "{{RETO_TEXTO}}":      content.get("reto",      {}).get("texto",  ""),
        "{{FOOTER_EDICIONES}}": footer_editions,
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))

    return html


def generate(articles: List[Dict], warnings: List[str] = None) -> tuple:
    """Función principal: devuelve (web_html, content) para web y email."""
    content = select_and_draft(articles, warnings=warnings)

    issues = verify_content(content, EDITION_NUMBER)
    if issues:
        print(f"\n  ⚠️  {len(issues)} issue(s) editorial(es) detectado(s):")
        for issue in issues:
            print(f"     • {issue}")
        print("  ↩️  Regenerando con correcciones...\n")
        content = select_and_draft(articles, warnings=warnings)
        issues_retry = verify_content(content, EDITION_NUMBER)
        if issues_retry:
            print(f"  ⚠️  Tras reintento quedan {len(issues_retry)} issue(s) — continuando con advertencia")
            for issue in issues_retry:
                print(f"     • {issue}")
    else:
        print("  ✅ Verificación editorial: OK")

    html = render_template(content, EDITION_NUMBER)
    return html, content


if __name__ == "__main__":
    from scraper import fetch_articles, validate_freshness
    print("\n📰 Obteniendo artículos...\n")
    arts = fetch_articles()
    freshness = validate_freshness(arts)
    print("\n✍️  Generando NextTech...\n")
    web_html, content = generate(arts, warnings=freshness["warnings"])
    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(web_html)
    print("\n✅ Preview guardado en preview.html")
