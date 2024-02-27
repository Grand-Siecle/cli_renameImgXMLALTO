import os
import xml.etree.ElementTree as ET

# Fonction pour renommer un fichier image et mettre à jour le fichier XML
def renommer_et_mettre_a_jour(fichier_image, fichier_xml):
    # Extraire le nom du dossier parent
    parent_folder = os.path.basename(os.path.dirname(fichier_image))

    # Extraire le nom du fichier image sans l'extension
    nom_fichier_image = os.path.splitext(os.path.basename(fichier_image))[0]

    # Vérifier si le nom du fichier est plus long que 5 caractères
    if len(nom_fichier_image) > 5:
        return  # Ignorer les fichiers avec des noms trop longs

    # Nouveau nom de l'image (nomimg_nomfichier)
    nouveau_nom_image = f"{parent_folder}_{nom_fichier_image}"

    # Renommer le fichier image
    _, extension = os.path.splitext(fichier_image)
    nouveau_path_image = os.path.join(os.path.dirname(fichier_image), f"{nouveau_nom_image}{extension}")
    os.rename(fichier_image, nouveau_path_image)

    # Charger le fichier XML
    tree = ET.parse(fichier_xml)
    root = tree.getroot()

    # Trouver l'élément <fileName> dans la structure XML
    for fileName in root.findall('.//alto:fileName', namespaces={'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}):
        # Mettre à jour le contenu de l'élément <fileName>
        fileName.text = f"{nouveau_nom_image}{extension}"

    # Enregistrer les modifications dans le fichier XML
    tree.write(fichier_xml, encoding='utf-8', xml_declaration=True)

    # Renommer le fichier XML
    nouveau_nom_xml = f"{nouveau_nom_image}.xml"
    nouveau_path_xml = os.path.join(os.path.dirname(fichier_xml), nouveau_nom_xml)
    os.rename(fichier_xml, nouveau_path_xml)

# Répertoire courant
repertoire_courant = os.getcwd()

# Extensions d'images à prendre en compte
extensions_images = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico"]

# Parcours récursif des fichiers et dossiers à partir du répertoire courant
for dossier_parent, sous_dossiers, fichiers in os.walk(repertoire_courant):
    for fichier in fichiers:
        # Vérifier si le fichier est une image et a une correspondance XML
        for extension in extensions_images:
            if fichier.lower().endswith(extension):
                nom_fichier_sans_extension = os.path.splitext(fichier)[0]
                fichier_xml = os.path.join(dossier_parent, f"{nom_fichier_sans_extension}.xml")
                if os.path.exists(fichier_xml):
                    renommer_et_mettre_a_jour(os.path.join(dossier_parent, fichier), fichier_xml)

