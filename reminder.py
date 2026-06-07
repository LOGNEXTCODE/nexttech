"""
reminder.py — NextTech
Envía el recordatorio mensual de mitad de mes a sistemas@lognext.com.
Reutiliza get_access_token() de mailer.py (Microsoft Graph API / M365).
"""

import os
from datetime import datetime
import requests
from mailer import get_access_token


SENDER_EMAIL  = os.environ["MS_SENDER_EMAIL"]                           # sistemas@lognext.com
REMINDER_TO   = os.environ.get("REMINDER_EMAIL", "sistemas@lognext.com")

SUBJECT = "☕ ¿Aún no has leído NextTech? Tómate un respiro y ponte al día"

# Frase de apertura variable, rotada por mes (sensación de frescura).
# El resto del cuerpo es fijo.
_OPENERS = [
    "A mitad de mes, un recordatorio rápido: la última edición de NextTech sigue esperándote.",
    "Mitad de mes, buen momento para una pausa: la última edición de NextTech sigue esperándote.",
    "¿Semana intensa? La última edición de NextTech sigue esperándote.",
]


def get_opener() -> str:
    """Rota entre los 3 openers según el mes actual (enero=0, febrero=1 …)."""
    return _OPENERS[(datetime.now().month - 1) % len(_OPENERS)]


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


def send_reminder() -> bool:
    token  = get_access_token()
    opener = get_opener()
    html   = build_html(opener)

    payload = {
        "message": {
            "subject": SUBJECT,
            "body": {
                "contentType": "HTML",
                "content": html,
            },
            "toRecipients": [{"emailAddress": {"address": REMINDER_TO}}],
            "importance": "normal",
        },
        "saveToSentItems": "false",
    }

    url     = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    if response.status_code == 202:
        print(f"  ✅ Recordatorio enviado a: {REMINDER_TO}")
        print(f"  📧 Asunto: {SUBJECT}")
        print(f"  💬 Apertura usada: {opener}")
        return True

    print(f"  ❌ Error al enviar: {response.status_code} — {response.text}")
    return False


if __name__ == "__main__":
    send_reminder()
