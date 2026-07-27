# NextTech 🔐
**La carta de los que van un paso por delante**

Publicación mensual de ciberseguridad y tecnología para LOGNEXT. Publicada en [nexttech.lognext.com](https://nexttech.lognext.com) y distribuida por correo corporativo el **primer miércoles de cada mes**. La edición se genera automáticamente 14 días naturales antes (el miércoles de dos semanas antes) para dejar una ventana de revisión de 10 días laborables.

---

## ¿Cómo funciona?

El **miércoles exactamente 14 días antes del primer miércoles** de cada mes, GitHub Actions ejecuta automáticamente el pipeline de generación (ventana de revisión de 14 días naturales = 10 laborables). El envío a toda la organización es **manual el primer miércoles**:

1. **Scraper** — Lee RSS de INCIBE, CCN-CERT, El País Tech, Xataka, El Mundo, The Hacker News, Hispasec, Bleeping Computer
2. **Claude API** — Selecciona noticias, redacta el contenido con tono cercano y humor
3. **GitHub Pages** — Publica la edición en nexttech.lognext.com/XX automáticamente
4. **Mailer** — Envía el borrador a revisión vía Microsoft Graph API
5. **Revisión humana** — Se revisa, edita si procede, y se envía desde Outlook

---

## El NextTech incluye cada mes

| Sección | Descripción |
|---------|-------------|
| 👋 **Bienvenida** | Apertura propia de cada edición; cierra con el lema «Somos Nexters» |
| 🛠️ **Novedades del Departamento IT** | Cambios que aplica IT (DLP, GoPhish…) en lenguaje claro, con bloques colapsables «Seguir leyendo» — va tras «IA al Día» |
| 🗞️ **Esto Pasó** | La noticia más impactante del mes — ancho completo |
| 😱 **El Caso del Mes** | Un incidente real contado como serie |
| 💡 **El Consejo** | Un consejo práctico aplicable hoy |
| 🎯 **El Reto** | Una acción concreta para el mes |
| 📡 **En el Radar** | 4 titulares rápidos de fuentes oficiales |
| 🤖 **IA al Día** | Tendencias de IA del mes — ancho completo |
| 🎯 **Test de Phishing** | Prueba interactiva mensual con feedback |
| 🔗 **Agujero** | Artículo, vídeo y quiz de interés |

**Orden en la página (desde la #02):** Bienvenida → IA al Día → Novedades del Departamento IT (DLP colapsable + banner GoPhish) → Caso del Mes → Reto del Mes → Noticias (Esto Pasó, En el Radar, Consejo, Test Phishing, Agujero) → Footer.

---

## Diseño y tecnología

- **Tipografía:** Space Grotesk + JetBrains Mono
- **Colores:** Branding oficial LOGNEXT (`#000029`, `#FA3C0F` + paleta secundaria)
- **Layout:** Grid responsive — 1100px desktop / adaptado tablet y móvil
- **Favicon:** Símbolo LOGNEXT (X con paralelogramos naranjas) en SVG transparente
- **Logo LOGNEXT** en la topbar fija — logotipo negativo completo en SVG
- **Cursor personalizado** — símbolo LOGNEXT animado con glow rojo (solo desktop)
- **Fondo nebulosa** — nubes de color animadas con estrellas parpadeantes y fugaces
- **Modo claro/oscuro** — toggle con persistencia (`localStorage 'nl-theme'`); nebulosa en oscuro, partículas en claro
- **Trilingüe ES/EN/FR** — selector de idioma con `data-i18n` y diccionario `I18N`; todas las secciones (incluidos cookies, DLP y banner GoPhish) traducidas
- **Secciones colapsables** — bloques largos con botón accesible «Seguir leyendo» (`aria-expanded`), traducible
- **Efecto hover** en cards y botones con colores explícitos por sección
- **Google Analytics GA4** integrado — tracking por sección, clics y test phishing
- **Test phishing interactivo** con feedback educativo
- **Topbar fija** con logo LOGNEXT al hacer scroll

---

## Fuentes de noticias configuradas

### 🔴 Fuentes oficiales (máxima prioridad)
- **INCIBE** — incibe.es (Instituto Nacional de Ciberseguridad)
- **CCN-CERT** — ccn-cert.cni.es (Centro Criptológico Nacional)
- **ENISA** — enisa.europa.eu (Agencia Europea de Ciberseguridad)

### 📰 Medios especializados
- **The Hacker News** — thehackernews.com
- **Bleeping Computer** — bleepingcomputer.com
- **Hispasec / Una al día** — unaaldia.hispasec.com
- **Krebs on Security** — krebsonsecurity.com

### 🇪🇸 Medios en español
- **El País Tecnología**
- **Xataka**
- **El Mundo Tecnología**

Para añadir más fuentes, edita el array `SOURCES` en `scraper.py`.

---

## Google Analytics

El sistema trackea automáticamente:
- `section_read` — qué secciones lee cada usuario
- `outbound_click` — qué enlaces externos generan más interés
- `phishing_test` — resultados del test mensual (correct / incorrect)

El ID de medición ya está configurado (`G-H3Y3WBWSLR`) en ediciones y guías. GA4 carga
**solo tras aceptar «Analítica»** en el banner de cookies (RGPD); sin consentimiento no se envía nada.

---

## Configuración inicial

### 1. GitHub Secrets
Ve a tu repositorio → **Settings → Secrets and variables → Actions** y añade:

| Secret | Descripción |
|--------|-------------|
| `ANTHROPIC_API_KEY` | API Key de Anthropic (console.anthropic.com) |
| `MS_TENANT_ID` | Azure AD → Overview → Tenant ID |
| `MS_CLIENT_ID` | Azure AD → App registrations → tu app → Application ID |
| `MS_CLIENT_SECRET` | Azure AD → tu app → Certificates & secrets → New secret |
| `MS_SENDER_EMAIL` | Email desde el que se envía (sistemas@lognext.com) |
| `REVIEWER_EMAIL` | Email del revisor (sistemas@lognext.com) |

### 2. Registro de app en Azure AD

1. Ve a **portal.azure.com** → Registros de aplicaciones → Nuevo registro
2. Nombre: `NextTech`
3. En **Permisos de API** añade: `Mail.Send` (Permiso de aplicación)
4. Haz clic en **Conceder consentimiento de administrador**
5. Crea un **Secreto de cliente** y cópialo como secret de GitHub

### 3. GitHub Pages

1. Settings → Pages → Source: **GitHub Actions**
2. Custom domain: `nexttech.lognext.com`
3. Marcar ✅ Enforce HTTPS
4. En tu DNS (Acens): registro CNAME `nexttech` → `lognextcode.github.io`

---

## Ejecución manual

Desde GitHub → **Actions → NextTech — Generación mensual → Run workflow**

Puedes especificar el número de edición manualmente si es necesario.

---

## Estructura del proyecto

```
nexttech/
├── .github/
│   └── workflows/
│       ├── monthly.yml         # Cron: genera y publica la edición (miércoles 14 días antes del primer miércoles)
│       └── translate-pages.yml # Traducción manual EN/FR de páginas estáticas
├── main.py                  # Orquestador principal
├── scraper.py               # Lee RSS de fuentes de noticias
├── generator.py             # Genera el contenido con Claude API (rellena web_template.html)
├── mailer.py                # Envía borrador a revisión vía Microsoft Graph API
├── translator.py            # Traduce la edición a EN/FR (Claude API)
├── web_template.html        # Plantilla de la edición web
├── email_template.html      # Plantilla del email de revisión
├── requirements.txt
└── README.md
```

---

## Ecosistema Next

NextTech forma parte de la familia de comunicaciones Next de LOGNEXT:

| Producto | Descripción |
|----------|-------------|
| **NextTech** | Newsletter mensual de IA y ciberseguridad (este proyecto) |
| **NextGuide** | Guías de consulta rápida (cómo etiquetar, cómo activar 2FA…) |
| **NextLearn** | Formación estructurada futura (cursos, itinerarios) |
| **NextSec** | Comunicaciones de seguridad urgentes / alertas |
| **NextAlert** | Alertas de incidentes y vulnerabilidades críticas |

---

## Roadmap

| Fase | Descripción | Estado |
|------|-------------|--------|
| ✅ 1 | Configuración Azure AD y GitHub | Completado |
| ✅ 2 | API Keys y Secrets | Completado |
| ✅ 3 | Prueba y verificación pipeline | Completado |
| ✅ 3b | GitHub Pages + DNS personalizado | Completado |
| ✅ 4 | Diseño final — logo, favicon, nebulosa, cursor | Completado |
| ✅ 5 | Lanzamiento NextTech #01 — Mayo 2026 | Completado |
| ⏳ 6 | Campaña phishing simulado (GoPhish) — primer simulacro anunciado para **septiembre 2026** en la #02 | Planificado |

---

*by LOGNEXT · sistemas@lognext.com*
