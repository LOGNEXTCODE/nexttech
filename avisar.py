"""
avisar.py — NextTech
Aviso breve por correo a REVIEWER_EMAIL vía Microsoft Graph (M365).
Uso desde los workflows: python avisar.py "Asunto" "Cuerpo en texto plano".
Reutiliza get_access_token() de mailer.py (mismos secrets MS_*).
"""

import os
import sys
import requests

from mailer import get_access_token, SENDER_EMAIL


def main():
    if len(sys.argv) < 3:
        print("Uso: python avisar.py \"Asunto\" \"Cuerpo\"")
        sys.exit(1)
    subject, body = sys.argv[1], sys.argv[2]
    to = [a.strip() for a in os.environ.get("REVIEWER_EMAIL", "").split(",") if a.strip()]
    if not to:
        print("Sin REVIEWER_EMAIL — no se envía aviso.")
        return

    token = get_access_token()
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": a}} for a in to],
            "importance": "high",
        },
        "saveToSentItems": "false",
    }
    r = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
    )
    r.raise_for_status()
    print(f"  ✅ Aviso enviado a {', '.join(to)}: {subject}")


if __name__ == "__main__":
    main()
