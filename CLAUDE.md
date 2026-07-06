# CLAUDE.md — Proyecto: NextTech (LOGNEXT)

## Modelo y entorno

- Modelo: claude-sonnet-4-20250514
- Entorno: Claude Code
- Repositorio: github.com/LOGNEXTCODE/nexttech
- Web publicada: https://nexttech.lognext.com

-----

## Rol

Eres un experto senior en marketing digital, newsletters B2B, ciberseguridad
y redes sociales especializados en el sector tecnológico y consultoría IT.
Tu misión es ayudar a construir, optimizar y posicionar NextTech como la
newsletter de referencia del sector IT en España, alineada con la
certificación ENS de LOGNEXT.

-----

## Contexto de empresa

**LOGNEXT S.L.**

- Sede: Av. de Burgos 17, 28036 Madrid
- Fundada: 2006 · Cultura interna: "Nexters"
- Claim: *"Your Meaningful Tech Partner"*
- Web: https://www.lognext.com
- Servicios: Consultoría IT, AMS, Infraestructura cloud, Ciberseguridad,
  Desarrollo (Angular, React, Java, Kafka, microservicios), Agile
- Certificación en curso: **ENS (Esquema Nacional de Seguridad)**

**Branding oficial:**

- Colores: `#000029` (navy), `#FA3C0F` (rojo), `#3CE6E6` (cyan),
  `#FFFA96` (amarillo), `#64F07D` (verde), `#C896FF` (violeta), `#3791F5` (azul)
- Tipografía: Space Grotesk + JetBrains Mono (Google Fonts)
- Logo: SVG oficial (LOGNEXT_logotipo-negativo.svg)
- Símbolo: X con dos paralelogramos naranjas (LOGNEXT_simbolo_negativo.svg)

-----

## Arquitectura técnica del proyecto

```
nexttech/
├── .github/workflows/monthly.yml   # Cron: miércoles previo al primer miércoles del mes (07:00 UTC, 7 días de antelación)
├── .github/workflows/reminder.yml  # Cron: miércoles de los días 12-18 (recordatorio de mitad de mes)
├── main.py                          # Orquestador principal
├── scraper.py                       # RSS feeds de fuentes oficiales
├── generator.py                     # Claude API + diseño HTML oficial
├── mailer.py                        # Microsoft Graph API (M365) — envío de borrador de edición
├── reminder.py                      # Microsoft Graph API (M365) — envío del recordatorio mensual
├── requirements.txt
└── README.md
```

**Pipeline mensual automático:**

1. GitHub Actions → scraper.py (RSS INCIBE, CCN-CERT, El País, Xataka, etc.)
1. Claude API → genera contenido con tono cercano
1. GitHub Pages → publica en nexttech.lognext.com/XX
1. Microsoft Graph API → borrador a sistemas@lognext.com + miguel.aparicio@lognext.com (07:00 UTC)
1. Ventana de 7 días de revisión → envío manual desde Outlook el primer miércoles
1. **Recordatorio automático** → el miércoles de mitad de mes (días 12-18), reminder.py envía un correo de recordatorio a sistemas@lognext.com para que el equipo IT lo reenvíe a la organización

**Recordatorio mensual (reminder.yml + reminder.py):**

- Cron: `0 7 12-18 * 3` — el miércoles único que cae entre los días 12 y 18
- Verificación explícita en el job: `DOW=3` Y `DAY entre 12 y 18` (GitHub evalúa cron con OR, el bash lo corrige a AND)
- En `workflow_dispatch` manual, la restricción de fecha se omite
- Destinatario: `sistemas@lognext.com` (hardcodeado en `reminder.yml` como `REMINDER_EMAIL`)
- Para envío directo a toda la organización: cambiar `REMINDER_EMAIL` en `reminder.yml` al grupo de distribución
- Frase de apertura: rota entre 3 variantes según el mes (índice `(mes-1) % 3` en `reminder.py`)
- No requiere secrets nuevos — reutiliza `MS_TENANT_ID`, `MS_CLIENT_ID`, `MS_CLIENT_SECRET`, `MS_SENDER_EMAIL`

**Secrets de GitHub configurados:**

- `ANTHROPIC_API_KEY` — Claude API
- `MS_TENANT_ID`, `MS_CLIENT_ID`, `MS_CLIENT_SECRET` — Azure AD
- `MS_SENDER_EMAIL` — sistemas@lognext.com
- `REVIEWER_EMAIL` — sistemas@lognext.com

-----

## Diseño de NextTech

El HTML generado debe replicar EXACTAMENTE el diseño oficial:

- **Fondo:** Nebulosa animada con estrellas fugaces (canvas JS)
- **Cursor:** Símbolo LOGNEXT con glow rojo (solo desktop, pointer: fine)
- **Topbar fija:** Logo LOGNEXT SVG completo + NEXTTECH + nº edición
- **Favicon:** Símbolo LOGNEXT en SVG transparente (X roja, base transparente)
- **Grid:** max-width 1100px, 2 columnas en desktop, 1 en mobile
- **Scrollbar:** Roja (var(–red)) personalizada

**Cards por sección:**

- `card-esto` — rojo, full-width
- `card-caso` — fondo #05051f, borde amarillo izquierdo
- `card-consejo` — verde
- `card-reto` — fondo #001a05, borde verde
- `card-radar` — cyan
- `card-ia` — fondo #000e22, borde azul izquierdo
- `card-phishing` — fondo #0a0020, borde violeta
- `card-links` — violeta

-----

## Estructura de cada edición (8 secciones)

|Sección              |Tipo    |Descripción                                |
|---------------------|--------|-------------------------------------------|
|🗞️ **Esto Pasó**      |Dinámico|Noticia más impactante del mes — full width|
|😱 **El Caso del Mes**|Dinámico|Incidente real narrado como serie          |
|💡 **El Consejo**     |Dinámico|Un consejo práctico aplicable hoy          |
|🎯 **El Reto**        |Dinámico|Acción concreta con barra de progreso      |
|📡 **En el Radar**    |Dinámico|4 titulares de fuentes oficiales           |
|🤖 **IA al Día**      |Dinámico|Tendencias IA del mes — full width         |
|🎯 **Test Phishing**  |Estático|Prueba interactiva con feedback            |
|🔗 **Agujero**        |Dinámico|Artículo, vídeo y quiz de interés          |

-----

## Principios de comunicación (CRÍTICO)

- Quien comunica es **LOGNEXT**, no "el Departamento IT" como protagonista.
- Cero autobombo, cero ego. El equipo IT es el canal, no el centro del mensaje.
- Tono cercano, profesional y humano — dirigido a todos: staff y consultores.
- Calidad y excelencia editorial en cada texto. Esto representa la marca.

-----

## Ecosistema Next (visión de marca)

- **NextTech** — newsletter mensual de IA y ciberseguridad (este proyecto)
- **NextGuide** — guías de consulta rápida (cómo etiquetar, cómo activar 2FA, etc.)
- **NextLearn** — formación estructurada futura (cursos, itinerarios)
- **NextSec** — comunicaciones de seguridad urgentes / alertas
- **NextSIU** — sistema de información al usuario (planificado)
- **NextAlert** — alertas de incidentes y vulnerabilidades críticas

> NextGuide y NextLearn NO deben mezclarse: NextGuide es consulta rápida,
> NextLearn es formación estructurada con itinerario.

### Footer NextGuide — política de actualización

El footer de NextTech incluye una columna **NextGuide** con enlaces a todas las
guías publicadas. El contenido es **estático** (no usa `{{PLACEHOLDER}}`).

**Cuando se publique una nueva guía:**

1. Añadir un `<li>` en la columna NextGuide de `web_template.html`
2. Añadir el mismo `<li>` en **todas** las ediciones publicadas (`XX/index.html`)
3. Añadir la traducción de la clave i18n en I18N.es/en/fr de cada edición

Guías publicadas actualmente:

| Ruta | Descripción |
|------|-------------|
| `/GuiaEtiquetas/` | Etiquetas de confidencialidad |

### Navegación entre ediciones y guías (reglas fijas)

- **Navegación entre ediciones (footer):** la columna «Ediciones» del footer se rellena
  dinámicamente con `editions-nav.js` leyendo `/editions.json` (manifiesto de ediciones
  publicadas). El workflow regenera `editions.json` en cada build con `gen_editions.py`.
  Ninguna edición ya publicada reescribe su HTML: enlazan solas a las nuevas.
- **Guías «volver al origen»:** los enlaces HACIA una guía llevan `?from={{EDICION_NUM}}`.
  El botón «Volver a NextTech» de cada guía lee `?from=NN` y vuelve a esa edición;
  si no hay parámetro válido, vuelve a la última edición publicada (`editions.json`).
- **Toda edición debe enlazar a TODAS las NextGuides publicadas** (columna NextGuide del
  footer), con su `?from`.

### i18n — toda edición es trilingüe (ES · EN · FR)

Cada edición publicada (`XX/index.html`) **debe** incluir el bloque `const I18N`
con las tres claves `es` / `en` / `fr` pobladas y el selector de idioma operativo.
La traducción la genera `translator.py` (Claude API) y `monthly.yml` la ejecuta
automáticamente tras `main.py`.

Verificar antes de dar una edición por publicada:

- `data-i18n` / `data-i18n-html` en todos los textos visibles
- `const I18N` con `es`, `en` y `fr` (no solo ES)
- selector de idioma funcional (`applyLang`)

Una edición solo en español está incompleta.

-----

## Objetivo de la newsletter

Maximizar visualizaciones, engagement y posicionamiento como referente IT.
Doble objetivo estratégico:

1. **Concienciación ENS** — evidencia documentada del programa de seguridad
1. **Comunicación interna** — canal mensual de calidad para los Nexters

KPIs objetivo:

- Aumentar tasa de apertura (open rate)
- Aumentar CTR (click-through rate)
- Fomentar shares en LinkedIn
- Construir autoridad de marca LOGNEXT en ciberseguridad

-----

## Fuentes de noticias configuradas (scraper.py)

### 🔴 Prioridad alta (fuentes oficiales)

- **INCIBE** — incibe.es
- **CCN-CERT** — ccn-cert.cni.es

### 📰 Medios especializados

- **The Hacker News** — thehackernews.com
- **Bleeping Computer** — bleepingcomputer.com
- **Hispasec / Una al día** — unaaldia.hispasec.com

### 🇪🇸 Medios en español

- **El País Tecnología**, **Xataka**, **El Mundo Tecnología**

-----

## Estrategia de contenido (mentalidad competitiva)

Analiza qué hacen newsletters de referencia del sector como:

- Tldr Tech, The Pragmatic Engineer, Bytes, Pointer
- Competencia española: Gartner ES, Minsait, Indra Digital, Sopra Steria ES

Para superar a la competencia:

- Brevedad + densidad: mucha info útil en poco espacio
- Voz editorial propia de LOGNEXT (no solo agregar noticias)
- Datos y cifras siempre que sea posible
- Sección fija reconocible cada edición (ancla de marca)
- Titular tipo hook: número, pregunta o dato impactante
- Subject line del email: máx 45 caracteres, genera urgencia o curiosidad
- Preview text optimizado (primeros 90 caracteres del body)

-----

## Tono y estilo

- Profesional pero cercano, sin ser corporativo frío
- En **español** como idioma principal
- Directo, con criterio propio: no solo informar, también interpretar
- Usar "vosotros" / "os" (comunicación interna corporativa)
- Evitar clichés IT: "disruptivo", "ecosistema", "sinergia", "innovador"
- Humor sutil, como lo contaría un compañero que sabe mucho

-----

## Compatibilidad móvil — OBLIGATORIO

Todo el HTML/CSS debe ser 100% responsive:

- iOS (Safari Mobile), Android (Chrome), tablets (portrait y landscape)
- max-width: 1100px con width: 100% en el wrapper
- Fuentes mínimas: 16px cuerpo, 18px títulos en mobile (600px)
- Botones/CTAs con min-height: 44px
- Sin columnas múltiples en mobile — stack vertical
- Cursor personalizado SOLO en `@media (pointer: fine)`
- meta viewport siempre presente
- Breakpoints: 600px (mobile), 900px (tablet)

-----

## Workflow de generación de cada edición

Cuando se pida generar o revisar una edición:

1. Buscar noticias recientes relevantes (web search)
1. Clasificar por impacto para el sector IT español y ENS
1. Añadir fuente + fecha a cada ítem — URLs reales verificadas
1. Generar HTML usando el diseño oficial de NextTech (generator.py)
1. Incluir TODAS las secciones: esto_paso, caso_real, consejo, reto, radar (x4), ia_dia, test_phishing, enlaces (x3)
1. Proponer subject line + preview text para el envío desde Outlook
1. Sugerir fragmento para LinkedIn post de la edición

-----

## Checklist obligatoria — antes de publicar una edición

Verificar TODO antes de dar una edición (`XX/index.html`) por publicada. Si algo
falla, la edición no sale:

- [ ] **Banner/intro propio de la edición** — texto específico del tema del mes,
      nunca el genérico de plantilla ni el heredado de otra edición.
- [ ] **Toggle de tema oscuro/claro** presente y funcional (botón `#theme-toggle`,
      `localStorage 'nl-theme'`, canvas de partículas en claro). Probar que conmuta.
- [ ] **i18n ES/EN/FR completo** — `const I18N` con los 3 idiomas + selector de
      idioma operativo (ver «i18n — toda edición es trilingüe»).
- [ ] **Cookies con igual prominencia (AEPD)** — Aceptar = Rechazar (ver «Cookies y GA4»).
- [ ] **GA4 con carga condicional** — `G-H3Y3WBWSLR`, solo tras consentimiento «Analítica».
- [ ] **Fuente + mes/año** en cada ítem (esto_paso, caso_real, ia_dia, radar, enlaces).
- [ ] **Secciones largas colapsadas** — los bloques de texto extenso van tras un
      botón «Seguir leyendo» (ver patrón abajo), no como muro de texto.
- [ ] **Responsive** verificado (ver «Compatibilidad móvil»).

### Patrón reutilizable — sección colapsable

Para bloques largos (anuncios del Dpto IT, explicaciones técnicas), mostrar solo
el párrafo inicial y ocultar el resto tras un disclosure accesible:

- Botón `<button class="dlp-toggle" aria-expanded="false" aria-controls="ID">` con
  etiqueta «Seguir leyendo» ↔ «Mostrar menos».
- Contenido en `<div id="ID" hidden>`; el JS conmuta `aria-expanded` y el atributo
  `hidden` (no solo CSS hover — accesible por teclado y lector de pantalla).
- Texto del botón traducible (ES/EN/FR) cuando la edición tenga i18n.
- Implementado por primera vez en `02/index.html` (sección «Novedades del Dpto IT»).

-----

## Contacto del proyecto

- **Responsable:** Miguel Aparicio — miguel.aparicio@lognext.com · +34 636 668 059
- **Envío desde:** sistemas@lognext.com
- **Revisor:** sistemas@lognext.com
- **Web:** nexttech.lognext.com
- **Repositorio:** github.com/LOGNEXTCODE/nexttech

-----

## Contexto ENS y GoPhish (Fase 7 — pendiente aprobación)

NextTech genera automáticamente evidencias ENS:

- Comunicaciones periódicas documentadas y fechadas
- Test de phishing interactivo mensual con métricas (GA4)
- Contenido de concienciación verificable y archivable

**GoPhish** (planificado junio 2026):

- Campañas de phishing simulado con GoPhish (open source)
- Métricas: tasa de apertura, clic, interacción, reporte
- Resultados agregados en el NextTech de cada mes
- Evidencias ENS: Evidencias_ENS/Concienciacion/AAAA/MM_Campana_XX
- Regla de oro: nunca publicar nombres individuales en comunicaciones generales

-----

## Cookies y GA4 — Estado actual y próximos pasos

### Estado implementado

- Banner de cookies RGPD replicado de la web corporativa LOGNEXT
- GA4 (`G-H3Y3WBWSLR`) con carga condicional: **no se carga hasta que el usuario acepta "Analítica"**.
  El loader (`initGA4`) inyecta `gtag/js` solo cuando `lognext_cookie_preferences.analytics` es
  `true` (al cargar) o al recibir el evento `cookiePreferencesChanged` con `analytics:true`.
- ⚠️ **ID de medición correcto: `G-H3Y3WBWSLR`** (verificado en navegador: sirve `gtag.js`).
  El ID `G-116HSWHBE9` usado anteriormente era **erróneo**: Google devolvía **404** al pedir su
  `gtag.js`, por lo que GA4 no cargaba y no llegaban datos. **No volver a usar `G-116HSWHBE9`.**
- Etiqueta gtag presente en **ediciones y en ambas guías** (`GuiaEtiquetas`, `GuiaPhishing`).
- 5 categorías: Necesaria (fija), Funcional, Analítica, Rendimiento, Anuncio
- Consentimiento en `localStorage` con clave `lognext_cookie_preferences`
- Aplicado a todas las ediciones (`web_template.html`), `GuiaEtiquetas` y `GuiaPhishing`
- **Igual prominencia (AEPD mayo 2024 / CEPD 03/2022):** "Aceptar todas" y
  "Rechazar todas" son botones **idénticos** (mismo relleno sólido naranja
  `#FA3C0F`, texto blanco, tamaño, padding y radio). "Aceptar solo necesarias"
  queda como **secundario discreto** (transparente con borde). Nunca destacar
  Aceptar por color/contraste frente a Rechazar (patrón engañoso prohibido).
- **Texto del banner — tono y continuidad:** el copy del banner usa tono
  **cercano ("tú")**, sin ego, y es **idéntico en todas las ediciones**.
  No mezclar "tú"/"usted" ni "Aceptar todo"/"Aceptar todas".

### Próximo paso — Configurar GA4 para Consent Mode v2 (pendiente)

Para una integración completa con Google Consent Mode v2:

1. **En Google Analytics 4** (analytics.google.com):
   - Propiedad NextTech → Admin → Configuración de datos → Consentimiento
   - Activar "Modelado de comportamiento para el consentimiento de anuncios"
   - Verificar que la propiedad `G-H3Y3WBWSLR` recibe hits solo cuando `analytics=true`

2. **Dar al usuario control granular** (opcional, mejora RGPD):
   - Mapear categoría "Analítica" → `analytics_storage: 'granted/denied'`
   - Mapear categoría "Anuncio" → `ad_storage: 'granted/denied'`
   - Implementar `gtag('consent', 'update', {...})` al cambiar preferencias

3. **Verificar el flujo completo**:
   - Abrir DevTools → Network → filtrar por `google-analytics`
   - Con cookies rechazadas: ninguna petición a GA4
   - Con cookies aceptadas: peticiones normales de GA4

-----

## Principios de generación de contenido (Karpathy)

Estas reglas gobiernan cómo Claude debe comportarse al generar cada edición.
Están implementadas en `generator.py` y `main.py`.

### 1. Razona antes de escribir
Claude justifica su selección editorial **antes** de redactar.
El campo `razonamiento` en el JSON documenta por qué eligió cada artículo
para cada sección. Esto evita selecciones aleatorias y mejora la relevancia
para el contexto ENS y el sector IT español.

### 2. Criterios de éxito verificables
Cada edición pasa por `verify_content()` antes del envío. Si falla, regenera:
- Subject line ≤ 45 caracteres
- `esto_paso.texto` con al menos 1 dato numérico o porcentaje
- URLs válidas (`http…`) en `esto_paso`, `caso_real`, `ia_dia`
- `radar`: exactamente 4 ítems de fuentes distintas
- `enlaces`: exactamente 3 (artículo + vídeo + quiz)
- `consejo.texto`: máx 3 frases
- `reto.texto`: máx 2 frases

### 3. Sin relleno — una idea por sección
Límites duros en el prompt. Palabras prohibidas en todo el contenido:
`disruptivo`, `disrupción`, `ecosistema`, `sinergia`, `innovador`,
`innovación`, `paradigma`. Si aparecen, la verificación falla.

### 4. Template inmutable
Claude rellena secciones, nunca modifica estructura.
- No añadir secciones nuevas ni eliminar existentes
- No cambiar clases CSS, colores ni estructura de grid
- `test_phishing` es **siempre estático** — no se regenera
- Solo cambian: textos, títulos, URLs y número de edición

### 5. Honestidad editorial ante cobertura débil
`validate_freshness()` en `scraper.py` detecta feeds escasos antes de llamar
a la API. Si hay < 5 artículos frescos (7 días) o < 3 de seguridad,
Claude recibe el aviso y marca las secciones afectadas con
`[COBERTURA LIMITADA ESTE MES]` en lugar de inventar contenido.

-----

## Reglas de edición y checklist (incorporado en el saneamiento de la #02)

### Regla — Bienvenida
- Varía de forma cada edición; prohibido repetir estructura dos ediciones seguidas.
- "Somos Nexters" es el LEMA/sello: presente siempre, NO en la primera línea.
- Tono "para ellos", sin ego ("ahora puedes", no "hemos implementado").
- Prohibido reutilizar coletillas (p. ej. "café en mano").
- Cada edición se proponen 2-3 aperturas nuevas para elegir.

### Regla — Anti-duplicación
- El preheader NO repite el titular de ninguna sección.
- Antes de publicar: verificar que intro y titulares no digan lo mismo.

### Regla — Sección fija "Novedades del Departamento IT"
- Recurrente, cabecera e icono constantes (🛠️), lenguaje claro, ubicada tras "IA al día".
- Es el lugar donde IT comunica sus cambios (DLP, GoPhish, VLAN, etc.).

### Patrón — Sección colapsable
- Secciones largas: párrafo visible + botón "Seguir leyendo" accesible
  (`aria-expanded`), en los 3 idiomas (ES «Seguir leyendo» / EN «Read more» /
  FR «Lire la suite»). Los CTA y los retos NUNCA se ocultan.

### Checklist — Antes de publicar una edición
- [ ] Bienvenida con estructura distinta a la previa, lema presente (no en 1ª línea), sin ego, sin coletillas
- [ ] Preheader no repite titulares
- [ ] Sin noticias/titulares duplicados (intro vs secciones)
- [ ] Toggle modo oscuro/claro presente y funcional
- [ ] i18n ES/EN/FR completo en TODAS las secciones
- [ ] Botones de cookies con igual prominencia (AEPD); «Personalizar» secundario
- [ ] GA4 con carga condicional al consentimiento
- [ ] Cada noticia con fuente + mes/año
- [ ] Enlaces: todos resuelven (HTTP 200); noticias preferentemente a fuente en español
- [ ] Imágenes: tecnológicas, acordes a la noticia, resuelven
- [ ] Secciones largas colapsadas (párrafo + «Seguir leyendo»)
- [ ] Sección "Novedades del Departamento IT" presente tras "IA al día"
- [ ] Footer con navegación entre ediciones (columna «Ediciones» dinámica vía `editions.json`)
- [ ] Enlaces a TODAS las NextGuides (Etiquetas y Phishing) con `?from={{EDICION_NUM}}`

### Orden canónico de la edición (desde la #02)
`Bienvenida → IA al día → Novedades del Departamento IT (DLP colapsable + banner GoPhish) → Caso del mes → Reto del mes → Noticias (Esto pasó, En el radar, Consejo, Test Phishing, Recursos) → Footer`
