"""
translator.py — NextTech
Lee un index.html ya instrumentado con data-i18n/data-i18n-html,
extrae los textos en español, llama a Claude una vez por idioma (EN, FR)
e inyecta las traducciones en el objeto I18N del mismo HTML.

Uso:
    python translator.py [ruta/al/index.html]   # default: 01/index.html
"""

import json
import re
import sys
from pathlib import Path

import anthropic
from bs4 import BeautifulSoup

MODEL = "claude-sonnet-4-6"


# ─── EXTRACCIÓN ────────────────────────────────────────────────────────────────

def extract_strings(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    strings: dict[str, str] = {}

    for el in soup.find_all(attrs={"data-i18n": True}):
        key = el["data-i18n"]
        strings[key] = el.get_text(strip=True)

    for el in soup.find_all(attrs={"data-i18n-html": True}):
        key = el["data-i18n-html"]
        strings[key] = el.decode_contents().strip()

    return strings


# ─── TRADUCCIÓN ────────────────────────────────────────────────────────────────

def translate(client: anthropic.Anthropic, strings: dict[str, str], lang: str) -> dict[str, str]:
    lang_name = {"en": "English", "fr": "French"}[lang]

    prompt = f"""You are a professional translator specializing in corporate IT security documentation for LOGNEXT, a Spanish company.

Translate each JSON value from Spanish to {lang_name}.

Rules:
- Preserve ALL HTML tags exactly as-is (do not add, remove, or alter any tag).
- Keep brand/product names unchanged: LOGNEXT, Microsoft 365, Outlook, Word, Excel, Teams, Microsoft Purview, Google, Cisco, INCIBE, etc.
- Keep classification label names unchanged (they are Microsoft Purview system literals in Spanish): Público, Interno, Confidencial, Muy Confidencial.
- Keep URLs, email addresses, phone numbers, and example data (DNI, IBAN, etc.) unchanged.
- For date strings like "Junio 2026" translate only the month name.
- Use professional yet approachable tone appropriate for internal corporate IT communication.
- Return ONLY valid JSON — no markdown, no code fences, no explanation.

Input JSON:
{json.dumps(strings, ensure_ascii=False, indent=2)}"""

    msg = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    return json.loads(raw)


# ─── INYECCIÓN ─────────────────────────────────────────────────────────────────

def inject_i18n(html: str, translations: dict) -> str:
    marker = "const I18N ="
    start = html.find(marker)
    if start == -1:
        raise ValueError("No se encontró 'const I18N =' en el HTML.")

    brace_open = html.index("{", start)
    depth = 0
    i = brace_open
    while i < len(html):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1

    end = i + 1
    if html[end : end + 1] == ";":
        end += 1

    replacement = "const I18N = " + json.dumps(translations, ensure_ascii=False, indent=2) + ";"
    return html[:start] + replacement + html[end:]


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> None:
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("01/index.html")

    if not html_path.exists():
        print(f"Error: {html_path} no existe.", file=sys.stderr)
        sys.exit(1)

    html = html_path.read_text(encoding="utf-8")

    print(f"Extrayendo textos de {html_path}...")
    es_strings = extract_strings(html)
    print(f"  {len(es_strings)} claves encontradas.")

    translations: dict[str, dict[str, str]] = {
        "es": es_strings,
        "en": {},
        "fr": {},
    }

    client = anthropic.Anthropic()

    for lang in ("en", "fr"):
        lang_name = {"en": "English", "fr": "French"}[lang]
        print(f"Traduciendo a {lang_name}...")
        translations[lang] = translate(client, es_strings, lang)
        print(f"  {len(translations[lang])} strings traducidos.")

    print("Inyectando en el HTML...")
    new_html = inject_i18n(html, translations)
    html_path.write_text(new_html, encoding="utf-8")
    print(f"Guardado: {html_path}")


if __name__ == "__main__":
    main()
