import zipfile
import os
from PIL import Image
import argparse
from rich.progress import Progress

def extract_zip(zip_path, extract_to, progress):
    """Extract zip file to a specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        total_files = len(file_list)
        
        # Track extraction progress
        with progress:
            task = progress.add_task("[cyan]Extracting files...", total=total_files)
            for file in file_list:
                zip_ref.extract(file, extract_to)
                progress.advance(task)

def convert_images_to_pdf(image_files, output_pdf, progress, dpi=600):
    """Convert a list of image files to a single PDF, limiting resolution to 600 DPI."""
    images = []
    with progress:
        task = progress.add_task("[green]Converting images to PDF...", total=len(image_files))
        for image_file in image_files:
            img = Image.open(image_file)
            img = img.convert("RGB")  # Ensure the image is RGB
            img.info['dpi'] = (dpi, dpi)
            images.append(img)
            progress.advance(task)
            
    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:], dpi=(dpi, dpi))


def image_zip_to_pdf(zip_path, extract_dir, output_pdf, dpi=600):
    """Main function to extract images from a zip and convert them to PDF."""
    os.makedirs(extract_dir, exist_ok=True)
    
    with Progress() as progress:
        main_task = progress.add_task("[magenta]Processing ZIP to PDF...", total=2)

        extract_zip(zip_path, extract_dir, progress)
        progress.advance(main_task)

        supported_formats = ['.tiff', '.tif', '.jpg', '.jpeg', '.png']
        image_files = [os.path.join(extract_dir, f) for f in os.listdir(extract_dir) if os.path.splitext(f.lower())[1] in supported_formats]

        if not image_files:
            print("No supported image files found in the archive.")
            return

        convert_images_to_pdf(image_files, output_pdf, progress, dpi)
        progress.advance(main_task)

    for file in image_files:
        os.remove(file)
    os.rmdir(extract_dir)

def main():
    parser = argparse.ArgumentParser(description="Convert a ZIP file containing images (TIFF, JPG, PNG) to a PDF with limited DPI.")
    parser.add_argument('zipfile', type=str, help="Path to the input ZIP file.")
    parser.add_argument('output_pdf', type=str, help="Path to the output PDF file.")
    parser.add_argument('-d', '--dir', type=str, default="temp_images", help="Temporary directory for extraction (default: temp_images).")
    parser.add_argument('--dpi', type=int, default=600, help="Set the DPI (default: 600) for images in the PDF.")
    args = parser.parse_args()
    image_zip_to_pdf(args.zipfile, args.dir, args.output_pdf, args.dpi)

if __name__ == "__main__":
    main()