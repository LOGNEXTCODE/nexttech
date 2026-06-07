"""
reminder.py — NextTech
Envía el recordatorio mensual de mitad de mes a sistemas@lognext.com
y actualiza el texto de bienvenida de la edición vigente (3 idiomas).
Reutiliza get_access_token() de mailer.py (Microsoft Graph API / M365).
"""

import os
import re
from datetime import datetime
import requests
from mailer import get_access_token


SENDER_EMAIL   = os.environ["MS_SENDER_EMAIL"]                            # sistemas@lognext.com
REMINDER_TO    = os.environ.get("REMINDER_EMAIL", "sistemas@lognext.com")
EDITION_NUMBER = os.environ.get("EDITION_NUMBER", "01")

SUBJECT = "☕ ¿Aún no has leído NextTech? Tómate un respiro y ponte al día"


# ── EMAIL ─────────────────────────────────────────────────────────────────────

def _edition_label_es(edition: str) -> str:
    return "primera" if edition == "01" else "última"

def get_opener(edition: str) -> str:
    """Frase de apertura del correo, rotada por mes. 'primera' para #01."""
    label = _edition_label_es(edition)
    openers = [
        f"A mitad de mes, un recordatorio rápido: la {label} edición de NextTech sigue esperándote.",
        f"Mitad de mes, buen momento para una pausa: la {label} edición de NextTech sigue esperándote.",
        f"¿Semana intensa? La {label} edición de NextTech sigue esperándote.",
    ]
    return openers[(datetime.now().month - 1) % len(openers)]


def build_html(opener: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#000029;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:#000029;">
    <tr><td align="center" style="padding:40px 20px;">
      <table width="600" cellpadding="0" cellspacing="0" border="0"
             style="max-width:600px;width:100%;background-color:#050520;
                    border-radius:12px;overflow:hidden;
                    border:1px solid rgba(250,60,15,0.2);">

        <!-- Cabecera -->
        <tr>
          <td style="background:linear-gradient(135deg,#000029 0%,#050535 100%);
                     padding:28px 40px;border-bottom:3px solid #FA3C0F;">
            <p style="margin:0;font-size:11px;font-weight:700;letter-spacing:3px;
                      text-transform:uppercase;color:#FA3C0F;
                      font-family:'Courier New',Courier,monospace;">
              LOGNEXT · NEXTTECH
            </p>
            <p style="margin:6px 0 0 0;font-size:22px;font-weight:700;
                      color:#ffffff;letter-spacing:-0.5px;">
              Recordatorio mensual
            </p>
          </td>
        </tr>

        <!-- Cuerpo -->
        <tr>
          <td style="padding:36px 40px;">
            <p style="margin:0 0 20px 0;font-size:15px;color:#E1E1E8;
                      line-height:1.7;font-family:Arial,sans-serif;">
              Buenos días Nexters,
            </p>
            <p style="margin:0 0 20px 0;font-size:15px;color:#E1E1E8;
                      line-height:1.7;font-family:Arial,sans-serif;">
              {opener}
            </p>
            <p style="margin:0 0 28px 0;font-size:15px;color:#E1E1E8;
                      line-height:1.7;font-family:Arial,sans-serif;">
              Si aún no le has echado un vistazo, este es tu momento.
              Hazte un café, tómate cinco minutos y ponte al día con lo
              último en inteligencia artificial y ciberseguridad.
            </p>

            <!-- CTA -->
            <table cellpadding="0" cellspacing="0" border="0"
                   style="margin:0 0 28px 0;">
              <tr>
                <td style="background-color:#FA3C0F;border-radius:8px;">
                  <a href="https://nexttech.lognext.com" target="_blank"
                     style="display:inline-block;padding:14px 32px;
                            font-size:15px;font-weight:700;color:#ffffff;
                            text-decoration:none;font-family:Arial,sans-serif;
                            letter-spacing:-0.2px;">
                    → Leer NextTech
                  </a>
                </td>
              </tr>
            </table>

            <p style="margin:0 0 4px 0;font-size:15px;color:#E1E1E8;
                      line-height:1.7;font-family:Arial,sans-serif;">
              Nos vemos en la próxima edición.
            </p>
            <p style="margin:0;font-size:15px;color:#E1E1E8;
                      line-height:1.7;font-family:Arial,sans-serif;">
              El equipo IT de LOGNEXT
            </p>
          </td>
        </tr>

        <!-- Pie -->
        <tr>
          <td style="background-color:#000015;padding:20px 40px;
                     border-top:1px solid rgba(250,60,15,0.1);">
            <p style="margin:0;font-size:11px;color:#E1E1E8;
                      font-family:'Courier New',Courier,monospace;
                      opacity:0.4;letter-spacing:1px;">
              LOGNEXT · sistemas@lognext.com · nexttech.lognext.com
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── WEB INTRO ─────────────────────────────────────────────────────────────────

def _intro_texts(edition: str) -> dict:
    """
    Textos del bloque de bienvenida de la web para los 3 idiomas.
    Diferente al correo: más visual, directo al grano, sin repetir el email.
    Usa 'primera' para #01, 'última' / 'latest' / 'dernière' para el resto.
    """
    if edition == "01":
        return {
            "es": "Mitad de mes: si aún no has pasado por aquí, este es el momento. La primera edición de NextTech te espera — cinco minutos, un café y te pones al día con lo último en IA y ciberseguridad.",
            "en": "Mid-month: if you haven't stopped by yet, now's the time. The first NextTech edition is waiting — five minutes, a coffee and you're up to speed on AI and cybersecurity.",
            "fr": "À mi-parcours : si vous n'êtes pas encore passé par ici, c'est le moment. La première édition de NextTech vous attend — cinq minutes, un café et vous êtes à jour sur l'IA et la cybersécurité.",
        }
    return {
        "es": "Mitad de mes: si aún no has pasado por aquí, este es el momento. La última edición de NextTech te espera — cinco minutos, un café y te pones al día con lo último en IA y ciberseguridad.",
        "en": "Mid-month: if you haven't stopped by yet, now's the time. The latest NextTech edition is waiting — five minutes, a coffee and you're up to speed on AI and cybersecurity.",
        "fr": "À mi-parcours : si vous n'êtes pas encore passé par ici, c'est le moment. La dernière édition de NextTech vous attend — cinq minutes, un café et vous êtes à jour sur l'IA et la cybersécurité.",
    }


def update_web_intro(edition: str) -> bool:
    """
    Actualiza el texto de bienvenida del index.html de la edición vigente
    en los 3 idiomas (inline ES + I18N.es / I18N.en / I18N.fr).
    Solo modifica el archivo — el workflow hace el git commit/push.
    """
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        edition, "index.html"
    )
    if not os.path.isfile(path):
        print(f"  ⚠️  {edition}/index.html no encontrado — intro web no actualizado.")
        return False

    texts = _intro_texts(edition)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Texto inline del div (siempre en ES — applyLang lo sobreescribe al cargar)
    html = re.sub(
        r'(data-i18n-html="intro">\n)\s+.+?(\n\s+</div>)',
        lambda m: f'{m.group(1)}    {texts["es"]}{m.group(2)}',
        html,
    )

    # 2. Las 3 entradas "intro" en I18N (orden: es → en → fr)
    count = [0]
    lang_order = ["es", "en", "fr"]

    def _replace(m):
        idx = min(count[0], 2)
        count[0] += 1
        return f'"intro": "{texts[lang_order[idx]]}"'

    html = re.sub(r'"intro":\s*"[^"]*"', _replace, html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✅ Intro web actualizado en {edition}/index.html (ES · EN · FR)")
    return True


# ── MAIN ──────────────────────────────────────────────────────────────────────

def send_reminder() -> bool:
    token  = get_access_token()
    opener = get_opener(EDITION_NUMBER)
    html   = build_html(opener)

    payload = {
        "message": {
            "subject": SUBJECT,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": [{"emailAddress": {"address": REMINDER_TO}}],
            "importance": "normal",
        },
        "saveToSentItems": "false",
    }

    url     = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    if response.status_code == 202:
        print(f"  ✅ Recordatorio enviado a: {REMINDER_TO}")
        print(f"  📧 Asunto: {SUBJECT}")
        print(f"  💬 Apertura: {opener}")
    else:
        print(f"  ❌ Error al enviar: {response.status_code} — {response.text}")
        return False

    # Actualizar intro web (el workflow hace el commit/push)
    update_web_intro(EDITION_NUMBER)
    return True


if __name__ == "__main__":
    send_reminder()
