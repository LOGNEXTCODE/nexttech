"""
gen_editions.py — genera /editions.json (manifiesto de ediciones publicadas)
para el navegador de ediciones del footer (editions-nav.js).

Lista las carpetas NN/ existentes, PRESERVA las etiquetas (mes/año) ya presentes
en un editions.json anterior y, para una edición nueva sin etiqueta, usa el mes
de PUBLICACIÓN (PUBLICATION_DATE vía pubdate.py — la edición se genera 14 días
antes, en el mes anterior). Idempotente: mismo repo → misma salida.

Con PUBLISHED_MAX=NN en el entorno, solo lista ediciones ≤ NN: las generadas
pero aún no publicadas NO aparecen en el manifiesto (ni, por tanto, en el
navegador público de ediciones). Sin la variable, lista todas (comportamiento
histórico). Lo fija portada.yml al publicar.
"""
import os
import re
import json

from pubdate import publication_date, MESES_ES

def main():
    prev = {}
    if os.path.exists("editions.json"):
        try:
            for e in json.load(open("editions.json", encoding="utf-8")):
                prev[str(e.get("n"))] = e
        except Exception:
            pass

    cap = os.environ.get("PUBLISHED_MAX", "").strip()
    eds = sorted(d for d in os.listdir(".")
                 if re.fullmatch(r"\d{2}", d) and os.path.isdir(d)
                 and (not cap or d <= cap))

    pub = publication_date()
    out = []
    for d in eds:
        label = (prev.get(d) or {}).get("label")
        if not label:
            label = "%s %d" % (MESES_ES[pub.month], pub.year)
        out.append({"n": d, "url": "/%s/" % d, "label": label})

    with open("editions.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    main()
