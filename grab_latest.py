#!/usr/bin/env python3

import os
import shutil
import argparse
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib

def parse_pom(pom_file):
    tree = ET.parse(pom_file)
    root = tree.getroot()

    # Define the namespace mapping based on the POM's schema location
    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}

    # Extract groupId, artifactId, and version
    group_id = root.find('mvn:groupId', ns).text
    artifact_id = root.find('mvn:artifactId', ns).text
    version = root.find('mvn:version', ns).text

    return group_id, artifact_id, version

def create_metadata_xml(target_dir, group_id, artifact_id, version):
    metadata_file = os.path.join(target_dir, 'maven-metadata.xml')
    
    # Create XML structure
    metadata = ET.Element('metadata')
    ET.SubElement(metadata, 'groupId').text = group_id
    ET.SubElement(metadata, 'artifactId').text = artifact_id
    
    versioning = ET.SubElement(metadata, 'versioning')
    ET.SubElement(versioning, 'latest').text = version
    ET.SubElement(versioning, 'release').text = version
    versions = ET.SubElement(versioning, 'versions')
    ET.SubElement(versions, 'version').text = version
    ET.SubElement(versioning, 'lastUpdated').text = datetime.now().strftime('%Y%m%d')
    
    # Write XML to file
    tree = ET.ElementTree(metadata)
    with open(metadata_file, 'wb') as file:
        tree.write(file)
    
    print(f"Created {metadata_file}")

    # Generate MD5 checksum
    generate_md5_checksum(metadata_file)

def generate_md5_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    checksum_file = f"{file_path}.sha1"
    with open(checksum_file, 'w') as f:
        f.write(hash_md5.hexdigest())
    
    print(f"Created {checksum_file}")

def copy_files(project_dir, registry_dir):
    # Parse the POM file to get groupId, artifactId, and version
    pom_file = os.path.join(project_dir, 'pom.xml')
    if not os.path.exists(pom_file):
        print(f"Error: {pom_file} does not exist.")
        return
    
    group_id, artifact_id, version = parse_pom(pom_file)
    
    # Create the target directory structure: /groupId/artifactId/version
    target_dir = os.path.join(registry_dir, group_id.replace('.', '/'), artifact_id, version)
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy JAR files
    jar_files = glob.glob(os.path.join(project_dir, 'target', '*.jar'))
    for jar_file in jar_files:
        destination = os.path.join(target_dir, os.path.basename(jar_file))
        if os.path.exists(destination):
            os.remove(destination)

        shutil.copy(jar_file, destination)
        print(f"Copied {jar_file} to {destination}")

    # Copy POM file
    destination_pom = os.path.join(target_dir, f'{artifact_id}-{version}.xml')
    if os.path.exists(destination_pom):
        os.remove(destination_pom)
    shutil.copy(pom_file, destination_pom)
    print(f"Copied {pom_file} to {destination_pom}")

    # Create maven-metadata.xml
    create_metadata_xml(target_dir, group_id, artifact_id, version)

def main():
    parser = argparse.ArgumentParser(description='Copy JAR and POM files to registry directory.')
    parser.add_argument('-pd', '--project-dir', required=True, help='Path to the project directory')
    parser.add_argument('-rd', '--registry-dir', required=True, help='Path to the registry directory')
    
    args = parser.parse_args()
    
    copy_files(args.project_dir, args.registry_dir)

if __name__ == '__main__':
    main()
