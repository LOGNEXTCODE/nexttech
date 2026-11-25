# NextStep · Mejora continua

Sección fija de NextTech y **siempre la primera** de la edición. Cuenta lo que IT ha
mejorado ese mes (seguridad, herramientas, procesos), en «tú» y sin jerga.

**El texto lo escribe IT a mano. `generator.py` nunca lo redacta.**

## Cómo se publica

1. Antes de la generación (miércoles 14 días antes del primer miércoles), crea
   `nextstep/NN.json`, donde `NN` es el número de la edición (`08.json` para la #08):

   ```json
   {
     "titulo": "Hemos reforzado la protección de tu equipo",
     "texto": "<p>Primer párrafo.</p><p>Segundo párrafo.</p>"
   }
   ```

   - `texto` admite solo `<p>`.
   - Explica cada sigla la primera vez que aparezca, por ejemplo «un EDR (protección
     avanzada que detecta y responde a ataques en el equipo)».
   - Sin rayas «—» y con comillas curvas.

2. La traducción a EN y FR la hace `translator.py`, como en el resto de la edición.

## Si un mes no hay texto

Si falta `nextstep/NN.json`, o tiene `titulo` o `texto` vacíos, la sección **no se muestra**.
El correo de borrador lo avisa en «Avisos para la revisión».

Si el texto llega después de generar, se añade a mano en `NN/index.html`:

- copia el bloque `NEXTSTEP:INICIO` … `NEXTSTEP:FIN` de `web_template.html` antes de IA al día;
- rellena el titular y el texto;
- añade las claves `mejora-title` y `mejora-text` en ES, EN y FR. Las claves `tag-mejora` y
  `mejora-note` también hacen falta: cópialas de `07/index.html`.

La foto de cabecera y la nota al pie («Nosotros ponemos las herramientas; tú, el ojo
crítico…») son fijas y están en la plantilla.
