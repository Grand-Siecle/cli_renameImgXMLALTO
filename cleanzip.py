import zipfile
import xml.etree.ElementTree as ET
import os
import click
import tempfile
import shutil
from rich.progress import Progress
from rich.console import Console
from rich.logging import RichHandler
import logging

console = Console()
logging.basicConfig(
    level=logging.ERROR,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, show_path=False)]
)
logger = logging.getLogger("rich")

@click.command()
@click.argument("zip_path", type=click.Path(exists=True))
def clean_filenames_in_zip(zip_path):
    """
    Nettoie les noms de fichier dans les XML d'un zip, en supprimant le dossier pour ne garder que le nom du fichier,
    puis compresse à nouveau le zip en place.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        with zipfile.ZipFile(zip_path, 'r') as zip_in:
            zip_in.extractall(tempdir)

            xml_files = [f for f in zip_in.namelist() if f.endswith('.xml')]

            with Progress(console=console) as progress:
                task = progress.add_task("Nettoyage des fichiers XML...", total=len(xml_files))

                for file_name in xml_files:
                    file_path = os.path.join(tempdir, file_name)
                    try:
                        clean_filename(file_path)
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement de {file_name}: {e}")
                    finally:
                        progress.update(task, advance=1)

        temp_zip_path = f"{zip_path}.tmp"
        with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_out:
            for root, _, files in os.walk(tempdir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, tempdir)
                    zip_out.write(full_path, arcname)

        shutil.move(temp_zip_path, zip_path)
    
    console.print("[bold green]Le nettoyage et la compression sont terminés. Le fichier zip a été modifié en place.[/bold green]")

def clean_filename(file_path):
    """Nettoie le champ <fileName> dans un fichier XML donné pour ne garder que le nom du fichier."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespace = "http://www.loc.gov/standards/alto/ns-v4#"
    xsi_namespace = "http://www.w3.org/2001/XMLSchema-instance"
    ns_map = {"alto": namespace}
    
    # Identifier et nettoyer l'élément <fileName>
    filename_element = root.find(".//alto:sourceImageInformation/alto:fileName", ns_map)
    if filename_element is not None:
        filename_element.text = os.path.basename(filename_element.text)
    else:
        raise ValueError("Élément <fileName> non trouvé.")

    ET.register_namespace('', namespace)
    ET.register_namespace('xsi', xsi_namespace)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    clean_filenames_in_zip()
