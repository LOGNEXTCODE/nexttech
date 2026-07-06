"""
gen_editions.py — genera /editions.json (manifiesto de ediciones publicadas)
para el navegador de ediciones del footer (editions-nav.js).

Lista las carpetas NN/ existentes, PRESERVA las etiquetas (mes/año) ya presentes
en un editions.json anterior y, para una edición nueva sin etiqueta, usa el mes
del build como mejor esfuerzo. Idempotente: mismo repo → misma salida.
"""
import os
import re
import json
import datetime

MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def main():
    prev = {}
    if os.path.exists("editions.json"):
        try:
            for e in json.load(open("editions.json", encoding="utf-8")):
                prev[str(e.get("n"))] = e
        except Exception:
            pass

    eds = sorted(d for d in os.listdir(".")
                 if re.fullmatch(r"\d{2}", d) and os.path.isdir(d))

    today = datetime.date.today()
    out = []
    for d in eds:
        label = (prev.get(d) or {}).get("label")
        if not label:
            label = "%s %d" % (MESES[today.month], today.year)
        out.append({"n": d, "url": "/%s/" % d, "label": label})

    with open("editions.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    main()
