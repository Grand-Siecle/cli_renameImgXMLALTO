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

- Cas mélange entre XML océrisé et seulement segmentation
Check si attribut tous les attributs CONTENT sont vides, si c'est le cas enregistre dans listxml.txt
```python
import os
import xml.etree.ElementTree as ET

folder_path = 'content/data/doc_1/'

output_file = 'content/listxml.txt'

empty_content_files = []

for filename in os.listdir(folder_path):
    if filename.endswith('.xml'):
        file_path = os.path.join(folder_path, filename)

        tree = ET.parse(file_path)
        root = tree.getroot()

        string_elements = root.findall(".//{http://www.loc.gov/standards/alto/ns-v4#}String")

        # Vérifier si tous les éléments <String> ont l'attribut CONTENT vide
        if all(string.get('CONTENT') == "" for string in string_elements):
            empty_content_files.append(filename)

with open(output_file, 'w') as f:
    for file in empty_content_files:
        f.write(f"{file}\n")
```

Déplacer les fichiers vers images/  présents dans le txt
  ```bash
  xargs -I {} mv data/doc_1/{} images/ < listxml.txt
  ```

Supprimer les images n'ayant pas de fichiers xml associés (cas d'HTR non terminé).
```bash
for jpg in *.jpg; do [ ! -f "${jpg%.jpg}.xml" ] && rm "$jpg"; done
```

  
