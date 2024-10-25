import zipfile
import os
from PIL import Image
import argparse
from rich.progress import Progress
import gc
from contextlib import contextmanager
import multiprocessing as mp
import tempfile
from PyPDF2 import PdfMerger
import re

def natural_sort_key(s):
    """
    Function to generate key for natural sorting of strings with numbers.
    This will ensure "_1_", "_2_", "_10_" are sorted correctly.
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

@contextmanager
def managed_image(image_path, mode='RGB'):
    """Context manager to ensure proper image cleanup."""
    img = Image.open(image_path)
    try:
        if img.mode != mode:
            img = img.convert(mode)
        yield img
    finally:
        img.close()
        gc.collect()

def process_single_image(args):
    """Process a single image for multiprocessing."""
    zip_path, filename, temp_dir, dpi = args
    output_path = os.path.join(temp_dir, f"{os.path.basename(filename)}.pdf")
    
    try:
        # Extract the image
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            temp_image_path = zip_ref.extract(filename, temp_dir)
        
        # Convert to PDF
        with managed_image(temp_image_path) as img:
            img.save(output_path, 'PDF', dpi=(dpi, dpi))
        
        # Clean up the temporary image file
        os.remove(temp_image_path)
        
        return (filename, output_path)  # Return tuple with original filename
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return None

def merge_pdfs(pdf_files, output_pdf):
    """Merge multiple PDFs into a single file using PyPDF2."""
    if not pdf_files:
        return
    
    merger = PdfMerger()
    
    try:
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                merger.append(pdf_file)
        
        merger.write(output_pdf)
    finally:
        merger.close()

def is_supported_image(filename):
    """Check if the file is a supported image format."""
    supported_formats = {'.tiff', '.tif', '.jpg', '.jpeg', '.png'}
    return os.path.splitext(filename.lower())[1] in supported_formats

def convert_images_to_pdf_parallel(zip_path, output_pdf, progress, dpi=600, num_processes=None):
    """Convert images to PDF using parallel processing."""
    if num_processes is None:
        num_processes = max(1, mp.cpu_count() - 1)  # Leave one CPU free
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of supported image files
            file_list = [f for f in zip_ref.namelist() if is_supported_image(f)]
            
            if not file_list:
                print("No supported image files found in the archive.")
                return
            
            # Sort file list using natural sort
            file_list.sort(key=natural_sort_key)
            
            # Prepare arguments for multiprocessing
            process_args = [(zip_path, filename, temp_dir, dpi) for filename in file_list]
            
            # Initialize progress bar
            with progress:
                task = progress.add_task("[green]Converting images to PDF...", total=len(file_list))
                
                # Process images in parallel and store results in a dictionary
                results_dict = {}
                with mp.Pool(num_processes) as pool:
                    for result in pool.imap_unordered(process_single_image, process_args):
                        if result:
                            orig_filename, pdf_path = result
                            results_dict[orig_filename] = pdf_path
                        progress.advance(task)
                
                # Create ordered list of PDF files based on original file list
                pdf_files = [results_dict[filename] for filename in file_list 
                           if filename in results_dict]
                
                # Merge PDFs
                merge_task = progress.add_task("[yellow]Merging PDFs...", total=1)
                merge_pdfs(pdf_files, output_pdf)
                progress.advance(merge_task)

def image_zip_to_pdf(zip_path, output_pdf, dpi=600, num_processes=None):
    """Main function to process ZIP to PDF with parallel processing."""
    try:
        with Progress() as progress:
            main_task = progress.add_task("[magenta]Processing ZIP to PDF...", total=1)
            convert_images_to_pdf_parallel(zip_path, output_pdf, progress, dpi, num_processes)
            progress.advance(main_task)
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Convert a ZIP file containing images (TIFF, JPG, PNG) to a PDF with parallel processing.")
    parser.add_argument('zipfile', type=str, help="Path to the input ZIP file.")
    parser.add_argument('output_pdf', type=str, help="Path to the output PDF file.")
    parser.add_argument('--dpi', type=int, default=600, help="Set the DPI (default: 600) for images in the PDF.")
    parser.add_argument('--processes', type=int, default=None, 
                       help="Number of processes to use (default: number of CPU cores minus 1)")
    
    args = parser.parse_args()
    
    image_zip_to_pdf(args.zipfile, args.output_pdf, args.dpi, args.processes)

if __name__ == "__main__":
    main()
