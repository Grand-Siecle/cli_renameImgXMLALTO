# Bash

- Supprimer les images n'ayant pas de fichiers xml associés
```bash
for jpg in *.jpg; do [ ! -f "${jpg%.jpg}.xml" ] && rm "$jpg"; done
```
