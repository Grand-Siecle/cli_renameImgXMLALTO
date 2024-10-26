import os
import json
import requests
from unidecode import unidecode
import cases  # Ensure this library (e.g., 'stringcase') is installed or implemented
import argparse

# Define the clean_kebab transformation function
def clean_kebab(string: str, max_length: int = 100) -> str:
    kebab_string = cases.to_kebab(unidecode(string))
    # Truncate if longer than max_length
    if len(kebab_string) > max_length:
        kebab_string = kebab_string[:max_length].rsplit('-', 1)[0]  # Avoid cutting off mid-word
    return kebab_string

# Fetch IIIF manifest and get the label
def fetch_label_from_manifest(manifest_url):
    response = requests.get(manifest_url)
    response.raise_for_status()
    manifest_data = response.json()
    
    # Extract label (assuming IIIF v3 format)
    label = manifest_data.get("label", {})
    if isinstance(label, dict):  # Handle multilingual labels
        label = label.get("en", [None])[0]  # Use 'en' if available, else take the first available language label
    if not label:
        raise ValueError("Label not found in manifest")
    
    return label

# Main function to process URLs from JSON file
def process_manifests(json_file, log_file):
    with open(json_file, 'r') as file:
        manifests = json.load(file)
    
    with open(log_file, 'w') as log:
        for url, name_prefix in manifests.items():
            try:
                # Fetch and transform label
                label = fetch_label_from_manifest(url)
                kebab_label = clean_kebab(label)
                
                # Create directory with name_prefix and kebab label
                dir_name = f"{kebab_label}"
                
                # Create directory if it doesn't exist
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                    print(f"Directory created: {dir_name}")
                else:
                    print(f"Directory already exists: {dir_name}")

                # Write to log file
                log.write(f"{name_prefix} -> {dir_name}/\n")
            
            except requests.exceptions.RequestException as e:
                print(f"Error fetching manifest for {url}: {e}")
            except ValueError as e:
                print(e)

# CLI setup
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch IIIF manifests and create directories with transformed label names.")
    parser.add_argument("json_file", help="Path to the JSON file containing IIIF manifest URLs and directory name prefixes")
    parser.add_argument("log_file", help="Path to the log file where directory names will be recorded")
    args = parser.parse_args()
    
    process_manifests(args.json_file, args.log_file)