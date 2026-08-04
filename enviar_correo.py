"""
enviar_correo.py — NextTech
Envía un archivo HTML como correo a REVIEWER_EMAIL (SOLO al revisor; el
reenvío a la organización es siempre manual de Miguel). El asunto se toma
del <title> del HTML. Reutiliza get_access_token() de mailer.py.

Uso: python enviar_correo.py correo/anuncio-03.html
"""

import io
import os
import re
import sys
import requests

from mailer import get_access_token, SENDER_EMAIL


def main():
    if len(sys.argv) < 2:
        print("Uso: python enviar_correo.py <ruta.html>")
        sys.exit(1)
    path = sys.argv[1]
    html = io.open(path, encoding="utf-8").read()
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    if not m:
        print(f"::error::{path} no tiene <title> (se usa como asunto)")
        sys.exit(1)
    subject = re.sub(r"\s+", " ", m.group(1)).strip()

    to = [a.strip() for a in os.environ.get("REVIEWER_EMAIL", "").split(",") if a.strip()]
    if not to:
        print("::error::REVIEWER_EMAIL vacío — no se envía nada")
        sys.exit(1)

    token = get_access_token()
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": [{"emailAddress": {"address": a}} for a in to],
            "importance": "normal",
        },
        "saveToSentItems": "false",
    }
    r = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
    )
    r.raise_for_status()
    print(f"  ✅ Correo enviado a {', '.join(to)}")
    print(f"  📧 Asunto: {subject}")
    print(f"  ↪️  Recuerda: el reenvío a la organización es manual desde Outlook.")


if __name__ == "__main__":
    main()
