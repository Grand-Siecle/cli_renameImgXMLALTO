# Bash

- Supprimer les images n'ayant pas de fichiers xml associés (cas d'HTR non terminé).
```bash
for jpg in *.jpg; do [ ! -f "${jpg%.jpg}.xml" ] && rm "$jpg"; done
```

- Créer un dossier puis déplacer toutes les fichiers ayant une image et un xml associé pour les déplacer. (cas yolo non terminé)
```bash
mkdir -p ../data/doc_1 && for jpg in *.jpg; do xml="${jpg%.jpg}.xml"; [ -f "$xml" ] && mv "$jpg" "$xml" ../data/doc_1/; done
```
Ensuite pour ramener dans le bon dossier 
```bash
mv ../data/doc_1/* .
```
