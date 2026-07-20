"""
pubdate.py — NextTech
Única fuente de la fecha de publicación para todos los scripts.

El workflow (monthly.yml) calcula PUBLICATION_DATE = fecha de generación + 8 días
(el primer lunes del mes siguiente) y la exporta como variable de entorno.
Aquí solo se lee — el cálculo "+8 días" vive únicamente en monthly.yml.
Sin la variable (ejecución local), se usa la fecha de hoy.

Los meses van SIEMPRE en español desde MESES_ES: strftime("%B") depende del
locale y en el runner de GitHub (locale C) devuelve "June" en vez de "Junio".
"""

import os
from datetime import datetime

MESES_ES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def publication_date() -> datetime:
    """Fecha de publicación de la edición (PUBLICATION_DATE, formato YYYY-MM-DD)."""
    raw = os.environ.get("PUBLICATION_DATE", "").strip()
    if raw:
        return datetime.strptime(raw, "%Y-%m-%d")
    return datetime.now()


def mes_label(dt: datetime) -> str:
    """Etiqueta 'Mes Año' en español, p. ej. 'Agosto 2026'."""
    return f"{MESES_ES[dt.month]} {dt.year}"
